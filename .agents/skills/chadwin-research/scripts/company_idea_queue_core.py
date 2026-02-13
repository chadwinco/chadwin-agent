from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG_RELATIVE_PATH = Path("idea-screens") / "company-ideas-log.jsonl"
DEFAULT_PREFERENCES_RELATIVE_PATH = Path("user_preferences.json")

TASK_FETCH_US = "fetch-us-company-data"
TASK_FETCH_NON_US = "non-us"
TASK_RESEARCH = "run-llm-workflow"
TASK_VALUES = {TASK_FETCH_US, TASK_FETCH_NON_US, TASK_RESEARCH}
COUNTRY_DIR_BY_MARKET = {"us": "US", "non-us": "International"}


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


def resolve_preferences_path(
    base_dir: Path, preferences_path: str | Path | None = None
) -> Path:
    if preferences_path is None:
        return base_dir / DEFAULT_PREFERENCES_RELATIVE_PATH
    path = Path(preferences_path)
    if path.is_absolute():
        return path
    return base_dir / path


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        values = value
    else:
        values = [value]

    items: list[str] = []
    for raw in values:
        if raw is None:
            continue
        text = str(raw)
        for piece in text.replace(";", ",").replace("\n", ",").split(","):
            cleaned = piece.strip()
            if cleaned:
                items.append(cleaned)
    return items


def _normalized_token_set(value: Any) -> set[str]:
    return {item.lower() for item in _string_list(value)}


def _normalize_taxonomy_text(value: Any) -> str:
    text = _clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = " ".join(text.split())
    return text


def _taxonomy_matches(candidate: str, preference: str) -> bool:
    candidate_norm = _normalize_taxonomy_text(candidate)
    preference_norm = _normalize_taxonomy_text(preference)
    if not candidate_norm or not preference_norm:
        return False

    if candidate_norm == preference_norm:
        return True

    # Support concise user preference labels (for example: biotech -> biotechnology).
    if preference_norm in candidate_norm or candidate_norm in preference_norm:
        return True

    candidate_tokens = set(candidate_norm.split())
    preference_tokens = set(preference_norm.split())
    if candidate_tokens & preference_tokens:
        return True

    def _stem(token: str) -> str:
        if len(token) > 5 and token.endswith("ies"):
            return token[:-3] + "y"
        if len(token) > 5 and token.endswith("ing"):
            return token[:-3]
        if len(token) > 4 and token.endswith("es"):
            return token[:-2]
        if len(token) > 4 and token.endswith("s"):
            return token[:-1]
        return token

    candidate_stems = {_stem(token) for token in candidate_tokens}
    preference_stems = {_stem(token) for token in preference_tokens}
    if candidate_stems & preference_stems:
        return True
    return False


def _matches_any_taxonomy_preference(candidate: str, preferences: set[str]) -> bool:
    candidate_norm = _normalize_taxonomy_text(candidate)
    if not candidate_norm:
        return False
    for raw_preference in preferences:
        if _taxonomy_matches(candidate_norm, raw_preference):
            return True
    return False


def normalize_ticker(value: Any) -> str:
    return _clean_text(value).upper()


def normalize_task(task: str) -> str:
    normalized = _clean_text(task).lower()
    if normalized not in TASK_VALUES:
        raise ValueError(f"Unsupported task: {task}")
    return normalized


def normalize_market(value: Any) -> str | None:
    normalized = _clean_text(value).lower()
    if not normalized:
        return None
    if normalized in {"us", "usa", "united states"}:
        return "us"
    if normalized in {"non-us", "non us", "non_us", "international"}:
        return "non-us"
    return None


def load_user_preferences(
    *,
    base_dir: Path,
    preferences_path: str | Path | None = None,
) -> dict[str, Any]:
    path = resolve_preferences_path(base_dir=base_dir, preferences_path=preferences_path)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def preferred_markets(preferences: dict[str, Any] | None) -> set[str]:
    if not isinstance(preferences, dict):
        return set()
    markets = preferences.get("markets")
    if not isinstance(markets, dict):
        return set()

    selected: set[str] = set()
    for country in _string_list(markets.get("included_countries")):
        normalized = normalize_market(country)
        if normalized in {"us", "non-us"}:
            selected.add(normalized)
    return selected


def market_is_allowed(market: Any, preferences: dict[str, Any] | None) -> bool:
    selected = preferred_markets(preferences)
    if not selected:
        return True
    normalized = normalize_market(market)
    if normalized is None:
        return True
    return normalized in selected


def matches_sector_industry_preferences(
    candidate: dict[str, Any], preferences: dict[str, Any] | None
) -> bool:
    if not isinstance(preferences, dict):
        return True
    block = preferences.get("sector_and_industry_preferences")
    if not isinstance(block, dict):
        return True

    preferred_sectors = _normalized_token_set(block.get("preferred_sectors"))
    preferred_industries = _normalized_token_set(block.get("preferred_industries"))
    excluded_sectors = _normalized_token_set(block.get("excluded_sectors"))
    excluded_industries = _normalized_token_set(block.get("excluded_industries"))

    sector = _clean_text(candidate.get("sector")).lower()
    industry = _clean_text(candidate.get("industry")).lower()

    if sector and _matches_any_taxonomy_preference(sector, excluded_sectors):
        return False
    if industry and _matches_any_taxonomy_preference(industry, excluded_industries):
        return False
    if preferred_sectors and sector and not _matches_any_taxonomy_preference(
        sector, preferred_sectors
    ):
        return False
    if preferred_industries and industry and not _matches_any_taxonomy_preference(
        industry, preferred_industries
    ):
        return False
    return True


def _non_us_numeric_root_code(ticker: str) -> str | None:
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
    numeric_code = _non_us_numeric_root_code(normalized)
    if numeric_code:
        return f"NONUS:{numeric_code}"
    return f"GEN:{normalized}"


def detect_market(ticker: Any, exchange: Any = None) -> str | None:
    normalized_ticker = normalize_ticker(ticker)
    normalized_exchange = _clean_text(exchange).upper()
    if normalized_exchange in {"NASDAQ", "NYSE", "AMEX"}:
        return "us"
    if normalized_exchange:
        return "non-us"
    if _non_us_numeric_root_code(normalized_ticker):
        return "non-us"
    if normalized_ticker:
        candidate = normalized_ticker.replace(".", "").replace("-", "")
        if candidate.isdigit():
            return "non-us"
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
        payload["sector"] = _clean_text(payload.get("sector"))
        payload["industry"] = _clean_text(payload.get("industry"))
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
            "sector": _clean_text(idea.get("sector")),
            "industry": _clean_text(idea.get("industry")),
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
    if normalized_task == TASK_FETCH_NON_US:
        return "non-us"
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
            companies_dir / "International" / normalized_ticker / "data",
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
    preferences_path: str | Path | None = None,
    respect_preferences: bool = True,
) -> dict[str, Any] | None:
    normalized_task = normalize_task(task)
    entries = read_queue_entries(base_dir, ideas_log)
    required_market = _task_market(normalized_task)
    preferences = (
        load_user_preferences(base_dir=base_dir, preferences_path=preferences_path)
        if respect_preferences
        else {}
    )

    candidates = [
        entry
        for entry in entries
        if required_market is None or entry.get("market") == required_market
    ]
    if respect_preferences:
        candidates = [
            entry
            for entry in candidates
            if market_is_allowed(entry.get("market"), preferences)
            and matches_sector_industry_preferences(entry, preferences)
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
