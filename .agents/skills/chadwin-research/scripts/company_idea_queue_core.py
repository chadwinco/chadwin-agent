from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_DATA_DIR_NAME = "Chadwin"
DATA_ROOT_ENV_VAR = "CHADWIN_DATA_DIR"
APP_ROOT_ENV_VAR = "CHADWIN_APP_ROOT"
REPO_MARKER_RELATIVE_PATH = Path(".agents") / "skills"
DEFAULT_COMPANIES_SUBPATH = Path("companies")
DEFAULT_IDEA_SCREENS_SUBPATH = Path("idea-screens")
SCREENER_RESULTS_FILENAME = "screener-results.jsonl"
DEFAULT_PREFERENCES_SUBPATH = Path("user_preferences.json")

TASK_FETCH_US = "fetch-us-company-data"
TASK_FETCH_NON_US = "non-us"
TASK_RESEARCH = "chadwin-research"
TASK_VALUES = {TASK_FETCH_US, TASK_FETCH_NON_US, TASK_RESEARCH}
COUNTRY_DIR_BY_MARKET = {"us": "US"}
ISO_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")


def _detect_repo_root(start: Path | None = None) -> Path:
    configured = os.getenv(APP_ROOT_ENV_VAR, "").strip()
    if configured:
        configured_path = Path(configured).expanduser()
        if not configured_path.is_absolute():
            configured_path = (Path.cwd() / configured_path).resolve()
        if configured_path.exists():
            return configured_path

    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in [candidate, *candidate.parents]:
        if (parent / REPO_MARKER_RELATIVE_PATH).exists():
            return parent
    return Path.cwd().resolve()


def _default_data_root() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_DATA_DIR_NAME
        return Path.home() / "AppData" / "Roaming" / APP_DATA_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DATA_DIR_NAME
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / APP_DATA_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DATA_DIR_NAME


def _resolve_data_root() -> Path:
    configured = os.getenv(DATA_ROOT_ENV_VAR, "").strip()
    if configured:
        path = Path(configured).expanduser()
        if path.is_absolute():
            return path
        return (Path.cwd() / path).resolve()
    return _default_data_root()


def default_base_dir() -> Path:
    return _detect_repo_root(Path(__file__).resolve())


def resolve_companies_root() -> Path:
    return _resolve_data_root() / DEFAULT_COMPANIES_SUBPATH


def resolve_idea_screens_root() -> Path:
    return _resolve_data_root() / DEFAULT_IDEA_SCREENS_SUBPATH


def _resolve_path(base_dir: Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path


def _looks_like_directory_override(path: Path) -> bool:
    return path.suffix == "" and path.name != SCREENER_RESULTS_FILENAME


def _default_screener_results_path(
    *,
    base_dir: Path,
    source_output: str | None = None,
) -> Path:
    resolved_source_output = _clean_text(source_output)
    if resolved_source_output:
        source_output_path = _resolve_path(base_dir, resolved_source_output)
        if source_output_path.suffix:
            return source_output_path.parent / source_output_path.stem / SCREENER_RESULTS_FILENAME
        return source_output_path / SCREENER_RESULTS_FILENAME

    date_dir = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return resolve_idea_screens_root() / date_dir / SCREENER_RESULTS_FILENAME


def resolve_log_path(
    base_dir: Path,
    ideas_log: str | Path | None = None,
    *,
    source_output: str | None = None,
) -> Path:
    if ideas_log is not None:
        path = _resolve_path(base_dir, ideas_log)
        if path.is_dir() or _looks_like_directory_override(path):
            return path / SCREENER_RESULTS_FILENAME
        return path
    return _default_screener_results_path(base_dir=base_dir, source_output=source_output)


def resolve_preferences_path(
    base_dir: Path, preferences_path: str | Path | None = None
) -> Path:
    if preferences_path is None:
        return _resolve_data_root() / DEFAULT_PREFERENCES_SUBPATH
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
    if normalized == "us":
        return "us"
    if normalized == "non-us":
        return "non-us"
    return None


def normalize_country_code(value: Any) -> str | None:
    normalized = _clean_text(value).upper()
    if not normalized:
        return None
    if ISO_COUNTRY_RE.match(normalized):
        return normalized
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


def preferred_countries(preferences: dict[str, Any] | None) -> set[str]:
    if not isinstance(preferences, dict):
        return set()
    markets = preferences.get("markets")
    if not isinstance(markets, dict):
        return set()

    selected: set[str] = set()
    for country in _string_list(markets.get("included_countries")):
        country_code = normalize_country_code(country)
        if country_code:
            selected.add(country_code)
    return selected


def market_is_allowed(
    market: Any,
    preferences: dict[str, Any] | None,
    exchange_country: Any = None,
) -> bool:
    selected_countries = preferred_countries(preferences)
    if not selected_countries:
        return True

    normalized = normalize_market(market)
    if normalized is None:
        return True

    if normalized == "us":
        return "US" in selected_countries

    allowed_non_us = {country for country in selected_countries if country != "US"}
    if not allowed_non_us:
        return False

    country_code = normalize_country_code(exchange_country)
    if country_code:
        return country_code in allowed_non_us

    # With explicit country preferences, unknown non-US country metadata does
    # not satisfy the filter.
    return False


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


def _path_sort_key(path: Path) -> tuple[float, str]:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return (mtime, str(path))


def _list_screener_results_paths(
    base_dir: Path,
    ideas_log: str | Path | None = None,
) -> list[Path]:
    if ideas_log is not None:
        path = _resolve_path(base_dir, ideas_log)
        if path.is_dir():
            paths = [candidate for candidate in path.rglob(SCREENER_RESULTS_FILENAME) if candidate.is_file()]
            paths.sort(key=_path_sort_key, reverse=True)
            return paths
        if path.is_file():
            return [path]
        return []

    idea_screens_root = resolve_idea_screens_root()
    if not idea_screens_root.exists():
        return []

    paths = [
        candidate
        for candidate in idea_screens_root.rglob(SCREENER_RESULTS_FILENAME)
        if candidate.is_file()
    ]
    paths.sort(key=_path_sort_key, reverse=True)
    return paths


def _normalize_queue_entry(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None

    ticker = normalize_ticker(payload.get("ticker"))
    if not ticker:
        return None

    normalized = dict(payload)
    normalized["ticker"] = ticker
    normalized["sector"] = _clean_text(payload.get("sector"))
    normalized["industry"] = _clean_text(payload.get("industry"))
    normalized["market"] = normalize_market(payload.get("market")) or detect_market(
        ticker=ticker,
        exchange=payload.get("exchange"),
    )
    normalized["exchange_country"] = normalize_country_code(payload.get("exchange_country"))
    if normalized["exchange_country"] is None and normalized["market"] == "us":
        normalized["exchange_country"] = "US"
    return normalized


def _read_entries_from_path(path: Path) -> list[dict[str, Any]]:
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
        normalized = _normalize_queue_entry(payload)
        if normalized:
            entries.append(normalized)
    return entries


def read_queue_entries(base_dir: Path, ideas_log: str | Path | None = None) -> list[dict[str, Any]]:
    paths = _list_screener_results_paths(base_dir, ideas_log)
    if not paths:
        return []

    entries: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for path in paths:
        for entry in _read_entries_from_path(path):
            key = queue_key(entry.get("ticker"))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            entries.append(entry)
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
    path = resolve_log_path(base_dir, ideas_log, source_output=source_output)
    all_entries = read_queue_entries(base_dir, ideas_log)
    existing_keys = {queue_key(entry.get("ticker")) for entry in all_entries}
    entries_for_target_path = _read_entries_from_path(path)

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

        exchange_country = normalize_country_code(idea.get("exchange_country"))
        if market == "us":
            exchange_country = "US"
        elif exchange_country == "US":
            exchange_country = None

        entry = {
            "ticker": ticker,
            "company": _clean_text(idea.get("company")),
            "exchange": _clean_text(idea.get("exchange")),
            "sector": _clean_text(idea.get("sector")),
            "industry": _clean_text(idea.get("industry")),
            "market": market,
            "exchange_country": exchange_country,
            "thesis": _clean_text(idea.get("thesis")),
            "source": _clean_text(source),
            "generated_at_utc": _clean_text(generated_at_utc),
            "queued_at_utc": queued_at,
            "source_output": _clean_text(source_output),
        }
        entries_for_target_path.append(entry)
        existing_keys.add(key)
        appended += 1

    if appended:
        _write_queue_entries(path, entries_for_target_path)
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


def _company_data_exists(
    ticker: str,
    market: str | None = None,
    exchange_country: str | None = None,
) -> bool:
    companies_dir = resolve_companies_root()
    if not companies_dir.exists():
        return False

    normalized_ticker = normalize_ticker(ticker)
    normalized_market = normalize_market(market)
    normalized_country = normalize_country_code(exchange_country)
    candidates: list[Path] = []

    if normalized_country:
        candidates.append(companies_dir / normalized_country / normalized_ticker / "data")
    elif normalized_market:
        country_dir = COUNTRY_DIR_BY_MARKET.get(normalized_market)
        if country_dir:
            candidates.append(companies_dir / country_dir / normalized_ticker / "data")

    for candidate in candidates:
        if candidate.exists():
            return True

    for country_dir in companies_dir.iterdir():
        if not country_dir.is_dir():
            continue
        canonical = country_dir / normalized_ticker / "data"
        if canonical.exists():
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
            if market_is_allowed(
                entry.get("market"),
                preferences,
                entry.get("exchange_country"),
            )
            and matches_sector_industry_preferences(entry, preferences)
        ]
    if not candidates:
        return None

    if normalized_task == TASK_RESEARCH:
        candidates_with_data = [
            entry
            for entry in candidates
            if _company_data_exists(
                str(entry.get("ticker") or ""),
                entry.get("market"),
                str(entry.get("exchange_country") or ""),
            )
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
    target_key = queue_key(ticker)
    if ideas_log is None:
        paths = _list_screener_results_paths(base_dir, None)
    else:
        resolved = _resolve_path(base_dir, ideas_log)
        if resolved.is_dir() or _looks_like_directory_override(resolved):
            paths = _list_screener_results_paths(base_dir, ideas_log)
        elif resolved.is_file():
            paths = [resolved]
        else:
            paths = []

    removed_count = 0
    for path in paths:
        entries = _read_entries_from_path(path)
        kept = [entry for entry in entries if queue_key(entry.get("ticker")) != target_key]
        removed = len(entries) - len(kept)
        if removed:
            _write_queue_entries(path, kept)
            removed_count += removed
    return removed_count
