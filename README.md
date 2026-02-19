# Chadwin Codex Research

This repository is a Codex-operated, skill-first equity research system.

The app repo is a thin control plane:
- bootstrap/install orchestration
- release-pinned skill manifest
- global operating contract and shared data contract docs

Operational skills are installed into Codex skill storage (`$CODEX_HOME/skills`, default `~/.codex/skills`), not kept as app-local runtime dependencies.

Agent operating contract and workflow rules are defined in `AGENTS.md`.
Shared data primitives and extension rules are defined in `DATA_CONTRACT.md`.

## One-Time Bootstrap
Run bootstrap from repo root:

```bash
python3 scripts/bootstrap_chadwin.py
```

If EDGAR identity is not already set in environment or `.env`, pass it explicitly:

```bash
python3 scripts/bootstrap_chadwin.py --edgar-identity "Your Name your.email@example.com"
```

Bootstrap responsibilities:
- ensure app `.venv` exists
- install/update required skills from `skills.lock.json` into `$CODEX_HOME/skills`
- install required Python packages declared by installed skills in `agents/openai.yaml`
- run installed `chadwin-setup` scripts for `<DATA_ROOT>` bootstrap + validation

Dry-run planning:

```bash
python3 scripts/bootstrap_chadwin.py --dry-run
```

## Skill Manifest
The canonical release contract is `skills.lock.json`.

It defines:
- required skills + pinned refs
- deprecated skills excluded from install

Current deprecated skills:
- `fetch-daily-sec-filings`
- `chart-valuation-ranges`

## Discover Installed Skills
List installed skills:

```bash
find "${CODEX_HOME:-$HOME/.codex}/skills" -mindepth 1 -maxdepth 1 -type d | sort
```

Read a skill workflow:

```bash
sed -n '1,220p' "${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/SKILL.md"
```

## Required Outputs Per Completed Research Run
For `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`, a run is complete only when these files exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`
