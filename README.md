# Chadwin Codex Research

This repository is a skill-first, Codex-operated equity research system.

Deterministic code lives inside skills (`.agents/skills/*`) and is used as bounded helpers. The LLM agent remains responsible for workflow control, sanity checks, and final output quality.

Agent operating contract and workflow rules are defined in `AGENTS.md`.

## One-Time Setup
From repo root:

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

## Environment Variables
SEC/EDGAR skills require an identity string.

Use a repo-level `.env` file for shared skill configuration.

Template:

```bash
cp .env.example .env
```

Then set:

```bash
EDGAR_IDENTITY="Your Name your.email@example.com"
```

Data artifacts are written to `<DATA_ROOT>`:
- `CHADWIN_DATA_DIR` when set.
- Otherwise OS default app-data location:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

Repo-local `.chadwin-data` is no longer used.

Optional one-time bootstrap:

```bash
.venv/bin/python .agents/skills/setup-chadwin-data/scripts/setup_chadwin_data_dirs.py
```

This bootstrap is intentionally minimal:
- creates `<DATA_ROOT>/`
- initializes `<DATA_ROOT>/user_preferences.json`

Other skills create and manage their own data folders/files under `<DATA_ROOT>`.

## Discover and Use Skills
List available repo-local skills:

```bash
find .agents/skills -mindepth 1 -maxdepth 1 -type d | sort
```

For each skill you intend to run, read its workflow first:

```bash
sed -n '1,220p' .agents/skills/<skill-name>/SKILL.md
```

If an orchestrator skill is installed, use it for semi-autonomous runs. If not, compose manual runs from available lower-level skills (idea generation, data fetch, research/reporting, preferences).

## Required Outputs Per Completed Research Run
For `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`, a run is complete only when these files exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

## Repository Layout
- `.agents/skills/`: skill definitions, scripts, references, and assets
- `<DATA_ROOT>/idea-screens/`: queue and generated idea files
- `<DATA_ROOT>/user_preferences.json`: persistent preference profile
- `<DATA_ROOT>/improvement-log.md`: process improvement log
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/`: company evidence and reports
