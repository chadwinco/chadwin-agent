# Chadwin Codex Research

This repository is a Codex-operated, skill-first equity research system.

The app repo is a thin control plane:
- bootstrap/install orchestration
- release-pinned skill manifest
- global operating contract and shared data contract docs

Operational skills are installed into Codex skill storage (`$CODEX_HOME/skills`, default `~/.codex/skills`).

Agent operating contract and workflow rules are defined in `AGENTS.md`.

## Setup
- `scripts/chadwin_setup.py` (app repo control plane):
  - ensures `.venv` exists
  - installs/updates skills listed in `skills.lock.json` into `$CODEX_HOME/skills`
  - delegates shared `<DATA_ROOT>` bootstrap and contract validation to installed `chadwin-setup`
- `chadwin-setup` skill (skill repo runtime owner):
  - defines setup workflow and setup policy
  - owns shared primitive creation under `<DATA_ROOT>`
  - owns shared data-contract validation behavior

## One-Time Bootstrap
Run bootstrap from repo root:

```bash
python3 scripts/chadwin_setup.py
```

Default bootstrap mode uses locked refs from `skills.lock.json`.

If EDGAR identity is not already set in environment or `.env`, pass it explicitly:

```bash
python3 scripts/chadwin_setup.py --edgar-identity "Your Name your.email@example.com"
```

Bootstrap responsibilities:
- ensure app `.venv` exists
- install/update required skills from `skills.lock.json` into `$CODEX_HOME/skills`
- delegate to installed `chadwin-setup` scripts for `<DATA_ROOT>` bootstrap + validation

Inside Codex, if the user asks to start fresh (for example, "let's get started"), run `python3 scripts/chadwin_setup.py` first, then proceed with skill workflows.

Dry-run planning:

```bash
python3 scripts/chadwin_setup.py --dry-run
```

Install/update using latest default branch tip for each skill repo:

```bash
python3 scripts/chadwin_setup.py --latest
```

Check whether installed skills are aligned with locked refs:

```bash
python3 scripts/chadwin_setup.py --check
```

Check against latest default-branch tips:

```bash
python3 scripts/chadwin_setup.py --check --latest
```

## Skill Manifest
The release contract is `skills.lock.json`.

It defines:
- required skills + pinned refs
- full git clone sources per skill (URL, SSH, or filesystem path)
- deprecated skills excluded from install
