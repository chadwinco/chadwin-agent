---
name: chadwin-setup
description: One-time setup entrypoint for Chadwin: bootstrap Python `.venv`, install skill dependencies, configure `.env`, and initialize the minimal shared `<DATA_ROOT>` artifacts.
---

# Chadwin Setup

## Overview
Run this skill first on a new machine or worktree.
It centralizes one-time setup and then performs the minimal shared `<DATA_ROOT>` bootstrap.

This skill intentionally does not create data folders owned by other skills.

`<DATA_ROOT>` resolution:
- `CHADWIN_DATA_DIR` when set
- otherwise OS app-data default:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

## One-Time Python Environment Setup
Run from repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
```

If `python3 -m venv .venv` fails with `No module named venv`, install Python venv support first:

```bash
# macOS (Homebrew; venv is included)
brew install python

# Debian/Ubuntu
sudo apt update && sudo apt install -y python3-venv

# Fedora/RHEL/CentOS
sudo dnf install -y python3

# Arch Linux
sudo pacman -S python
```

## Install Dependencies By Skill
Dependencies are owned by the skill that uses them.

For each skill you plan to run, install the packages listed in:
- `.agents/skills/<skill-name>/agents/openai.yaml` under `dependencies.python_packages`

## Configure Environment Variables
SEC/EDGAR skills require an identity string.

Use a repo-level `.env` file:

```bash
cp .env.example .env
```

Set:

```bash
EDGAR_IDENTITY="Your Name your.email@example.com"
```

## Bootstrap `<DATA_ROOT>`
Create the minimal shared bootstrap:

```bash
.venv/bin/python .agents/skills/chadwin-setup/scripts/setup_chadwin_data_dirs.py
```

Print the resolved data root without creating anything:

```bash
.venv/bin/python .agents/skills/chadwin-setup/scripts/setup_chadwin_data_dirs.py --print-only
```

## Inputs
- `--data-root` (optional): explicit override path
- `--print-only` (optional): dry resolution-only mode

## Output
Creates:
- `<DATA_ROOT>/`
- `<DATA_ROOT>/user_preferences.json` (canonical scaffold with empty preferences)

Each data-producing skill is responsible for creating and maintaining its own subdirectories/files under `<DATA_ROOT>`.
