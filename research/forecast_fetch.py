from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SKILL_SRC = BASE_DIR / ".agents" / "skills" / "fetch-company-data" / "src"

if not SKILL_SRC.exists():
    raise ImportError(
        "Missing fetch-company-data skill source at "
        f"{SKILL_SRC}. Restore the skill directory before importing this module."
    )

if str(SKILL_SRC) not in sys.path:
    sys.path.insert(0, str(SKILL_SRC))

from fetch_company_data.forecast_fetch import *  # noqa: F401,F403,E402
