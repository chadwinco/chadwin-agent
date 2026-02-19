#!/usr/bin/env python3
"""Fetch possible US stock investment ideas using a value + quality screen."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

SKILLS_DIR_ENV_VAR = "CHADWIN_SKILLS_DIR"


def _resolve_queue_scripts_dir() -> Path:
    candidates: list[Path] = []

    configured = os.getenv(SKILLS_DIR_ENV_VAR, "").strip()
    if configured:
        configured_path = Path(configured).expanduser()
        if not configured_path.is_absolute():
            configured_path = (Path.cwd() / configured_path).resolve()
        candidates.append(configured_path / "chadwin-research" / "scripts")

    codex_home = os.getenv("CODEX_HOME", "").strip()
    if codex_home:
        candidates.append(Path(codex_home).expanduser() / "skills" / "chadwin-research" / "scripts")

    # Sibling-skill fallback when this skill is installed into a skills root.
    candidates.append(Path(__file__).resolve().parents[2] / "chadwin-research" / "scripts")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    checked = ", ".join(str(path) for path in candidates)
    raise RuntimeError(
        "Unable to locate chadwin-research queue scripts. "
        f"Checked: {checked}. Set {SKILLS_DIR_ENV_VAR} when skills are installed elsewhere."
    )


QUEUE_SCRIPTS = _resolve_queue_scripts_dir()
if str(QUEUE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(QUEUE_SCRIPTS))

from company_idea_queue import append_new_ideas, default_base_dir  # noqa: E402
from company_idea_queue_core import (  # noqa: E402
    load_user_preferences,
    market_is_allowed,
    matches_sector_industry_preferences,
    resolve_preferences_path,
)

FINVIZ_BASE_URL = "https://finviz.com/screener.ashx"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)

EXCHANGES = {
    "NASDAQ": "exch_nasd",
    "NYSE": "exch_nyse",
    "AMEX": "exch_amex",
}

BASE_FILTERS = [
    "geo_usa",
    "ind_stocksonly",
    "cap_midover",
    "fa_pe_u25",
    "fa_roe_o15",
    "fa_debteq_u1",
    "fa_netmargin_o10",
    "sh_price_o5",
    "sh_avgvol_o200",
]

VIEWS = (111, 121, 161)
ROWS_PER_PAGE = 20


def repo_scoped_path(path: Path, base_dir: Path) -> str:
    base = base_dir.resolve()
    candidate = path if path.is_absolute() else (base / path)
    resolved_candidate = candidate.resolve()
    try:
        relative = resolved_candidate.relative_to(base)
    except ValueError:
        return str(candidate)

    relative_text = relative.as_posix()
    if not relative_text or relative_text == ".":
        return base.name
    return f"{base.name}/{relative_text}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Screen US exchange-listed stocks and emit a structured list of "
            "possible value + quality ideas."
        )
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of ideas to return.",
    )
    parser.add_argument(
        "--max-pages-per-exchange",
        type=int,
        default=4,
        help="How many screener pages to scan for each US exchange.",
    )
    parser.add_argument(
        "--min-market-cap-b",
        type=float,
        default=2.0,
        help="Minimum market cap in USD billions.",
    )
    parser.add_argument(
        "--max-pe",
        type=float,
        default=25.0,
        help="Maximum trailing P/E ratio.",
    )
    parser.add_argument(
        "--min-roe",
        type=float,
        default=15.0,
        help="Minimum return on equity (percent).",
    )
    parser.add_argument(
        "--min-roic",
        type=float,
        default=10.0,
        help="Minimum return on invested capital (percent).",
    )
    parser.add_argument(
        "--min-operating-margin",
        type=float,
        default=10.0,
        help="Minimum operating margin (percent).",
    )
    parser.add_argument(
        "--min-profit-margin",
        type=float,
        default=10.0,
        help="Minimum net profit margin (percent).",
    )
    parser.add_argument(
        "--max-debt-to-equity",
        type=float,
        default=1.0,
        help="Maximum debt-to-equity ratio.",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=0.2,
        help="Delay between HTTP requests to reduce rate-limit risk.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output JSON file path. Print to stdout when omitted.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON (no indentation).",
    )
    parser.add_argument(
        "--base-dir",
        default=str(default_base_dir()),
        help=(
            "Repository root used for screener result queue paths "
            "(default: auto-detected)."
        ),
    )
    parser.add_argument(
        "--ideas-log",
        help=(
            "Override screener results path "
            "(file or directory; defaults to <DATA_ROOT>/idea-screens/**/screener-results.jsonl)."
        ),
    )
    parser.add_argument(
        "--preferences-path",
        help="Override preferences path (default: <DATA_ROOT>/user_preferences.json).",
    )
    parser.add_argument(
        "--ignore-preferences",
        action="store_true",
        help="Ignore preference-based filters and market guardrails.",
    )
    args = parser.parse_args()

    if args.limit <= 0:
        parser.error("--limit must be greater than 0.")
    if args.max_pages_per_exchange <= 0:
        parser.error("--max-pages-per-exchange must be greater than 0.")
    if args.min_market_cap_b < 0:
        parser.error("--min-market-cap-b cannot be negative.")
    if args.max_pe <= 0:
        parser.error("--max-pe must be greater than 0.")
    if args.max_debt_to_equity <= 0:
        parser.error("--max-debt-to-equity must be greater than 0.")
    if args.request_delay < 0:
        parser.error("--request-delay cannot be negative.")

    return args


def _request(url: str, delay_seconds: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="ignore")
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    return body


def _build_url(view: int, exchange_filter: str, start_row: int) -> str:
    filters = ",".join([exchange_filter, *BASE_FILTERS])
    params = urllib.parse.urlencode(
        {
            "v": str(view),
            "ft": "4",
            "o": "-marketcap",
            "f": filters,
            "r": str(start_row),
        }
    )
    return f"{FINVIZ_BASE_URL}?{params}"


def _parse_table_rows(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    table = None
    for candidate in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True) for th in candidate.find_all("th")]
        if "No." in headers and "Ticker" in headers:
            table = candidate
            break

    if table is None:
        return []

    headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]
    parsed: list[dict[str, str]] = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != len(headers):
            continue
        if not cells[0].get_text(strip=True).isdigit():
            continue
        values = [cell.get_text(" ", strip=True) for cell in cells]
        parsed.append(dict(zip(headers, values)))
    return parsed


def fetch_view_rows(
    *,
    view: int,
    exchange_filter: str,
    start_row: int,
    delay_seconds: float,
) -> list[dict[str, str]]:
    url = _build_url(view=view, exchange_filter=exchange_filter, start_row=start_row)
    return _parse_table_rows(_request(url=url, delay_seconds=delay_seconds))


def parse_percent(value: str | None) -> float | None:
    if value is None or value in {"", "-"}:
        return None
    try:
        return float(value.replace("%", "").replace(",", ""))
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None or value in {"", "-"}:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def parse_market_cap(value: str | None) -> float | None:
    if value is None or value in {"", "-"}:
        return None
    cleaned = value.replace(",", "").upper()
    scale = 1.0
    if cleaned.endswith("T"):
        scale = 1_000_000_000_000.0
        cleaned = cleaned[:-1]
    elif cleaned.endswith("B"):
        scale = 1_000_000_000.0
        cleaned = cleaned[:-1]
    elif cleaned.endswith("M"):
        scale = 1_000_000.0
        cleaned = cleaned[:-1]
    elif cleaned.endswith("K"):
        scale = 1_000.0
        cleaned = cleaned[:-1]
    try:
        return float(cleaned) * scale
    except ValueError:
        return None


def as_pct_string(value: float | None) -> str:
    return f"{value:.1f}%" if value is not None else "n/a"


def as_ratio_string(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "n/a"


def as_multiple_string(value: float | None) -> str:
    return f"{value:.1f}x" if value is not None else "n/a"


def build_thesis(row: dict[str, Any]) -> str:
    pe = row["metrics"]["pe"]
    fwd_pe = row["metrics"]["forward_pe"]
    roe = row["metrics"]["roe_pct"]
    roic = row["metrics"]["roic_pct"]
    debt_to_equity = row["metrics"]["debt_to_equity"]
    operating_margin = row["metrics"]["operating_margin_pct"]

    value_part = (
        f"trades near {as_multiple_string(pe)} P/E "
        f"(forward {as_multiple_string(fwd_pe)})"
    )
    quality_part = (
        f"while generating ROE {as_pct_string(roe)}, "
        f"ROIC {as_pct_string(roic)}, "
        f"operating margin {as_pct_string(operating_margin)}"
    )
    leverage_part = f"and Debt/Equity {as_ratio_string(debt_to_equity)}"
    return f"Possible value-quality setup: {value_part} {quality_part} {leverage_part}."


def score_candidate(
    *,
    pe: float | None,
    fwd_pe: float | None,
    pb: float | None,
    roe: float | None,
    roic: float | None,
    operating_margin: float | None,
    profit_margin: float | None,
    debt_to_equity: float | None,
    eps_next_5y: float | None,
    max_pe: float,
    max_debt_to_equity: float,
) -> float:
    value_score = 0.0
    if pe and pe > 0:
        value_score += max(0.0, (max_pe - pe) / max_pe) * 40
    if fwd_pe and fwd_pe > 0:
        value_score += max(0.0, (max_pe - fwd_pe) / max_pe) * 20
    if pb and pb > 0:
        value_score += max(0.0, (6.0 - pb) / 6.0) * 10

    quality_score = 0.0
    if roe is not None:
        quality_score += min(roe / 30.0, 1.0) * 10
    if roic is not None:
        quality_score += min(roic / 25.0, 1.0) * 10
    if operating_margin is not None:
        quality_score += min(operating_margin / 25.0, 1.0) * 10
    if profit_margin is not None:
        quality_score += min(profit_margin / 20.0, 1.0) * 5
    if debt_to_equity is not None and max_debt_to_equity > 0:
        debt_component = max(0.0, 1.0 - (debt_to_equity / max_debt_to_equity))
        quality_score += min(debt_component, 1.0) * 5

    growth_score = 0.0
    if eps_next_5y is not None:
        growth_score = min(max(eps_next_5y, 0.0) / 15.0, 1.0) * 10

    return round(value_score + quality_score + growth_score, 2)


def merge_exchange_rows(
    *,
    exchange_name: str,
    exchange_filter: str,
    max_pages: int,
    delay_seconds: float,
) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for page in range(max_pages):
        start_row = 1 + (page * ROWS_PER_PAGE)
        page_rows: dict[int, list[dict[str, str]]] = {}
        for view in VIEWS:
            rows = fetch_view_rows(
                view=view,
                exchange_filter=exchange_filter,
                start_row=start_row,
                delay_seconds=delay_seconds,
            )
            page_rows[view] = rows

        min_count = min(len(rows) for rows in page_rows.values())
        if min_count == 0:
            break

        for view_rows in page_rows.values():
            for row in view_rows:
                ticker = row.get("Ticker")
                if not ticker:
                    continue
                slot = merged.setdefault(ticker, {"Ticker": ticker, "Exchange": exchange_name})
                slot.update(row)

        if min_count < ROWS_PER_PAGE:
            break
    return list(merged.values())


def select_ideas(
    raw_rows: list[dict[str, str]],
    args: argparse.Namespace,
    *,
    preferences: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    ideas: list[dict[str, Any]] = []
    min_market_cap = args.min_market_cap_b * 1_000_000_000.0

    for row in raw_rows:
        ticker = row.get("Ticker")
        if not ticker:
            continue

        market_cap = parse_market_cap(row.get("Market Cap"))
        pe = parse_float(row.get("P/E"))
        fwd_pe = parse_float(row.get("Fwd P/E"))
        pb = parse_float(row.get("P/B"))
        roe = parse_percent(row.get("ROE"))
        roic = parse_percent(row.get("ROIC"))
        operating_margin = parse_percent(row.get("Oper M"))
        profit_margin = parse_percent(row.get("Profit M"))
        debt_to_equity = parse_float(row.get("Debt/Eq"))
        eps_next_5y = parse_percent(row.get("EPS Next 5Y"))
        sector = row.get("Sector")
        industry = row.get("Industry")

        if market_cap is None or market_cap < min_market_cap:
            continue
        if pe is None or pe <= 0 or pe > args.max_pe:
            continue
        if roe is None or roe < args.min_roe:
            continue
        if roic is None or roic < args.min_roic:
            continue
        if operating_margin is None or operating_margin < args.min_operating_margin:
            continue
        if profit_margin is None or profit_margin < args.min_profit_margin:
            continue
        if debt_to_equity is None or debt_to_equity > args.max_debt_to_equity:
            continue
        if preferences and not matches_sector_industry_preferences(
            {"sector": sector, "industry": industry},
            preferences,
        ):
            continue

        score = score_candidate(
            pe=pe,
            fwd_pe=fwd_pe,
            pb=pb,
            roe=roe,
            roic=roic,
            operating_margin=operating_margin,
            profit_margin=profit_margin,
            debt_to_equity=debt_to_equity,
            eps_next_5y=eps_next_5y,
            max_pe=args.max_pe,
            max_debt_to_equity=args.max_debt_to_equity,
        )

        idea = {
            "ticker": ticker,
            "company": row.get("Company"),
            "exchange": row.get("Exchange"),
            "sector": sector,
            "industry": industry,
            "score": score,
            "thesis": "",
            "metrics": {
                "market_cap_usd": round(market_cap),
                "pe": pe,
                "forward_pe": fwd_pe,
                "price_to_book": pb,
                "roe_pct": roe,
                "roic_pct": roic,
                "operating_margin_pct": operating_margin,
                "profit_margin_pct": profit_margin,
                "debt_to_equity": debt_to_equity,
                "eps_next_5y_pct": eps_next_5y,
            },
        }
        idea["thesis"] = build_thesis(idea)
        ideas.append(idea)

    ideas.sort(key=lambda item: item["score"], reverse=True)
    return ideas[: args.limit]


def build_payload(
    ideas: list[dict[str, Any]],
    args: argparse.Namespace,
    *,
    preferences_applied: bool,
    preferences_path: str | None,
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "finviz_screener",
        "universe": {
            "country": "USA",
            "exchanges": list(EXCHANGES.keys()),
        },
        "filters": {
            "min_market_cap_b": args.min_market_cap_b,
            "max_pe": args.max_pe,
            "min_roe_pct": args.min_roe,
            "min_roic_pct": args.min_roic,
            "min_operating_margin_pct": args.min_operating_margin,
            "min_profit_margin_pct": args.min_profit_margin,
            "max_debt_to_equity": args.max_debt_to_equity,
            "max_pages_per_exchange": args.max_pages_per_exchange,
        },
        "preferences": {
            "applied": preferences_applied,
            "path": preferences_path,
        },
        "ideas": ideas,
    }


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir)
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

    raw_rows: list[dict[str, str]] = []
    for exchange_name, exchange_filter in EXCHANGES.items():
        raw_rows.extend(
            merge_exchange_rows(
                exchange_name=exchange_name,
                exchange_filter=exchange_filter,
                max_pages=args.max_pages_per_exchange,
                delay_seconds=args.request_delay,
            )
        )

    ideas = select_ideas(
        raw_rows,
        args,
        preferences=preferences if preferences_applied else None,
    )
    payload = build_payload(
        ideas,
        args,
        preferences_applied=preferences_applied,
        preferences_path=(
            repo_scoped_path(resolved_preferences_path, base_dir=base_dir)
            if preferences_applied
            else None
        ),
    )
    output_text = json.dumps(payload, indent=None if args.compact else 2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text + "\n", encoding="utf-8")
    else:
        print(output_text)

    append_new_ideas(
        base_dir=base_dir,
        ideas=ideas,
        source="fetch-us-investment-ideas",
        generated_at_utc=payload.get("generated_at_utc"),
        source_output=str(args.output) if args.output else "",
        ideas_log=args.ideas_log,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
