from __future__ import annotations

import os
import sys
from pathlib import Path


APP_DATA_DIR_NAME = "Chadwin"
DATA_ROOT_ENV_VAR = "CHADWIN_DATA_DIR"
APP_ROOT_ENV_VAR = "CHADWIN_APP_ROOT"
REPO_MARKER_RELATIVE_PATH = Path(".agents") / "skills"


def _configured_app_root() -> Path | None:
    configured = os.getenv(APP_ROOT_ENV_VAR, "").strip()
    if not configured:
        return None
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path if path.exists() else None


def detect_repo_root(start: Path | None = None) -> Path:
    configured = _configured_app_root()
    if configured is not None:
        return configured

    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in [candidate, *candidate.parents]:
        if (parent / REPO_MARKER_RELATIVE_PATH).exists():
            return parent
    return Path.cwd().resolve()


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


def resolve_data_root() -> Path:
    configured = os.getenv(DATA_ROOT_ENV_VAR, "").strip()
    if configured:
        path = Path(configured).expanduser()
        if path.is_absolute():
            return path
        return (Path.cwd() / path).resolve()
    return default_data_root()
