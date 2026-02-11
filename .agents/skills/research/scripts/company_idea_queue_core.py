from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG_RELATIVE_PATH = Path("idea-screens") / "company-ideas-log.jsonl"

TASK_FETCH_US = "fetch-us-company-data"
TASK_FETCH_JP = "fetch-japanese-company-data"
TASK_RESEARCH = "run-llm-workflow"
COUNTRY_DIR_BY_MARKET = {"us": "US", "jp": "Japan"}

TASK_ALIASES = {
    TASK_FETCH_US: TASK_FETCH_US,
    "fetch_us_company_data": TASK_FETCH_US,
    "us": TASK_FETCH_US,
    TASK_FETCH_JP: TASK_FETCH_JP,
    "fetch_japanese_company_data": TASK_FETCH_JP,
    "jp": TASK_FETCH_JP,
    "japan": TASK_FETCH_JP,
    TASK_RESEARCH: TASK_RESEARCH,
    "run-company-research": TASK_RESEARCH,
    "run_company_research": TASK_RESEARCH,
    "run_llm_workflow": TASK_RESEARCH,
    "research": TASK_RESEARCH,
}


def default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


def resolve_log_path(base_dir: Path, ideas_log: str | Path | None = None) -> Path:
    if ideas_log is None:
        return base_dir / DEFAULT_LOG_RELATIVE_PATH
    path = Path(ideas_log)
    if path.is_absolute():
        return path
    return base_dir / path


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_ticker(value: Any) -> str:
    return _clean_text(value).upper()


def normalize_task(task: str) -> str:
    normalized = TASK_ALIASES.get(_clean_text(task).lower())
    if not normalized:
        raise ValueError(f"Unsupported task: {task}")
    return normalized


def normalize_market(value: Any) -> str | None:
    normalized = _clean_text(value).lower()
    if not normalized:
        return None
    if normalized in {"us", "usa", "united states"}:
        return "us"
    if normalized in {"jp", "japan", "tse", "jpx"}:
        return "jp"
    return None


def _jp_root_code(ticker: str) -> str | None:
    normalized = normalize_ticker(ticker)
    root = normalized[:-2] if normalized.endswith(".T") else normalized
    if not root.isdigit():
        return None
    if len(root) == 4:
        return root
    if len(root) == 5 and root.endswith("0"):
        return root[:-1]
    return None


def queue_key(ticker: Any) -> str:
    normalized = normalize_ticker(ticker)
    jp_code = _jp_root_code(normalized)
    if jp_code:
        return f"JP:{jp_code}"
    return f"GEN:{normalized}"


def detect_market(ticker: Any, exchange: Any = None) -> str | None:
    normalized_ticker = normalize_ticker(ticker)
    normalized_exchange = _clean_text(exchange).upper()
    if normalized_exchange in {"NASDAQ", "NYSE", "AMEX"}:
        return "us"
    if normalized_exchange in {"TSE", "JPX", "TOKYO"}:
        return "jp"
    if _jp_root_code(normalized_ticker):
        return "jp"
    if normalized_ticker:
        candidate = normalized_ticker.replace(".", "").replace("-", "")
        if candidate.isalnum():
            return "us"
    return None


def read_queue_entries(base_dir: Path, ideas_log: str | Path | None = None) -> list[dict[str, Any]]:
    path = resolve_log_path(base_dir, ideas_log)
    if not path.exists():
        return []

    entries: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        ticker = normalize_ticker(payload.get("ticker"))
        if not ticker:
            continue

        payload["ticker"] = ticker
        payload["market"] = normalize_market(payload.get("market")) or detect_market(
            ticker=ticker,
            exchange=payload.get("exchange"),
        )
        entries.append(payload)
    return entries


def _write_queue_entries(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(entry, ensure_ascii=True) for entry in entries]
    content = "\n".join(lines)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def append_new_ideas(
    *,
    base_dir: Path,
    ideas: list[dict[str, Any]],
    source: str,
    generated_at_utc: str | None = None,
    source_output: str | None = None,
    ideas_log: str | Path | None = None,
) -> int:
    path = resolve_log_path(base_dir, ideas_log)
    entries = read_queue_entries(base_dir, ideas_log)
    existing_keys = {queue_key(entry.get("ticker")) for entry in entries}

    appended = 0
    queued_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for idea in ideas:
        ticker = normalize_ticker(idea.get("ticker"))
        if not ticker:
            continue

        key = queue_key(ticker)
        if key in existing_keys:
            continue

        market = normalize_market(idea.get("market")) or detect_market(
            ticker=ticker,
            exchange=idea.get("exchange"),
        )
        if market is None:
            continue

        entry = {
            "ticker": ticker,
            "company": _clean_text(idea.get("company")),
            "exchange": _clean_text(idea.get("exchange")),
            "market": market,
            "thesis": _clean_text(idea.get("thesis")),
            "source": _clean_text(source),
            "generated_at_utc": _clean_text(generated_at_utc),
            "queued_at_utc": queued_at,
            "source_output": _clean_text(source_output),
        }
        entries.append(entry)
        existing_keys.add(key)
        appended += 1

    if appended:
        _write_queue_entries(path, entries)
    elif not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    return appended


def _task_market(task: str) -> str | None:
    normalized_task = normalize_task(task)
    if normalized_task == TASK_FETCH_US:
        return "us"
    if normalized_task == TASK_FETCH_JP:
        return "jp"
    return None


def _company_data_exists(base_dir: Path, ticker: str, market: str | None = None) -> bool:
    companies_dir = base_dir / "companies"
    if not companies_dir.exists():
        return False

    normalized_ticker = normalize_ticker(ticker)
    normalized_market = normalize_market(market)
    candidates: list[Path] = []

    if normalized_market:
        country_dir = COUNTRY_DIR_BY_MARKET.get(normalized_market)
        if country_dir:
            candidates.append(companies_dir / country_dir / normalized_ticker / "data")

    candidates.extend(
        [
            companies_dir / "US" / normalized_ticker / "data",
            companies_dir / "Japan" / normalized_ticker / "data",
            companies_dir / normalized_ticker / "data",  # legacy flat layout fallback
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return True

    for entry in companies_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.upper() == normalized_ticker and (entry / "data").exists():
            return True
        for nested in entry.iterdir():
            if (
                nested.is_dir()
                and nested.name.upper() == normalized_ticker
                and (nested / "data").exists()
            ):
                return True
    return False


def pick_next_company(
    *,
    base_dir: Path,
    task: str,
    ideas_log: str | Path | None = None,
) -> dict[str, Any] | None:
    normalized_task = normalize_task(task)
    entries = read_queue_entries(base_dir, ideas_log)
    required_market = _task_market(normalized_task)

    candidates = [
        entry
        for entry in entries
        if required_market is None or entry.get("market") == required_market
    ]
    if not candidates:
        return None

    if normalized_task == TASK_RESEARCH:
        candidates_with_data = [
            entry
            for entry in candidates
            if _company_data_exists(base_dir, str(entry.get("ticker") or ""), entry.get("market"))
        ]
        if candidates_with_data:
            return candidates_with_data[0]

    return candidates[0]


def remove_company(
    *,
    base_dir: Path,
    ticker: str,
    ideas_log: str | Path | None = None,
) -> int:
    path = resolve_log_path(base_dir, ideas_log)
    if not path.exists():
        return 0

    entries = read_queue_entries(base_dir, ideas_log)
    target_key = queue_key(ticker)

    kept = [entry for entry in entries if queue_key(entry.get("ticker")) != target_key]
    removed_count = len(entries) - len(kept)
    if removed_count:
        _write_queue_entries(path, kept)
    return removed_count
