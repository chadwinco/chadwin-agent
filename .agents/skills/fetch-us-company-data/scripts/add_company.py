#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

import sys


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


BASE_DIR = _default_base_dir()
QUEUE_SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "scripts"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(QUEUE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(QUEUE_SCRIPTS))

from edgar_fetch import fetch_company_filings, fetch_company_financials  # noqa: E402
from forecast_fetch import fetch_analyst_forecasts  # noqa: E402
from loaders import load_company_data  # noqa: E402
from metrics import compute_metrics  # noqa: E402
from transcript_fetch import fetch_latest_transcript_with_report  # noqa: E402
from company_idea_queue import TASK_FETCH_US, pick_next_company  # noqa: E402
from company_idea_queue_core import (  # noqa: E402
    load_user_preferences,
    market_is_allowed,
    resolve_preferences_path,
)


COUNTRY_DIR = "US"


def _ensure_dirs(base_dir: Path, ticker: str) -> Path:
    company_dir = base_dir / "companies" / COUNTRY_DIR / ticker
    (company_dir / "data").mkdir(parents=True, exist_ok=True)
    (company_dir / "data" / "filings").mkdir(parents=True, exist_ok=True)
    (company_dir / "data" / "financial_statements").mkdir(parents=True, exist_ok=True)
    (company_dir / "reports").mkdir(parents=True, exist_ok=True)
    return company_dir


def _valuation_inputs_path(company_dir: Path, asof: str) -> Path:
    path = company_dir / "reports" / asof / "valuation" / "inputs.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _transcript_report_path(data_dir: Path, asof: str) -> Path:
    filings_dir = data_dir / "filings"
    filings_dir.mkdir(parents=True, exist_ok=True)
    return filings_dir / f"earnings-call-fetch-report-{asof}.json"


def _summarize_failures(statuses: list[str]) -> str:
    if not statuses:
        return ""
    counts = Counter(statuses)
    parts = [f"{status}={count}" for status, count in counts.most_common()]
    return ", ".join(parts)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _analyst_revenue_growth(metrics: dict, analyst_estimates):
    if analyst_estimates is None or getattr(analyst_estimates, "empty", True):
        return None
    try:
        import pandas as pd  # type: ignore
    except ImportError:
        return None

    df = analyst_estimates.copy()
    df.columns = [str(c).strip() for c in df.columns]

    if "metric" in df.columns:
        df = df[df["metric"].astype(str).str.contains("revenue", case=False, na=False)]
    if df.empty:
        return None

    year_col = None
    for candidate in ("fiscalYear", "year", "fiscal_year"):
        if candidate in df.columns:
            year_col = candidate
            break
    if not year_col:
        return None

    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[year_col])
    if df.empty:
        return None
    df[year_col] = df[year_col].astype(int)

    for col in ("high", "avg", "low"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    latest_year = int(metrics.get("latest_year") or 0)
    df = df[df[year_col] > latest_year]
    if df.empty:
        return None

    df = df.sort_values(year_col)
    last = df.iloc[-1]
    years_forward = int(last[year_col]) - latest_year
    if years_forward <= 0:
        return None

    latest_revenue = float(metrics.get("latest_revenue") or 0)
    if latest_revenue <= 0:
        return None

    def _cagr(value):
        if value is None or value != value or value <= 0:
            return None
        return (float(value) / latest_revenue) ** (1 / years_forward) - 1

    return {
        "avg": _cagr(last.get("avg")),
        "high": _cagr(last.get("high")),
        "low": _cagr(last.get("low")),
        "forecast_year": int(last[year_col]),
        "years_forward": years_forward,
    }


def _coalesce(*values):
    for value in values:
        if value is None:
            continue
        if value != value:
            continue
        return float(value)
    return None


def _build_assumptions(metrics: dict, analyst_estimates=None) -> dict:
    base_growth = _clamp(metrics.get("avg_revenue_growth", 0.02), -0.02, 0.08)
    base_margin = _clamp(metrics.get("avg_fcf_margin", 0.05), 0.02, 0.15)

    notes = "Auto-generated from recent financial averages. Review and adjust before making decisions."

    analyst_growth = _analyst_revenue_growth(metrics, analyst_estimates)
    if analyst_growth:
        avg_growth = _coalesce(analyst_growth.get("avg"))
        high_growth = _coalesce(analyst_growth.get("high"))
        low_growth = _coalesce(analyst_growth.get("low"))

        candidate_base = avg_growth
        if candidate_base is None and high_growth is not None and low_growth is not None:
            candidate_base = (high_growth + low_growth) / 2
        if candidate_base is None:
            candidate_base = _coalesce(high_growth, low_growth)

        if candidate_base is not None:
            base_growth = candidate_base
        notes = (
            "Auto-generated using analyst revenue forecasts (StockAnalysis) "
            f"for FY{analyst_growth['forecast_year']} "
            f"(CAGR from FY{metrics.get('latest_year')} over {analyst_growth['years_forward']} years) "
            "and recent financial averages. "
            "Review and adjust before making decisions."
        )

    bull_growth = high_growth if analyst_growth else None
    bear_growth = low_growth if analyst_growth else None

    if bull_growth is None:
        bull_growth = base_growth + 0.02
    if bear_growth is None:
        bear_growth = base_growth - 0.02

    bull_growth = _clamp(bull_growth, -0.01, 0.12)
    bear_growth = _clamp(bear_growth, -0.05, 0.06)
    base_growth = _clamp(base_growth, -0.02, 0.08)

    bull_margin = _clamp(base_margin + 0.02, 0.03, 0.18)
    bear_margin = _clamp(base_margin - 0.02, 0.01, 0.12)

    return {
        "forecast_years": 5,
        "notes": notes,
        "scenarios": {
            "base": {
                "revenue_growth": float(base_growth),
                "fcf_margin": float(base_margin),
                "discount_rate": 0.10,
                "terminal_growth": 0.02,
            },
            "bull": {
                "revenue_growth": float(bull_growth),
                "fcf_margin": float(bull_margin),
                "discount_rate": 0.09,
                "terminal_growth": 0.025,
            },
            "bear": {
                "revenue_growth": float(bear_growth),
                "fcf_margin": float(bear_margin),
                "discount_rate": 0.11,
                "terminal_growth": 0.015,
            },
        },
    }


def _write_assumptions(path: Path, assumptions: dict, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    import yaml  # type: ignore

    path.write_text(yaml.safe_dump(assumptions, sort_keys=False))


def _company_name_from_profile(data_dir: Path) -> str | None:
    profile_path = data_dir / "company_profile.csv"
    if not profile_path.exists():
        return None
    try:
        with profile_path.open("r", newline="") as fp:
            reader = csv.DictReader(fp)
            row = next(reader, None)
    except Exception:
        return None
    if not row:
        return None
    name = str(row.get("companyName") or "").strip()
    return name or None


def _load_analyst_estimates(data_dir: Path):
    path = data_dir / "analyst_estimates.csv"
    if not path.exists():
        return None
    try:
        import pandas as pd  # type: ignore
    except ImportError:
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or refresh a company data package and bootstrap valuation assumptions"
    )
    parser.add_argument(
        "--ticker",
        help="US ticker symbol. If omitted, pick the next US company from the ideas log.",
    )
    parser.add_argument("--identity", help="EDGAR identity string: 'Name email@domain.com'")
    parser.add_argument("--base-dir", default=str(BASE_DIR))
    parser.add_argument("--asof", default=str(date.today()))
    parser.add_argument(
        "--ideas-log",
        help="Override ideas log path (default: idea-screens/company-ideas-log.jsonl).",
    )
    parser.add_argument("--overwrite-assumptions", action="store_true")
    parser.add_argument(
        "--transcript-url",
        help="Fetch transcript from this specific URL instead of running search discovery",
    )
    parser.add_argument(
        "--transcript-max-results",
        type=int,
        default=20,
        help="Maximum DuckDuckGo results to scan for transcript candidates",
    )
    parser.add_argument(
        "--transcript-min-body-chars",
        type=int,
        default=1000,
        help="Minimum extracted body length required to accept a transcript",
    )
    parser.add_argument(
        "--preferences-path",
        help="Override preferences path (default: preferences/user_preferences.json).",
    )
    parser.add_argument(
        "--ignore-preferences",
        action="store_true",
        help="Ignore preference-based queue filtering and market guardrails.",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir)
    ticker = (args.ticker or "").strip().upper()
    preferences_applied = not args.ignore_preferences
    resolved_preferences_path = resolve_preferences_path(
        base_dir=base_dir,
        preferences_path=args.preferences_path,
    )
    preferences = (
        load_user_preferences(base_dir=base_dir, preferences_path=args.preferences_path)
        if preferences_applied
        else {}
    )
    if preferences_applied and not market_is_allowed("us", preferences):
        raise SystemExit(
            "Preferences currently exclude US market. "
            f"Update {resolved_preferences_path} or rerun with --ignore-preferences."
        )

    if not ticker:
        selected = pick_next_company(
            base_dir=base_dir,
            task=TASK_FETCH_US,
            ideas_log=args.ideas_log,
            preferences_path=args.preferences_path,
            respect_preferences=preferences_applied,
        )
        if not selected:
            raise SystemExit(
                "No US company found in idea-screens/company-ideas-log.jsonl. "
                "Run fetch-us-investment-ideas first, relax preferences, or pass --ticker."
            )
        ticker = str(selected["ticker"]).upper()
        queued_at = selected.get("queued_at_utc") or "unknown"
        print(f"No --ticker provided. Selected {ticker} from ideas log (queued_at_utc={queued_at}).")

    company_dir = _ensure_dirs(base_dir, ticker)
    data_dir = company_dir / "data"

    print(f"Fetching filings for {ticker}...")
    fetch_company_filings(ticker, data_dir, identity=args.identity)

    print(f"Fetching financial statements for {ticker}...")
    fetch_company_financials(ticker, data_dir, identity=args.identity)

    print(f"Fetching analyst revenue forecasts for {ticker}...")
    forecast = fetch_analyst_forecasts(ticker, data_dir)
    if forecast:
        print(f"Saved analyst forecasts to {forecast.path}")
    else:
        print("No analyst revenue forecast found.")

    data = None
    metrics = {}
    analyst_estimates = None
    company_name = _company_name_from_profile(data_dir)
    try:
        data = load_company_data(base_dir, ticker)
        metrics = compute_metrics(data)
        analyst_estimates = data.analyst_estimates
        if not data.profile.empty and "companyName" in data.profile.columns:
            company_name = str(data.profile.iloc[0].get("companyName"))
    except Exception as exc:
        print(
            "Warning: unable to load normalized financial statements for "
            f"{ticker}; using conservative default valuation assumptions. ({exc})"
        )
        analyst_estimates = _load_analyst_estimates(data_dir)

    print(f"Fetching latest earnings call transcript for {ticker}...")
    report = fetch_latest_transcript_with_report(
        ticker=ticker,
        data_dir=data_dir,
        company_name=company_name,
        asof=args.asof,
        transcript_url=args.transcript_url,
        max_results=args.transcript_max_results,
        min_body_chars=args.transcript_min_body_chars,
    )
    report_path = _transcript_report_path(data_dir, args.asof)
    report_path.write_text(json.dumps(report.to_dict(), indent=2))
    transcript = report.transcript
    try:
        report_rel = report_path.relative_to(base_dir)
    except ValueError:
        report_rel = report_path
    print(f"Wrote transcript fetch report to {report_rel}")

    if transcript:
        try:
            transcript_rel = transcript.path.relative_to(base_dir)
        except ValueError:
            transcript_rel = transcript.path
        print(f"Saved transcript to {transcript_rel} ({transcript.source_url})")
    else:
        failed = [attempt.status for attempt in report.attempts if attempt.status != "success"]
        if failed:
            print(f"Transcript fetch failures: {_summarize_failures(failed)}")
        print("No earnings call transcript found.")

    assumptions_path = _valuation_inputs_path(company_dir, args.asof)
    assumptions = _build_assumptions(metrics, analyst_estimates)
    _write_assumptions(assumptions_path, assumptions, overwrite=args.overwrite_assumptions)


if __name__ == "__main__":
    main()
