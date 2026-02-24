#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


APP_DATA_DIR_NAME = "Chadwin"
DATA_ROOT_ENV_VAR = "CHADWIN_DATA_DIR"
IDEA_SCREENS_SUBDIR = Path("idea-screens")
COMPANIES_SUBDIR = Path("companies")
PREFERENCES_PATH = Path("user_preferences.md")


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


def ensure_data_layout(data_root: Path) -> tuple[list[Path], list[Path]]:
    created_dirs: list[Path] = []
    for directory in (
        data_root,
        data_root / IDEA_SCREENS_SUBDIR,
        data_root / COMPANIES_SUBDIR,
    ):
        if directory.exists():
            continue
        directory.mkdir(parents=True, exist_ok=True)
        created_dirs.append(directory)

    created_files: list[Path] = []
    preferences_path = data_root / PREFERENCES_PATH
    # Setup only bootstraps missing preferences; preference semantics are owned elsewhere.
    if not preferences_path.exists():
        preferences_path.write_text("", encoding="utf-8")
        created_files.append(preferences_path)

    return created_dirs, created_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Chadwin data root and initialize shared data primitives."
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
