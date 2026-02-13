#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from company_idea_queue_core import (
    COUNTRY_DIR_BY_MARKET,
    DATA_ROOT_RELATIVE_PATH,
    DEFAULT_COMPANIES_RELATIVE_PATH,
    TASK_RESEARCH,
    detect_market,
    load_user_preferences,
    market_is_allowed,
    pick_next_company,
    queue_key,
    read_queue_entries,
    resolve_preferences_path,
)


@dataclass
class ReportStatus:
    latest_report_path: Path | None
    latest_report_mtime: float | None


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / DATA_ROOT_RELATIVE_PATH).exists() and (parent / ".agents" / "skills").exists():
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
        help=(
            "Override ideas log path "
            "(default: .chadwin-data/idea-screens/company-ideas-log.jsonl)."
        ),
    )
    parser.add_argument("--identity", help="EDGAR identity for US fetch.")
    parser.add_argument("--isin", help="Optional identifier for non-US fetch scripts.")
    parser.add_argument(
        "--market",
        choices=["us", "non-us"],
        help="Optional market override. Otherwise inferred from ticker/profile/queue.",
    )
    parser.add_argument(
        "--fetch-script",
        help=(
            "Optional path to a market fetch script (`add_company.py`). "
            "Relative paths are resolved from --base-dir."
        ),
    )
    parser.add_argument("--overwrite-assumptions", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not execute fetch script; emit decision only.",
    )
    parser.add_argument(
        "--post-report-check",
        action="store_true",
        help=(
            "Evaluate latest same-date report package and route to progressive follow-up "
            "research. Use after run-llm-workflow completes."
        ),
    )
    parser.add_argument(
        "--followup-confidence-threshold",
        type=float,
        default=0.80,
        help=(
            "Minimum thesis-confidence threshold (0-1) used by "
            "--post-report-check (default: 0.80)."
        ),
    )
    parser.add_argument(
        "--preferences-path",
        help="Override preferences path (default: .chadwin-data/user_preferences.json).",
    )
    parser.add_argument(
        "--ignore-preferences",
        action="store_true",
        help="Ignore preference-based filtering and market guards.",
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


def _asof_report_dir_match(report_dir_name: str, asof: str) -> bool:
    return report_dir_name == asof or report_dir_name.startswith(f"{asof}-")


def _latest_report_for_asof(company_dir: Path, asof: str) -> Path | None:
    reports_dir = company_dir / "reports"
    if not reports_dir.exists():
        return None

    latest_report_path: Path | None = None
    latest_mtime: float | None = None
    for report_dir in reports_dir.iterdir():
        if not report_dir.is_dir() or not _asof_report_dir_match(report_dir.name, asof):
            continue
        report_path = report_dir / "report.md"
        if not report_path.is_file():
            continue
        mtime = report_path.stat().st_mtime
        if latest_mtime is None or mtime > latest_mtime:
            latest_mtime = mtime
            latest_report_path = report_path
    return latest_report_path


def _parse_bool_token(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().strip("`").lower()
    normalized = normalized.replace("*", "")
    normalized = normalized.split("(", 1)[0].strip()
    if normalized in {"yes", "true"}:
        return True
    if normalized in {"no", "false"}:
        return False
    return None


def _parse_confidence_pct(value: str | None) -> float | None:
    if value is None:
        return None
    number_match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not number_match:
        return None
    try:
        parsed = float(number_match.group(0))
    except ValueError:
        return None
    if "%" not in value and 0.0 <= parsed <= 1.0:
        parsed *= 100.0
    return parsed


def _parse_int_token(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.search(r"-?\d+", value)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _normalize_gate_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


STOP_GATE_FIELD_MAP = {
    "thesis confidence": "thesis_confidence_pct",
    "highest impact levers": "highest_impact_levers",
    "levers resolved": "levers_resolved",
    "open thesis critical levers": "open_thesis_critical_levers",
    "diminishing returns from additional research": "diminishing_returns",
    "research complete": "research_complete",
    "next best research focus": "next_best_research_focus",
}


def _extract_report_stop_gate(report_path: Path) -> dict[str, Any] | None:
    try:
        text = report_path.read_text(encoding="utf-8")
    except Exception:
        return None

    lines = text.splitlines()
    start_idx: int | None = None
    for index, raw in enumerate(lines):
        if raw.strip().lower().startswith("## research stop gate"):
            start_idx = index + 1
            break
    if start_idx is None:
        return None

    raw_fields: dict[str, str] = {}
    for raw in lines[start_idx:]:
        stripped = raw.strip()
        if stripped.startswith("## "):
            break
        if not stripped or not (stripped.startswith("- ") or stripped.startswith("* ")):
            continue
        line = stripped[2:].strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key_norm = _normalize_gate_key(key)
        canonical = STOP_GATE_FIELD_MAP.get(key_norm)
        if canonical:
            raw_fields[canonical] = value.strip().strip("`")

    if not raw_fields:
        return None

    return {
        "section_found": True,
        "thesis_confidence_pct": _parse_confidence_pct(
            raw_fields.get("thesis_confidence_pct")
        ),
        "highest_impact_levers": _parse_int_token(raw_fields.get("highest_impact_levers")),
        "levers_resolved": _parse_int_token(raw_fields.get("levers_resolved")),
        "open_thesis_critical_levers": _parse_int_token(
            raw_fields.get("open_thesis_critical_levers")
        ),
        "diminishing_returns": _parse_bool_token(raw_fields.get("diminishing_returns")),
        "research_complete": _parse_bool_token(raw_fields.get("research_complete")),
        "next_best_research_focus": raw_fields.get("next_best_research_focus"),
        "raw_fields": raw_fields,
    }


def _post_report_decision(
    *,
    company_dir: Path,
    asof: str,
    confidence_threshold: float,
) -> dict[str, Any]:
    report_path = _latest_report_for_asof(company_dir, asof)
    if report_path is None:
        return {
            "status": "error",
            "reason": "missing_report_for_asof",
            "next_action": "done",
            "asof": asof,
        }

    report_dir = report_path.parent
    stop_gate = _extract_report_stop_gate(report_path)
    if stop_gate is None:
        followup_focus = "highest-impact-unresolved-lever"
        confidence_gate_passed = False
        next_action = "run_research"
        reason = "missing_research_stop_gate"
        confidence_pct = None
        open_critical = None
        research_complete = None
        diminishing_returns = None
    else:
        confidence_pct = stop_gate.get("thesis_confidence_pct")
        open_critical = stop_gate.get("open_thesis_critical_levers")
        research_complete = stop_gate.get("research_complete")
        diminishing_returns = stop_gate.get("diminishing_returns")
        confidence_required_pct = confidence_threshold * 100.0

        confidence_ok = (
            isinstance(confidence_pct, (int, float))
            and float(confidence_pct) >= confidence_required_pct
        )
        confidence_gate_passed = bool(
            research_complete is True
            and diminishing_returns is True
            and open_critical == 0
            and confidence_ok
        )
        next_action = "done" if confidence_gate_passed else "run_research"
        reason = (
            "research_confidence_gate_passed"
            if confidence_gate_passed
            else "research_confidence_gate_not_met"
        )
        followup_focus = (
            str(stop_gate.get("next_best_research_focus") or "").strip()
            or "highest-impact-unresolved-lever"
        )

    result = {
        "status": "ok",
        "reason": reason,
        "next_action": next_action,
        "asof": asof,
        "baseline_report_dir": report_dir.name,
        "report_path": str(report_path),
        "followup_confidence_threshold": confidence_threshold,
        "followup_focus": followup_focus,
        "research_stop_gate_found": stop_gate is not None,
        "confidence_gate_passed": confidence_gate_passed,
        "thesis_confidence_pct": confidence_pct,
        "open_thesis_critical_levers": open_critical,
        "research_complete": research_complete,
        "diminishing_returns": diminishing_returns,
    }
    if stop_gate is not None:
        result["research_stop_gate"] = stop_gate
    return result


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
    companies_dir = base_dir / DEFAULT_COMPANIES_RELATIVE_PATH
    if not companies_dir.exists():
        return []

    key = queue_key(ticker)
    exact = ticker.upper()
    matches: list[Path] = []
    candidates: list[Path] = []
    for entry in companies_dir.iterdir():
        if not entry.is_dir():
            continue
        if (entry / "data").exists() or (entry / "reports").exists():
            candidates.append(entry)
            continue
        for nested in entry.iterdir():
            if not nested.is_dir():
                continue
            if (nested / "data").exists() or (nested / "reports").exists():
                candidates.append(nested)

    for candidate in candidates:
        name = candidate.name.upper()
        if name == exact:
            matches.insert(0, candidate)
            continue
        if queue_key(name) == key:
            matches.append(candidate)
    return matches


def _default_company_dir(base_dir: Path, ticker: str, market: str) -> Path:
    country_dir = COUNTRY_DIR_BY_MARKET.get(market, "US")
    return base_dir / DEFAULT_COMPANIES_RELATIVE_PATH / country_dir / ticker


def _queue_market(base_dir: Path, ticker: str, ideas_log: str | None) -> str | None:
    for entry in read_queue_entries(base_dir=base_dir, ideas_log=ideas_log):
        if queue_key(entry.get("ticker")) == queue_key(ticker):
            market = str(entry.get("market") or "").strip().lower()
            if market in {"us", "non-us"}:
                return market
    return None


def _infer_market(
    *,
    base_dir: Path,
    ticker: str,
    ideas_log: str | None,
    override: str | None,
) -> str:
    if override in {"us", "non-us"}:
        return override

    matches = _matching_company_dirs(base_dir, ticker)
    for company_dir in matches:
        exchange = _profile_exchange(company_dir)
        inferred = detect_market(ticker=company_dir.name, exchange=exchange)
        if inferred in {"us", "non-us"}:
            return inferred

    queued = _queue_market(base_dir, ticker, ideas_log)
    if queued in {"us", "non-us"}:
        return queued

    inferred = detect_market(ticker=ticker)
    if inferred in {"us", "non-us"}:
        return inferred

    return "us"


def _fetch_script(base_dir: Path, market: str, override: str | None) -> Path | None:
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = base_dir / path
        return path
    if market == "us":
        return base_dir / ".agents" / "skills" / "fetch-us-company-data" / "scripts" / "add_company.py"
    return None


def _run_fetch(
    *,
    script: Path,
    base_dir: Path,
    market: str,
    ticker: str,
    asof: str,
    ideas_log: str | None,
    identity: str | None,
    isin: str | None,
    overwrite_assumptions: bool,
    preferences_path: str | None,
    ignore_preferences: bool,
) -> tuple[int, list[str]]:
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
    if preferences_path:
        command.extend(["--preferences-path", preferences_path])
    if ignore_preferences:
        command.append("--ignore-preferences")
    if overwrite_assumptions:
        command.append("--overwrite-assumptions")
    if market == "us" and identity:
        command.extend(["--identity", identity])
    if market != "us" and isin:
        command.extend(["--isin", isin])

    completed = subprocess.run(command, check=False)
    return completed.returncode, command


def _pick_from_queue(
    *,
    base_dir: Path,
    ideas_log: str | None,
    preferences_path: str | None,
    respect_preferences: bool,
) -> dict[str, Any]:
    selected = pick_next_company(
        base_dir=base_dir,
        task=TASK_RESEARCH,
        ideas_log=ideas_log,
        preferences_path=preferences_path,
        respect_preferences=respect_preferences,
    )
    if not selected:
        raise SystemExit(
            "No company available in .chadwin-data/idea-screens/company-ideas-log.jsonl. "
            "Run fetch-us-investment-ideas first, relax preferences, or pass --ticker."
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
    preferences_applied = not args.ignore_preferences
    resolved_preferences_path = resolve_preferences_path(
        base_dir=base_dir,
        preferences_path=args.preferences_path,
    )
    preferences = (
        load_user_preferences(
            base_dir=base_dir,
            preferences_path=args.preferences_path,
        )
        if preferences_applied
        else {}
    )

    if args.post_report_check:
        if not ticker_input:
            result = {
                "status": "error",
                "reason": "ticker_required_for_post_report_check",
                "next_action": "done",
                "asof": args.asof,
            }
            print(json.dumps(result, indent=2))
            return 2

        market = _infer_market(
            base_dir=base_dir,
            ticker=ticker_input,
            ideas_log=args.ideas_log,
            override=args.market,
        )
        if preferences_applied and not market_is_allowed(market, preferences):
            result = {
                "status": "error",
                "reason": "market_excluded_by_preferences",
                "market": market,
                "ticker_input": ticker_input,
                "next_action": "done",
                "preferences_applied": True,
                "preferences_path": str(resolved_preferences_path),
            }
            print(json.dumps(result, indent=2))
            return 2

        matches = _matching_company_dirs(base_dir, ticker_input)
        company_dir = (
            matches[0]
            if matches
            else _default_company_dir(base_dir, ticker_input, market)
        )
        if not company_dir.exists():
            result = {
                "status": "error",
                "reason": "company_package_not_found",
                "market": market,
                "ticker_input": ticker_input,
                "resolved_ticker": ticker_input,
                "company_dir": str(company_dir),
                "next_action": "done",
                "asof": args.asof,
            }
            print(json.dumps(result, indent=2))
            return 2

        decision = _post_report_decision(
            company_dir=company_dir,
            asof=args.asof,
            confidence_threshold=max(0.0, min(1.0, args.followup_confidence_threshold)),
        )
        decision.update(
            {
                "market": market,
                "ticker_input": ticker_input,
                "resolved_ticker": company_dir.name.upper(),
                "explicit_ticker": explicit_ticker,
                "company_dir": str(company_dir),
                "post_report_check": True,
                "preferences_applied": preferences_applied,
                "preferences_path": (
                    str(resolved_preferences_path) if preferences_applied else None
                ),
            }
        )
        print(json.dumps(decision, indent=2))
        return 0 if decision.get("status") == "ok" else 2

    if not ticker_input:
        queued = _pick_from_queue(
            base_dir=base_dir,
            ideas_log=args.ideas_log,
            preferences_path=args.preferences_path,
            respect_preferences=preferences_applied,
        )
        ticker_input = str(queued["ticker"]).strip().upper()
        market = str(queued.get("market") or "").strip().lower()
        if market not in {"us", "non-us"}:
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

    if preferences_applied and not market_is_allowed(market, preferences):
        result = {
            "status": "error",
            "reason": "market_excluded_by_preferences",
            "market": market,
            "ticker_input": ticker_input,
            "preferences_applied": True,
            "preferences_path": str(resolved_preferences_path),
        }
        print(json.dumps(result, indent=2))
        return 2

    before_matches = _matching_company_dirs(base_dir, ticker_input)
    before_company_dir = (
        before_matches[0]
        if before_matches
        else _default_company_dir(base_dir, ticker_input, market)
    )
    before_data_mtime = _max_mtime(before_company_dir / "data")

    fetch_return_code = 0
    fetch_command: list[str] = []
    fetch_script: Path | None = _fetch_script(base_dir, market, args.fetch_script)
    fetch_skipped_reason: str | None = None
    if args.dry_run:
        print("Dry run: skipping fetch execution.")
    else:
        if fetch_script is None:
            if before_data_mtime is None:
                result = {
                    "status": "error",
                    "reason": "missing_market_fetch_script",
                    "market": market,
                    "ticker_input": ticker_input,
                    "suggested_fix": "Install a fetch skill for this market or pass --fetch-script.",
                }
                print(json.dumps(result, indent=2))
                return 2
            fetch_skipped_reason = "missing_market_fetch_script"
        elif not fetch_script.exists():
            result = {
                "status": "error",
                "reason": "fetch_script_not_found",
                "market": market,
                "ticker_input": ticker_input,
                "fetch_script": str(fetch_script),
            }
            print(json.dumps(result, indent=2))
            return 2

        if fetch_script is not None:
            fetch_return_code, fetch_command = _run_fetch(
                script=fetch_script,
                base_dir=base_dir,
                market=market,
                ticker=ticker_input,
                asof=args.asof,
                ideas_log=args.ideas_log,
                identity=args.identity,
                isin=args.isin,
                overwrite_assumptions=args.overwrite_assumptions,
                preferences_path=args.preferences_path,
                ignore_preferences=args.ignore_preferences,
            )
            if fetch_return_code != 0:
                result = {
                    "status": "error",
                    "reason": "fetch_failed",
                    "market": market,
                    "ticker_input": ticker_input,
                    "fetch_script": str(fetch_script),
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
        "fetch_ran": bool(fetch_command),
        "fetch_script": str(fetch_script) if fetch_script is not None else None,
        "fetch_skipped_reason": fetch_skipped_reason,
        "fetch_command": fetch_command,
        "next_action": next_action,
        "reason": reason,
        "preferences_applied": preferences_applied,
        "preferences_path": (
            str(resolved_preferences_path) if preferences_applied else None
        ),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
