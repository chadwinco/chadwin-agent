#!/usr/bin/env python3
"""Fetch daily SEC filings and write per-form JSONL snapshots."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from edgar import get_company_tickers, get_filings, set_identity

TARGET_FORMS: Tuple[str, ...] = ("10-K", "10-Q", "20-F", "8-K", "6-K", "S-1")


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected format: YYYY-MM-DD."
        ) from exc


def _iter_business_days(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def _ticker_sort_key(ticker: str) -> Tuple[int, int, str]:
    base_like = 0 if "-" not in ticker and "." not in ticker else 1
    return (base_like, len(ticker), ticker)


def _safe_int(value: object) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _build_primary_ticker_lookup() -> Dict[int, str]:
    table = get_company_tickers(as_dataframe=True, clean_name=True, clean_suffix=False)
    grouped: Dict[int, List[str]] = defaultdict(list)

    for row in table.itertuples(index=False):
        cik = _safe_int(getattr(row, "cik", None))
        ticker = str(getattr(row, "ticker", "")).strip().upper()
        if cik is None or not ticker:
            continue
        grouped[cik].append(ticker)

    lookup: Dict[int, str] = {}
    for cik, ticker_list in grouped.items():
        lookup[cik] = sorted(set(ticker_list), key=_ticker_sort_key)[0]
    return lookup


def _resolve_identity(cli_identity: Optional[str]) -> str:
    identity = (
        (cli_identity or "").strip()
        or os.getenv("EDGAR_IDENTITY", "").strip()
        or os.getenv("SEC_IDENTITY_EMAIL", "").strip()
    )
    if not identity:
        raise SystemExit(
            "SEC identity is required. Set EDGAR_IDENTITY or SEC_IDENTITY_EMAIL, "
            "or pass --identity."
        )
    return identity


def _resolve_latest_complete_filing_day(lookback_days: int) -> date:
    if lookback_days < 1:
        raise SystemExit("--lookback-days must be >= 1.")

    today = date.today()
    for offset in range(1, lookback_days + 1):
        candidate = today - timedelta(days=offset)
        filings = get_filings(
            filing_date=candidate.isoformat(),
            form=list(TARGET_FORMS),
            amendments=False,
        )
        if filings is not None and len(filings) > 0:
            return candidate

    return today - timedelta(days=1)


def _resolve_date_window(args: argparse.Namespace) -> Tuple[date, date]:
    if args.date and (args.start_date or args.end_date):
        raise SystemExit("Use either --date or --start-date/--end-date, not both.")
    if args.end_date and not args.start_date:
        raise SystemExit("--end-date requires --start-date.")

    if args.date:
        return args.date, args.date
    if args.start_date:
        end_date = args.end_date or args.start_date
        return args.start_date, end_date

    if args.date_mode == "today":
        today = date.today()
        return today, today

    resolved = _resolve_latest_complete_filing_day(lookback_days=args.lookback_days)
    return resolved, resolved


def _fetch_records(
    start: date, end: date, cik_to_ticker: Dict[int, str]
) -> Dict[Tuple[str, str], List[Dict[str, Optional[str]]]]:
    filing_date = (
        start.isoformat() if start == end else f"{start.isoformat()}:{end.isoformat()}"
    )
    filings = get_filings(
        filing_date=filing_date,
        form=list(TARGET_FORMS),
        amendments=False,
    )

    records: Dict[Tuple[str, str], List[Dict[str, Optional[str]]]] = defaultdict(list)
    if filings is None or len(filings) == 0:
        return records

    frame = filings.to_pandas()
    for row in frame.itertuples(index=False):
        form_type = str(getattr(row, "form", "")).strip().upper()
        filing_day = str(getattr(row, "filing_date", "")).strip()
        if form_type not in TARGET_FORMS or not filing_day:
            continue

        cik = _safe_int(getattr(row, "cik", None))
        ticker = cik_to_ticker.get(cik) if cik is not None else None
        company_name = str(getattr(row, "company", "")).strip()
        accession = str(getattr(row, "accession_number", "")).strip()

        records[(filing_day, form_type)].append(
            {
                "company_name": company_name,
                "ticker": ticker,
                "form_type": form_type,
                "filing_date": filing_day,
                "accession_number": accession,
            }
        )

    return records


def _record_sort_key(record: Dict[str, Optional[str]]) -> Tuple[str, str]:
    accession = str(record.get("accession_number") or "")
    company = str(record.get("company_name") or "")
    return (accession, company)


def _write_daily_files(
    output_root: Path,
    business_days: List[date],
    records: Dict[Tuple[str, str], List[Dict[str, Optional[str]]]],
) -> int:
    files_written = 0
    for form in TARGET_FORMS:
        form_dir = output_root / form
        form_dir.mkdir(parents=True, exist_ok=True)
        for day_value in business_days:
            day_key = day_value.isoformat()
            out_path = form_dir / f"{day_key}.jsonl"
            legacy_json_path = form_dir / f"{day_key}.json"
            if legacy_json_path.exists():
                legacy_json_path.unlink()

            payload = sorted(records.get((day_key, form), []), key=_record_sort_key)
            with out_path.open("w", encoding="utf-8") as handle:
                for row in payload:
                    handle.write(json.dumps(row, ensure_ascii=True))
                    handle.write("\n")
            files_written += 1
    return files_written


def fetch_daily_sec_filings(
    start_date: date,
    end_date: date,
    output_root: Path,
    identity: str,
) -> None:
    if end_date < start_date:
        raise SystemExit("--end-date must be on or after --start-date.")

    set_identity(identity)
    business_days = list(_iter_business_days(start_date, end_date))
    if not business_days:
        print("No business days in the selected date range. Nothing written.")
        return

    cik_to_ticker = _build_primary_ticker_lookup()
    records = _fetch_records(start_date, end_date, cik_to_ticker)
    files_written = _write_daily_files(output_root, business_days, records)

    non_empty = sum(1 for rows in records.values() if rows)
    print(f"Requested window: {start_date.isoformat()} -> {end_date.isoformat()}")
    print(f"Business days: {len(business_days)}")
    print(f"Form/date buckets with filings: {non_empty}")
    print(f"Files written: {files_written}")
    print(f"Output root: {output_root}")


def parse_args() -> argparse.Namespace:
    default_output = Path(__file__).resolve().parents[1] / "assets"
    parser = argparse.ArgumentParser(
        description="Fetch daily SEC filings and write per-form JSONL files."
    )
    parser.add_argument(
        "--date",
        type=_parse_date,
        help="Single date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--start-date",
        type=_parse_date,
        help="Range start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--end-date",
        type=_parse_date,
        help="Range end date in YYYY-MM-DD format. Defaults to --start-date.",
    )
    parser.add_argument(
        "--date-mode",
        choices=("latest-complete", "today"),
        default="latest-complete",
        help="Default date behavior when no explicit date arguments are provided.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=14,
        help="Days to scan backward for --date-mode latest-complete.",
    )
    parser.add_argument(
        "--identity",
        help="SEC User-Agent identity string. Falls back to EDGAR_IDENTITY or SEC_IDENTITY_EMAIL.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=default_output,
        help=f"Output directory. Default: {default_output}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    identity = _resolve_identity(args.identity)
    set_identity(identity)
    start_date, end_date = _resolve_date_window(args)
    output_root = args.output_root.resolve()

    fetch_daily_sec_filings(
        start_date=start_date,
        end_date=end_date,
        output_root=output_root,
        identity=identity,
    )


if __name__ == "__main__":
    main()
