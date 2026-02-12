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
        "--followup-mode",
        choices=["confidence-gate", "mos-threshold"],
        default="confidence-gate",
        help=(
            "Routing mode for --post-report-check. "
            "`confidence-gate` uses the report's Research Stop Gate section "
            "(default). `mos-threshold` preserves legacy MoS-based routing."
        ),
    )
    parser.add_argument(
        "--followup-confidence-threshold",
        type=float,
        default=0.80,
        help=(
            "Minimum thesis-confidence threshold (0-1) used by "
            "--followup-mode confidence-gate (default: 0.80)."
        ),
    )
    parser.add_argument(
        "--followup-mos-threshold",
        type=float,
        default=0.25,
        help=(
            "Base-case margin-of-safety threshold for follow-up routing during "
            "--post-report-check (default: 0.25)."
        ),
    )
    parser.add_argument(
        "--preferences-path",
        help="Override preferences path (default: preferences/user_preferences.json).",
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


def _extract_report_verdict(report_path: Path) -> str | None:
    try:
        text = report_path.read_text(encoding="utf-8")
    except Exception:
        return None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if "verdict:" not in line.lower():
            continue
        _, _, value = line.partition(":")
        verdict = value.strip()
        if not verdict or "|" in verdict:
            return None
        verdict = verdict.replace("**", "").replace("*", "").replace("`", "").strip()
        return verdict or None
    return None


def _normalize_verdict(verdict: str | None) -> str | None:
    if verdict is None:
        return None
    normalized = verdict.strip().lower()
    if normalized.startswith("attractive"):
        return "attractive"
    if normalized.startswith("watch"):
        return "watch"
    if normalized.startswith("avoid"):
        return "avoid"
    return normalized or None


def _read_base_margin_of_safety(outputs_path: Path) -> float | None:
    try:
        payload = json.loads(outputs_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    scenarios = payload.get("scenarios") or {}
    base = scenarios.get("base") or {}
    value = base.get("margin_of_safety")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _parse_bool_token(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().strip("`").lower()
    normalized = normalized.split("(", 1)[0].strip()
    if normalized in {"yes", "y", "true", "1", "done", "complete"}:
        return True
    if normalized in {"no", "n", "false", "0", "open", "incomplete"}:
        return False
    return None


def _parse_float_token(value: str | None) -> float | None:
    if value is None:
        return None
    fraction_match = re.search(r"(-?\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", value)
    if fraction_match:
        numerator = float(fraction_match.group(1))
        denominator = float(fraction_match.group(2))
        if denominator == 0:
            return None
        return numerator / denominator

    number_match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not number_match:
        return None
    try:
        return float(number_match.group(0))
    except ValueError:
        return None


def _parse_int_token(value: str | None) -> int | None:
    parsed = _parse_float_token(value)
    if parsed is None:
        return None
    return int(round(parsed))


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

    section_lines: list[str] = []
    for raw in lines[start_idx:]:
        stripped = raw.strip()
        if stripped.startswith("## "):
            break
        if stripped:
            section_lines.append(stripped)

    parsed_fields: dict[str, str] = {}
    for raw in section_lines:
        line = raw
        if line.startswith("- "):
            line = line[2:].strip()
        elif line.startswith("* "):
            line = line[2:].strip()
        elif line.startswith("-"):
            line = line[1:].strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key_norm = re.sub(r"[^a-z0-9]+", " ", key.lower()).strip()
        parsed_fields[key_norm] = value.strip().strip("`")

    def _value_for(substrings: tuple[str, ...]) -> str | None:
        for key, value in parsed_fields.items():
            if any(sub in key for sub in substrings):
                return value
        return None

    confidence_raw = _value_for(("thesis confidence", "confidence"))
    confidence_pct = _parse_float_token(confidence_raw)
    if confidence_pct is not None and 0.0 <= confidence_pct <= 1.0:
        confidence_pct = confidence_pct * 100.0

    research_complete = _parse_bool_token(
        _value_for(("research complete", "stop research", "research stop"))
    )
    continue_research = _parse_bool_token(_value_for(("continue research",)))
    if research_complete is None and continue_research is not None:
        research_complete = not continue_research

    diminishing_returns = _parse_bool_token(
        _value_for(("diminishing returns", "incremental insight low"))
    )

    return {
        "section_found": True,
        "thesis_confidence_pct": confidence_pct,
        "highest_impact_levers": _parse_int_token(
            _value_for(("highest impact levers",))
        ),
        "levers_resolved": _parse_int_token(
            _value_for(("levers resolved", "resolved levers"))
        ),
        "open_thesis_critical_levers": _parse_int_token(
            _value_for(("open thesis critical levers", "open critical levers"))
        ),
        "diminishing_returns": diminishing_returns,
        "research_complete": research_complete,
        "next_best_research_focus": _value_for(("next best research focus", "next focus")),
        "raw_fields": parsed_fields,
    }


def _post_report_decision(
    *,
    company_dir: Path,
    asof: str,
    mos_threshold: float,
    followup_mode: str,
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
    outputs_path = report_dir / "valuation" / "outputs.json"
    if not outputs_path.exists():
        return {
            "status": "error",
            "reason": "missing_valuation_outputs",
            "next_action": "done",
            "asof": asof,
            "baseline_report_dir": report_dir.name,
            "report_path": str(report_path),
            "valuation_outputs_path": str(outputs_path),
        }

    base_mos = _read_base_margin_of_safety(outputs_path)
    if base_mos is None:
        return {
            "status": "error",
            "reason": "missing_base_margin_of_safety",
            "next_action": "done",
            "asof": asof,
            "baseline_report_dir": report_dir.name,
            "report_path": str(report_path),
            "valuation_outputs_path": str(outputs_path),
        }

    verdict_raw = _extract_report_verdict(report_path)
    verdict_normalized = _normalize_verdict(verdict_raw)

    stop_gate = _extract_report_stop_gate(report_path)

    promising = base_mos >= mos_threshold and verdict_normalized != "avoid"
    followup_focus = "falsification"
    confidence_gate_passed: bool | None = None

    if followup_mode == "confidence-gate":
        if stop_gate is None:
            if verdict_normalized == "avoid":
                next_action = "done"
                reason = "report_verdict_avoid"
            else:
                next_action = "run_research"
                reason = "missing_research_stop_gate"
            followup_focus = "highest-impact-unresolved-lever"
            confidence_gate_passed = False
        else:
            research_complete = stop_gate.get("research_complete")
            diminishing_returns = stop_gate.get("diminishing_returns")
            open_critical = stop_gate.get("open_thesis_critical_levers")
            confidence_pct = stop_gate.get("thesis_confidence_pct")
            confidence_required_pct = confidence_threshold * 100.0

            confidence_ok = (
                confidence_pct is None or confidence_pct >= confidence_required_pct
            )
            open_critical_ok = open_critical is None or open_critical == 0
            diminishing_ok = diminishing_returns is True or diminishing_returns is None

            confidence_gate_passed = bool(
                research_complete is True
                and confidence_ok
                and open_critical_ok
                and diminishing_ok
            )

            if confidence_gate_passed:
                next_action = "done"
                reason = "research_confidence_gate_passed"
            elif verdict_normalized == "avoid" and research_complete is True:
                next_action = "done"
                reason = "report_verdict_avoid"
            else:
                next_action = "run_research"
                reason = "research_confidence_gate_not_met"

            followup_focus = (
                str(stop_gate.get("next_best_research_focus") or "").strip()
                or "highest-impact-unresolved-lever"
            )
    else:
        if promising:
            next_action = "run_research"
            reason = "promising_report_requires_followup_research"
        elif verdict_normalized == "avoid":
            next_action = "done"
            reason = "report_verdict_avoid"
        else:
            next_action = "done"
            reason = "base_margin_of_safety_below_threshold"

    result = {
        "status": "ok",
        "reason": reason,
        "next_action": next_action,
        "asof": asof,
        "baseline_report_dir": report_dir.name,
        "report_path": str(report_path),
        "valuation_outputs_path": str(outputs_path),
        "base_margin_of_safety": base_mos,
        "followup_mode": followup_mode,
        "followup_confidence_threshold": confidence_threshold,
        "followup_mos_threshold": mos_threshold,
        "report_verdict": verdict_raw,
        "report_verdict_normalized": verdict_normalized,
        "promising": promising,
        "followup_focus": followup_focus,
        "research_stop_gate_found": stop_gate is not None,
        "confidence_gate_passed": confidence_gate_passed,
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
    companies_dir = base_dir / "companies"
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
    return base_dir / "companies" / country_dir / ticker


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
            "No company available in idea-screens/company-ideas-log.jsonl. "
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
            mos_threshold=args.followup_mos_threshold,
            followup_mode=args.followup_mode,
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
