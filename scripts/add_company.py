#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(BASE_DIR))

from research.edgar_fetch import fetch_company_filings, fetch_company_financials  # noqa: E402
from research.loaders import load_company_data  # noqa: E402
from research.metrics import compute_metrics  # noqa: E402
from research.transcript_fetch import fetch_latest_transcript  # noqa: E402
from scripts.run_company import run_company  # noqa: E402


def _ensure_dirs(base_dir: Path, ticker: str) -> Path:
    company_dir = base_dir / "companies" / ticker
    (company_dir / "data").mkdir(parents=True, exist_ok=True)
    (company_dir / "analysis").mkdir(parents=True, exist_ok=True)
    (company_dir / "model").mkdir(parents=True, exist_ok=True)
    return company_dir


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _build_assumptions(metrics: dict) -> dict:
    base_growth = _clamp(metrics.get("avg_revenue_growth", 0.02), -0.02, 0.08)
    base_margin = _clamp(metrics.get("avg_fcf_margin", 0.05), 0.02, 0.15)

    bull_growth = _clamp(base_growth + 0.02, -0.01, 0.12)
    bull_margin = _clamp(base_margin + 0.02, 0.03, 0.18)

    bear_growth = _clamp(base_growth - 0.02, -0.05, 0.06)
    bear_margin = _clamp(base_margin - 0.02, 0.01, 0.12)

    return {
        "forecast_years": 5,
        "notes": "Auto-generated from recent financial averages. Review and adjust before making decisions.",
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

    data = load_company_data(base_dir, ticker)
    metrics = compute_metrics(data)

    company_name = None
    if not data.profile.empty and "companyName" in data.profile.columns:
        company_name = str(data.profile.iloc[0].get("companyName"))

    print(f"Fetching latest earnings call transcript for {ticker}...")
    transcript = fetch_latest_transcript(ticker, data_dir, company_name=company_name, asof=args.asof)
    if transcript:
        _append_source_log(
            base_dir,
            ticker,
            args.asof,
            transcript.source_url,
            f"Saved to companies/{ticker}/data/{transcript.path.name}",
        )
    else:
        print("No earnings call transcript found.")

    assumptions_path = company_dir / "model" / "assumptions.yaml"
    assumptions = _build_assumptions(metrics)
    _write_assumptions(assumptions_path, assumptions, overwrite=args.overwrite_assumptions)

    if args.skip_analysis:
        print("Skipping analysis run.")
        return

    run_company(base_dir, ticker, args.asof)


if __name__ == "__main__":
    main()
