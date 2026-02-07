#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import sys


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / "research").exists():
            return parent
    return Path.cwd()


BASE_DIR = _default_base_dir()

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fetch_company_data.edgar_fetch import fetch_company_filings, fetch_company_financials  # noqa: E402
from fetch_company_data.forecast_fetch import fetch_analyst_forecasts  # noqa: E402
from fetch_company_data.loaders import load_company_data  # noqa: E402
from fetch_company_data.metrics import compute_metrics  # noqa: E402
from fetch_company_data.transcript_fetch import fetch_latest_transcript  # noqa: E402
from scripts.run_company import run_company  # noqa: E402


def _ensure_dirs(base_dir: Path, ticker: str) -> Path:
    company_dir = base_dir / "companies" / ticker
    (company_dir / "data").mkdir(parents=True, exist_ok=True)
    (company_dir / "data" / "filings").mkdir(parents=True, exist_ok=True)
    (company_dir / "data" / "financial_statements").mkdir(parents=True, exist_ok=True)
    (company_dir / "reports").mkdir(parents=True, exist_ok=True)
    return company_dir


def _valuation_inputs_path(company_dir: Path, asof: str) -> Path:
    path = company_dir / "reports" / asof / "valuation" / "inputs.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


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


def _append_source_log(base_dir: Path, ticker: str, asof_date: str, source: str, notes: str) -> None:
    log_path = base_dir / "docs" / "source-log.md"
    if not log_path.exists():
        return
    entry = f"| {asof_date} | {ticker} | Earnings Call Transcript | {source} | {notes} |\n"
    content = log_path.read_text()
    if entry in content:
        return
    with log_path.open("a") as f:
        f.write(entry)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new company, fetch EDGAR data, and run analysis")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--identity", help="EDGAR identity string: 'Name email@domain.com'")
    parser.add_argument("--base-dir", default=str(BASE_DIR))
    parser.add_argument("--asof", default=str(date.today()))
    parser.add_argument("--skip-analysis", action="store_true")
    parser.add_argument("--overwrite-assumptions", action="store_true")

    args = parser.parse_args()
    base_dir = Path(args.base_dir)
    ticker = args.ticker.upper()

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

    data = load_company_data(base_dir, ticker)
    metrics = compute_metrics(data)

    company_name = None
    if not data.profile.empty and "companyName" in data.profile.columns:
        company_name = str(data.profile.iloc[0].get("companyName"))

    print(f"Fetching latest earnings call transcript for {ticker}...")
    transcript = fetch_latest_transcript(ticker, data_dir, company_name=company_name, asof=args.asof)
    if transcript:
        try:
            transcript_rel = transcript.path.relative_to(base_dir)
        except ValueError:
            transcript_rel = transcript.path
        _append_source_log(
            base_dir,
            ticker,
            args.asof,
            transcript.source_url,
            f"Saved to {transcript_rel}",
        )
    else:
        print("No earnings call transcript found.")

    assumptions_path = _valuation_inputs_path(company_dir, args.asof)
    assumptions = _build_assumptions(metrics, data.analyst_estimates)
    _write_assumptions(assumptions_path, assumptions, overwrite=args.overwrite_assumptions)

    if args.skip_analysis:
        print("Skipping analysis run.")
        return

    run_company(base_dir, ticker, args.asof)


if __name__ == "__main__":
    main()
