#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
QUEUE_SRC = SKILL_DIR / "src"
if str(QUEUE_SRC) not in sys.path:
    sys.path.insert(0, str(QUEUE_SRC))

from company_idea_queue import (  # noqa: E402
    TASK_RESEARCH,
    detect_market,
    pick_next_company,
    queue_key,
    read_queue_entries,
)


@dataclass
class ReportStatus:
    latest_report_path: Path | None
    latest_report_mtime: float | None


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Orchestrate company fetch + research routing. "
            "Runs the right market fetch script and decides whether research is needed."
        )
    )
    parser.add_argument("--ticker", help="Optional ticker/identifier. Omit to auto-pick from ideas log.")
    parser.add_argument("--asof", default=str(date.today()))
    parser.add_argument("--base-dir", default=str(_default_base_dir()))
    parser.add_argument(
        "--ideas-log",
        help="Override ideas log path (default: idea-screens/company-ideas-log.jsonl).",
    )
    parser.add_argument("--identity", help="EDGAR identity for US fetch.")
    parser.add_argument("--isin", help="Optional ISIN for JP fetch.")
    parser.add_argument(
        "--market",
        choices=["us", "jp"],
        help="Optional market override. Otherwise inferred from ticker/profile/queue.",
    )
    parser.add_argument("--overwrite-assumptions", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not execute fetch script; emit decision only.",
    )
    return parser.parse_args()


def _max_mtime(root: Path) -> float | None:
    if not root.exists():
        return None

    latest: float | None = None
    for path in root.rglob("*"):
        if path.is_file():
            mtime = path.stat().st_mtime
            if latest is None or mtime > latest:
                latest = mtime
    return latest


def _latest_report_status(company_dir: Path) -> ReportStatus:
    reports_dir = company_dir / "reports"
    if not reports_dir.exists():
        return ReportStatus(latest_report_path=None, latest_report_mtime=None)

    latest_path: Path | None = None
    latest_mtime: float | None = None
    for report_path in reports_dir.rglob("report.md"):
        if not report_path.is_file():
            continue
        mtime = report_path.stat().st_mtime
        if latest_mtime is None or mtime > latest_mtime:
            latest_mtime = mtime
            latest_path = report_path
    return ReportStatus(latest_report_path=latest_path, latest_report_mtime=latest_mtime)


def _profile_exchange(company_dir: Path) -> str | None:
    profile_path = company_dir / "data" / "company_profile.csv"
    if not profile_path.exists():
        return None
    try:
        with profile_path.open("r", newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp), None)
    except Exception:
        return None
    if not row:
        return None

    for key in ("exchange", "fullExchangeName", "market"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return None


def _matching_company_dirs(base_dir: Path, ticker: str) -> list[Path]:
    companies_dir = base_dir / "companies"
    if not companies_dir.exists():
        return []

    key = queue_key(ticker)
    exact = ticker.upper()
    matches: list[Path] = []
    for candidate in companies_dir.iterdir():
        if not candidate.is_dir():
            continue
        name = candidate.name.upper()
        if name == exact:
            matches.insert(0, candidate)
            continue
        if queue_key(name) == key:
            matches.append(candidate)
    return matches


def _queue_market(base_dir: Path, ticker: str, ideas_log: str | None) -> str | None:
    for entry in read_queue_entries(base_dir=base_dir, ideas_log=ideas_log):
        if queue_key(entry.get("ticker")) == queue_key(ticker):
            market = str(entry.get("market") or "").strip().lower()
            if market in {"us", "jp"}:
                return market
    return None


def _infer_market(
    *,
    base_dir: Path,
    ticker: str,
    ideas_log: str | None,
    override: str | None,
) -> str:
    if override in {"us", "jp"}:
        return override

    matches = _matching_company_dirs(base_dir, ticker)
    for company_dir in matches:
        exchange = _profile_exchange(company_dir)
        inferred = detect_market(ticker=company_dir.name, exchange=exchange)
        if inferred in {"us", "jp"}:
            return inferred

    queued = _queue_market(base_dir, ticker, ideas_log)
    if queued in {"us", "jp"}:
        return queued

    inferred = detect_market(ticker=ticker)
    if inferred in {"us", "jp"}:
        return inferred

    return "us"


def _fetch_script(base_dir: Path, market: str) -> Path:
    if market == "us":
        return base_dir / ".agents" / "skills" / "fetch-us-company-data" / "scripts" / "add_company.py"
    return (
        base_dir
        / ".agents"
        / "skills"
        / "fetch-japanese-company-data"
        / "scripts"
        / "add_company.py"
    )


def _run_fetch(
    *,
    base_dir: Path,
    market: str,
    ticker: str,
    asof: str,
    ideas_log: str | None,
    identity: str | None,
    isin: str | None,
    overwrite_assumptions: bool,
) -> tuple[int, list[str]]:
    script = _fetch_script(base_dir, market)
    command = [
        "python3",
        str(script),
        "--base-dir",
        str(base_dir),
        "--asof",
        asof,
        "--ticker",
        ticker,
    ]
    if ideas_log:
        command.extend(["--ideas-log", ideas_log])
    if overwrite_assumptions:
        command.append("--overwrite-assumptions")
    if market == "us" and identity:
        command.extend(["--identity", identity])
    if market == "jp" and isin:
        command.extend(["--isin", isin])

    completed = subprocess.run(command, check=False)
    return completed.returncode, command


def _pick_from_queue(base_dir: Path, ideas_log: str | None) -> dict[str, Any]:
    selected = pick_next_company(base_dir=base_dir, task=TASK_RESEARCH, ideas_log=ideas_log)
    if not selected:
        raise SystemExit(
            "No company available in idea-screens/company-ideas-log.jsonl. "
            "Run fetch-us-investment-ideas first or pass --ticker."
        )
    return selected


def _format_utc(mtime: float | None) -> str | None:
    if mtime is None:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    args = _parse_args()
    base_dir = Path(args.base_dir).resolve()
    explicit_ticker = bool(args.ticker)
    ticker_input = (args.ticker or "").strip().upper()

    if not ticker_input:
        queued = _pick_from_queue(base_dir, args.ideas_log)
        ticker_input = str(queued["ticker"]).strip().upper()
        market = str(queued.get("market") or "").strip().lower()
        if market not in {"us", "jp"}:
            market = _infer_market(
                base_dir=base_dir,
                ticker=ticker_input,
                ideas_log=args.ideas_log,
                override=args.market,
            )
        print(
            "No --ticker provided. Selected "
            f"{ticker_input} from ideas log for market={market}."
        )
    else:
        market = _infer_market(
            base_dir=base_dir,
            ticker=ticker_input,
            ideas_log=args.ideas_log,
            override=args.market,
        )

    before_matches = _matching_company_dirs(base_dir, ticker_input)
    before_company_dir = before_matches[0] if before_matches else base_dir / "companies" / ticker_input
    before_data_mtime = _max_mtime(before_company_dir / "data")

    fetch_return_code = 0
    fetch_command: list[str] = []
    if args.dry_run:
        print("Dry run: skipping fetch execution.")
    else:
        fetch_return_code, fetch_command = _run_fetch(
            base_dir=base_dir,
            market=market,
            ticker=ticker_input,
            asof=args.asof,
            ideas_log=args.ideas_log,
            identity=args.identity,
            isin=args.isin,
            overwrite_assumptions=args.overwrite_assumptions,
        )
        if fetch_return_code != 0:
            result = {
                "status": "error",
                "reason": "fetch_failed",
                "market": market,
                "ticker_input": ticker_input,
                "fetch_command": fetch_command,
                "fetch_return_code": fetch_return_code,
            }
            print(json.dumps(result, indent=2))
            return fetch_return_code

    after_matches = _matching_company_dirs(base_dir, ticker_input)
    after_company_dir = after_matches[0] if after_matches else before_company_dir
    resolved_ticker = after_company_dir.name.upper()
    after_data_mtime = _max_mtime(after_company_dir / "data")
    after_report = _latest_report_status(after_company_dir)

    if args.dry_run:
        new_data_fetched = False
    elif before_data_mtime is None and after_data_mtime is not None:
        new_data_fetched = True
    elif before_data_mtime is not None and after_data_mtime is not None:
        new_data_fetched = after_data_mtime > before_data_mtime
    else:
        new_data_fetched = False

    report_exists = after_report.latest_report_path is not None
    report_up_to_date = bool(
        report_exists
        and after_report.latest_report_mtime is not None
        and after_data_mtime is not None
        and after_report.latest_report_mtime >= after_data_mtime
    )

    if explicit_ticker and (not new_data_fetched) and report_up_to_date:
        next_action = "done"
        reason = "no_new_data_and_report_is_current"
    else:
        next_action = "run_research"
        reason = (
            "selected_from_queue"
            if not explicit_ticker
            else "data_updated_or_report_missing_or_report_stale"
        )

    result = {
        "status": "ok",
        "market": market,
        "ticker_input": ticker_input,
        "resolved_ticker": resolved_ticker,
        "asof": args.asof,
        "explicit_ticker": explicit_ticker,
        "company_dir": str(after_company_dir),
        "before_data_mtime_utc": _format_utc(before_data_mtime),
        "after_data_mtime_utc": _format_utc(after_data_mtime),
        "new_data_fetched": new_data_fetched,
        "report_exists": report_exists,
        "latest_report_path": str(after_report.latest_report_path) if after_report.latest_report_path else None,
        "latest_report_mtime_utc": _format_utc(after_report.latest_report_mtime),
        "report_up_to_date": report_up_to_date,
        "fetch_ran": not args.dry_run,
        "fetch_command": fetch_command,
        "next_action": next_action,
        "reason": reason,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
