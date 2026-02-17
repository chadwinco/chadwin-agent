#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


APP_DATA_DIR_NAME = "Chadwin"
DATA_ROOT_ENV_VAR = "CHADWIN_DATA_DIR"


def default_data_root() -> Path:
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


def resolve_data_root(cli_data_root: str | None) -> Path:
    if cli_data_root:
        candidate = Path(cli_data_root).expanduser()
    else:
        configured = os.getenv(DATA_ROOT_ENV_VAR, "").strip()
        if configured:
            candidate = Path(configured).expanduser()
        else:
            return default_data_root()
    if candidate.is_absolute():
        return candidate
    return (Path.cwd() / candidate).resolve()


def default_preferences_payload() -> dict[str, Any]:
    return {
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
        "updated_at_utc": None,
    }


def ensure_data_layout(data_root: Path) -> tuple[list[Path], list[Path]]:
    created_dirs: list[Path] = []
    if not data_root.exists():
        data_root.mkdir(parents=True, exist_ok=True)
        created_dirs.append(data_root)

    preferences_path = data_root / "user_preferences.json"
    created_files: list[Path] = []
    if not preferences_path.exists():
        payload = default_preferences_payload()
        preferences_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        created_files.append(preferences_path)

    return created_dirs, created_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Chadwin data root and initialize user preferences."
    )
    parser.add_argument(
        "--data-root",
        help=(
            "Override data root. Defaults to CHADWIN_DATA_DIR when set, "
            "otherwise OS app-data Chadwin path."
        ),
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print resolved data root and exit without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = resolve_data_root(args.data_root)

    print(f"Data root: {data_root}")
    if args.print_only:
        return 0

    created_dirs, created_files = ensure_data_layout(data_root)
    print(f"Created directories: {len(created_dirs)}")
    for path in created_dirs:
        print(f"- {path}")
    print(f"Created files: {len(created_files)}")
    for path in created_files:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
