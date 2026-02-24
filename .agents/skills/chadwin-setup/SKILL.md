---
name: chadwin-setup
description: "Chadwin setup control plane: install/update core skills, bootstrap app `.venv`/`.env`, and validate shared `<DATA_ROOT>` primitives."
---

# Chadwin Setup

## Overview
Run this skill first on a new machine or worktree.

This skill is the setup control plane. It owns:
- core skill manifest (`assets/skills.lock.json`) in this bundled skill directory
- app workspace self-update (git clones fast-forward; downloaded copies initialize `.git` + align to official remote)
- install/update/check of core external skills for Codex and Claude runtime targets
- project skill mirror sync from `.agents/skills/` to `.claude/skills/`
- app `.venv` bootstrap
- optional EDGAR identity upsert into app `.env`
- shared `<DATA_ROOT>` primitive creation and contract validation

Bundled required skills (`chadwin-setup`, `chadwin-preferences`) are shipped in `.agents/skills/` and are not installed from the external manifest.

This skill creates only shared primitives and does not create company-specific data packages.

`<DATA_ROOT>` resolution:
- `CHADWIN_DATA_DIR` when set
- otherwise OS app-data default:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

## Shared Contract Guardrails
- Create only shared primitives from this skill: `<DATA_ROOT>/`, `<DATA_ROOT>/user_preferences.json`, `<DATA_ROOT>/idea-screens/`, `<DATA_ROOT>/companies/`.
- Do not create company-specific `data/` or `reports/` packages in this setup step.
- Do not rename or repurpose shared primitive paths.
- Keep setup policy in this skill; do not duplicate installer logic in app repos.
- Treat preference schema/content as owned by `chadwin-preferences`; setup only bootstraps the file from that skill's canonical template.

## Setup Entrypoint
From app repo root:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

## Core Manifest
`.agents/skills/chadwin-setup/assets/skills.lock.json` defines distributed core external skills.

Rules:
- use pinned tags or commit SHAs for default operation
- do not use floating refs for release/default pins
- list external skills only (do not include bundled skills from `.agents/skills/`)

## Command Reference
Default install/update using locked refs:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

Install/check target control:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target both
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target codex
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target claude
```

Optional runtime directory overrides:

```bash
export CHADWIN_CODEX_SKILLS_DIR="$HOME/.codex/skills"
export CHADWIN_CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
```

Dry run:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --dry-run
```

Skip app workspace self-update:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --skip-self-update
```

Check installed core skills against locked refs:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check
```

Check against latest default-branch tips:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check --latest
```

Install/update using latest default-branch tips:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --latest
```

Write/update EDGAR identity in app `.env`:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --edgar-identity "Full Name <email@example.com>"
```

## Output
Creates/ensures:
- app `.venv`
- core external skills under selected runtime targets
- project-local `.claude/skills/*` mirrors for bundled skills
- `<DATA_ROOT>/`
- `<DATA_ROOT>/user_preferences.json`
- `<DATA_ROOT>/idea-screens/`
- `<DATA_ROOT>/companies/`
