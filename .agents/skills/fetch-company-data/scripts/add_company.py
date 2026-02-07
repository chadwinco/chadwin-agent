#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_SRC = SKILL_DIR / "src"

if str(SKILL_SRC) not in sys.path:
    sys.path.insert(0, str(SKILL_SRC))

from add_company import main  # noqa: E402


if __name__ == "__main__":
    main()
