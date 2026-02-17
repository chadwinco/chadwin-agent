---
name: setup-chadwin-data
description: Initialize the Chadwin app-data root (`<DATA_ROOT>`) with minimum shared bootstrap artifacts only: root folder + `user_preferences.json`. Use once on a new machine/worktree.
---

# Setup Chadwin Data

## Overview
Run this skill to create only the minimal shared bootstrap under `<DATA_ROOT>`.
This skill intentionally does not create data folders owned by other skills.

`<DATA_ROOT>` resolution:
- `CHADWIN_DATA_DIR` when set
- otherwise OS app-data default:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

## Quick Start
Run from repo root:

```bash
.venv/bin/python .agents/skills/setup-chadwin-data/scripts/setup_chadwin_data_dirs.py
```

Print the resolved path without creating anything:

```bash
.venv/bin/python .agents/skills/setup-chadwin-data/scripts/setup_chadwin_data_dirs.py --print-only
```

## Inputs
- `--data-root` (optional): explicit override path
- `--print-only` (optional): dry resolution-only mode

## Output
Creates:
- `<DATA_ROOT>/`
- `<DATA_ROOT>/user_preferences.json` (canonical scaffold with empty preferences)

Each data-producing skill is responsible for creating and maintaining its own subdirectories/files under `<DATA_ROOT>`.
