#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_RELATIVE_PATH = Path("preferences") / "user_preferences.json"
CLEAR_TOKENS = {"none", "clear", "-"}


def default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "companies").exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


def default_preferences() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "updated_at_utc": None,
        "markets": {"included_countries": []},
        "sector_and_industry_preferences": {
            "preferred_sectors": [],
            "preferred_industries": [],
            "excluded_sectors": [],
            "excluded_industries": [],
            "notes": "",
        },
        "investment_strategy_preferences": {
            "preferred_strategies": [],
            "excluded_strategies": [],
            "notes": "",
        },
        "report_preferences": {
            "must_include": [],
            "nice_to_have": [],
            "exclude": [],
            "notes": "",
        },
    }


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _string_list(value: Any) -> list[str]:
    raw_items: list[str] = []
    if value is None:
        return []
    if isinstance(value, list):
        for item in value:
            if item is None:
                continue
            raw_items.append(str(item))
    elif isinstance(value, str):
        raw_items.append(value)
    else:
        raw_items.append(str(value))

    split_items: list[str] = []
    for item in raw_items:
        split_items.extend(re.split(r"[,\n;]+", item))

    cleaned = [piece.strip() for piece in split_items if piece and piece.strip()]
    return _dedupe(cleaned)


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def normalize_preferences(payload: dict[str, Any]) -> dict[str, Any]:
    defaults = default_preferences()
    merged = _deep_merge(defaults, payload)

    markets = merged.get("markets", {}) if isinstance(merged.get("markets"), dict) else {}
    sector = (
        merged.get("sector_and_industry_preferences", {})
        if isinstance(merged.get("sector_and_industry_preferences"), dict)
        else {}
    )
    strategy = (
        merged.get("investment_strategy_preferences", {})
        if isinstance(merged.get("investment_strategy_preferences"), dict)
        else {}
    )
    report = (
        merged.get("report_preferences", {})
        if isinstance(merged.get("report_preferences"), dict)
        else {}
    )

    normalized = default_preferences()
    try:
        schema_version = int(merged.get("schema_version", 1))
    except (TypeError, ValueError):
        schema_version = 1
    normalized["schema_version"] = max(schema_version, 1)
    normalized["updated_at_utc"] = merged.get("updated_at_utc")
    normalized["markets"]["included_countries"] = _string_list(markets.get("included_countries"))

    normalized["sector_and_industry_preferences"]["preferred_sectors"] = _string_list(
        sector.get("preferred_sectors")
    )
    normalized["sector_and_industry_preferences"]["preferred_industries"] = _string_list(
        sector.get("preferred_industries")
    )
    normalized["sector_and_industry_preferences"]["excluded_sectors"] = _string_list(
        sector.get("excluded_sectors")
    )
    normalized["sector_and_industry_preferences"]["excluded_industries"] = _string_list(
        sector.get("excluded_industries")
    )
    normalized["sector_and_industry_preferences"]["notes"] = _clean_text(sector.get("notes"))

    normalized["investment_strategy_preferences"]["preferred_strategies"] = _string_list(
        strategy.get("preferred_strategies")
    )
    normalized["investment_strategy_preferences"]["excluded_strategies"] = _string_list(
        strategy.get("excluded_strategies")
    )
    normalized["investment_strategy_preferences"]["notes"] = _clean_text(strategy.get("notes"))

    normalized["report_preferences"]["must_include"] = _string_list(report.get("must_include"))
    normalized["report_preferences"]["nice_to_have"] = _string_list(report.get("nice_to_have"))
    normalized["report_preferences"]["exclude"] = _string_list(report.get("exclude"))
    normalized["report_preferences"]["notes"] = _clean_text(report.get("notes"))
    return normalized


def _resolve_path(base_dir: Path, path_arg: str | None) -> Path:
    if not path_arg:
        return base_dir / DEFAULT_RELATIVE_PATH
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return base_dir / path


def _load_existing(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_preferences()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Preferences JSON must be an object: {path}")
    return normalize_preferences(payload)


def _save(path: Path, preferences: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(preferences, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _render_list(values: list[str]) -> str:
    if not values:
        return "(none)"
    return ", ".join(values)


def _prompt_list(label: str, current: list[str]) -> list[str]:
    print(f"\n{label}")
    print(f"Current: {_render_list(current)}")
    raw = input("Enter comma-separated values (`none` to clear, Enter to keep current): ").strip()
    if not raw:
        return current
    if raw.lower() in CLEAR_TOKENS:
        return []
    return _string_list(raw)


def _prompt_text(label: str, current: str) -> str:
    print(f"\n{label}")
    print(f"Current: {current or '(none)'}")
    raw = input("Enter text (`none` to clear, Enter to keep current): ").strip()
    if not raw:
        return current
    if raw.lower() in CLEAR_TOKENS:
        return ""
    return raw


def run_interactive(path: Path) -> int:
    current = _load_existing(path)
    print(f"Updating preferences at: {path}")
    print("Answer each prompt. Press Enter to keep existing values.")

    markets = current["markets"]
    sector = current["sector_and_industry_preferences"]
    strategy = current["investment_strategy_preferences"]
    report = current["report_preferences"]

    markets["included_countries"] = _prompt_list(
        "Which country markets are you interested in?",
        markets["included_countries"],
    )

    sector["preferred_sectors"] = _prompt_list(
        "Which sectors should be prioritized?",
        sector["preferred_sectors"],
    )
    sector["preferred_industries"] = _prompt_list(
        "Which industries should be prioritized?",
        sector["preferred_industries"],
    )
    sector["excluded_sectors"] = _prompt_list(
        "Which sectors should be excluded?",
        sector["excluded_sectors"],
    )
    sector["excluded_industries"] = _prompt_list(
        "Which industries should be excluded?",
        sector["excluded_industries"],
    )
    sector["notes"] = _prompt_text(
        "Any additional notes for sector/industry preferences?",
        sector["notes"],
    )

    strategy["preferred_strategies"] = _prompt_list(
        "Preferred investment strategy styles? (for example: value long, sum of the parts)",
        strategy["preferred_strategies"],
    )
    strategy["excluded_strategies"] = _prompt_list(
        "Any strategy styles to avoid?",
        strategy["excluded_strategies"],
    )
    strategy["notes"] = _prompt_text(
        "Any additional strategy notes?",
        strategy["notes"],
    )

    report["must_include"] = _prompt_list(
        "What information must always be in reports?",
        report["must_include"],
    )
    report["nice_to_have"] = _prompt_list(
        "What information is nice to have in reports?",
        report["nice_to_have"],
    )
    report["exclude"] = _prompt_list(
        "What information should be excluded or minimized in reports?",
        report["exclude"],
    )
    report["notes"] = _prompt_text(
        "Any additional notes for report preferences?",
        report["notes"],
    )

    current["updated_at_utc"] = _timestamp()
    _save(path, normalize_preferences(current))
    print(f"\nSaved preferences to {path}")
    return 0


def _read_payload(payload_arg: str | None, payload_file: str | None) -> dict[str, Any]:
    if bool(payload_arg) == bool(payload_file):
        raise SystemExit("Provide exactly one of --payload or --payload-file.")

    raw = payload_arg
    if payload_file:
        raw = Path(payload_file).read_text(encoding="utf-8")
    if raw is None:
        raise SystemExit("No payload provided.")

    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise SystemExit("Payload JSON must be an object.")
    return payload


def run_apply(path: Path, payload_arg: str | None, payload_file: str | None) -> int:
    patch = _read_payload(payload_arg=payload_arg, payload_file=payload_file)
    current = _load_existing(path)
    merged = _deep_merge(current, patch)
    normalized = normalize_preferences(merged)
    normalized["updated_at_utc"] = _timestamp()
    _save(path, normalized)
    print(f"Saved preferences to {path}")
    return 0


def run_show(path: Path) -> int:
    current = _load_existing(path)
    print(json.dumps(current, indent=2, ensure_ascii=True))
    return 0


def run_init(path: Path, force: bool) -> int:
    if path.exists() and not force:
        print(f"Preferences file already exists: {path}")
        return 0
    base = default_preferences()
    base["updated_at_utc"] = _timestamp()
    _save(path, base)
    print(f"Initialized preferences file at {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create/update persistent user preferences.")
    parser.add_argument("--base-dir", default=str(default_base_dir()))
    parser.add_argument(
        "--path",
        help="Preferences path relative to --base-dir (default: preferences/user_preferences.json).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("interactive", help="Run interactive terminal prompts and save preferences.")
    subparsers.add_parser("show", help="Print current normalized preferences JSON.")

    init_parser = subparsers.add_parser("init", help="Create default preferences file.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing file if present.")

    apply_parser = subparsers.add_parser(
        "apply",
        help="Apply a partial/full JSON payload into the preferences file.",
    )
    apply_parser.add_argument("--payload", help="Inline JSON payload.")
    apply_parser.add_argument("--payload-file", help="Path to a JSON payload file.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    base_dir = Path(args.base_dir).resolve()
    path = _resolve_path(base_dir=base_dir, path_arg=args.path)

    if args.command == "interactive":
        return run_interactive(path)
    if args.command == "show":
        return run_show(path)
    if args.command == "init":
        return run_init(path, force=bool(args.force))
    if args.command == "apply":
        return run_apply(path, payload_arg=args.payload, payload_file=args.payload_file)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
