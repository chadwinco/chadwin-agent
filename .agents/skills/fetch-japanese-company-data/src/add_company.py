#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

from japan_fetch import fetch_japanese_company_data, resolve_japanese_identifier
from loaders import load_company_data
from metrics import compute_metrics
from official_ir_fetch import fetch_nintendo_official_ir_documents
from transcript_fetch import fetch_latest_transcript_with_report


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


BASE_DIR = _default_base_dir()


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


def _build_assumptions(metrics: dict) -> dict:
    base_growth = _clamp(metrics.get("avg_revenue_growth", 0.02), -0.03, 0.08)
    base_margin = _clamp(metrics.get("avg_fcf_margin", 0.05), 0.02, 0.18)

    notes = (
        "Auto-generated from Yahoo Finance annual statements and recent financial averages. "
        "Review and adjust before making decisions."
    )

    bull_growth = _clamp(base_growth + 0.02, -0.01, 0.12)
    bear_growth = _clamp(base_growth - 0.02, -0.06, 0.06)

    bull_margin = _clamp(base_margin + 0.02, 0.03, 0.20)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create or refresh Japanese company data and bootstrap valuation assumptions "
            "from Yahoo Finance annual statements"
        )
    )
    parser.add_argument("--ticker", required=True, help="JP identifier (e.g., 7974, 79740, 7974.T, or seeded ISIN)")
    parser.add_argument("--isin", help="Optional ISIN to help resolve the company mapping")
    parser.add_argument("--base-dir", default=str(BASE_DIR))
    parser.add_argument("--asof", default=str(date.today()))
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

    args = parser.parse_args()
    base_dir = Path(args.base_dir)

    resolved = resolve_japanese_identifier(args.ticker, isin=args.isin)
    ticker = resolved.canonical_ticker

    company_dir = _ensure_dirs(base_dir, ticker)
    data_dir = company_dir / "data"

    print(
        "Resolved identifier "
        f"{args.ticker} -> local code {resolved.local_code}, Yahoo symbol {resolved.yahoo_symbol}, "
        f"repo ticker {resolved.canonical_ticker}"
    )

    print(f"Fetching Japanese market profile and annual statements for {ticker}...")
    fetch_result = fetch_japanese_company_data(resolved=resolved, data_dir=data_dir)

    try:
        profile_rel = fetch_result.profile_path.relative_to(base_dir)
    except ValueError:
        profile_rel = fetch_result.profile_path
    print(f"Saved profile to {profile_rel}")

    data = None
    metrics = {}
    company_name = resolved.company_name or _company_name_from_profile(data_dir)
    try:
        data = load_company_data(base_dir, ticker)
        metrics = compute_metrics(data)
        if not data.profile.empty and "companyName" in data.profile.columns:
            company_name = str(data.profile.iloc[0].get("companyName"))
    except Exception as exc:
        print(
            "Warning: unable to load normalized financial statements for "
            f"{ticker}; using conservative default valuation assumptions. ({exc})"
        )

    official_ir = None
    # Nintendo provides a high-quality official IR feed with PDF links for earnings releases and Q&A.
    if resolved.local_code == "7974":
        print(f"Fetching official IR documents from Nintendo website for {ticker}...")
        official_ir = fetch_nintendo_official_ir_documents(
            data_dir=data_dir,
            asof=args.asof,
            max_documents=14,
        )
        try:
            official_rel = official_ir.report_path.relative_to(base_dir)
        except ValueError:
            official_rel = official_ir.report_path
        print(
            f"Saved Nintendo official IR fetch report to {official_rel} "
            f"({official_ir.documents_written} documents)"
        )

    report_path = _transcript_report_path(data_dir, args.asof)
    if official_ir and official_ir.transcript_path and official_ir.transcript_url:
        report_path.write_text(json.dumps(official_ir.transcript_report_payload(), indent=2))
        try:
            transcript_rel = official_ir.transcript_path.relative_to(base_dir)
        except ValueError:
            transcript_rel = official_ir.transcript_path
        print(f"Saved transcript to {transcript_rel} ({official_ir.transcript_url})")
    else:
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
        report_path.write_text(json.dumps(report.to_dict(), indent=2))
        transcript = report.transcript
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

    try:
        report_rel = report_path.relative_to(base_dir)
    except ValueError:
        report_rel = report_path
    print(f"Wrote transcript fetch report to {report_rel}")

    assumptions_path = _valuation_inputs_path(company_dir, args.asof)
    assumptions = _build_assumptions(metrics)
    _write_assumptions(assumptions_path, assumptions, overwrite=args.overwrite_assumptions)

    try:
        assumptions_rel = assumptions_path.relative_to(base_dir)
    except ValueError:
        assumptions_rel = assumptions_path
    print(f"Wrote valuation assumptions to {assumptions_rel}")


if __name__ == "__main__":
    main()
