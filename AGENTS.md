# AGENTS.md

## Table of Contents
- [Project Purpose](#project-purpose)
- [Scope and Ownership](#scope-and-ownership)
- [Data Root Convention](#data-root-convention)
- [Shared Data Contract](#shared-data-contract)
- [Getting Started](#getting-started)
- [Setup Command Reference](#setup-command-reference)
- [Skill Freshness Policy](#skill-freshness-policy)
- [Core Skill Manifest](#core-skill-manifest)
- [General Ways of Working](#general-ways-of-working)
- [Completion and Validation](#completion-and-validation)

## Project Purpose
This repository is a local, LLM-operated equity research system.

Operating model:
- The LLM agent is the active operator.
- Deterministic code is used only for bounded steps where automation is materially better.
- The agent is accountable for end-to-end correctness, recovery, and output quality.

## Scope and Ownership
This file defines repository-level rules:
- shared data contract,
- top-level setup entrypoints,
- cross-skill operating behavior.

Setup ownership split:
- `chadwin-agent` bundles `chadwin-setup` at `.agents/skills/chadwin-setup`.
- `chadwin-agent` bundles `chadwin-preferences` at `.agents/skills/chadwin-preferences`.
- project-local Claude mirrors are tracked under `.claude/skills/` and synced from `.agents/skills/`.
- bundled `chadwin-setup` owns setup control-plane behavior:
  - core external skill manifest and install/update/check workflow
  - shared data-root bootstrap
  - shared data-contract validation
- Do not duplicate setup workflow logic in app-repo docs/scripts when it already belongs to `chadwin-setup`.

## Data Root Convention
`<DATA_ROOT>` resolves to:
- `CHADWIN_DATA_DIR` when set.
- Otherwise OS default app data location:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

Ownership rule:
- `chadwin-setup` creates shared primitives only:
  - `<DATA_ROOT>/`
  - `<DATA_ROOT>/user_preferences.json`
  - `<DATA_ROOT>/idea-screens/`
  - `<DATA_ROOT>/companies/`
  - `<DATA_ROOT>/improvement-log.md`
- Other skills may create additional files/directories under `<DATA_ROOT>`, but must not repurpose or break shared primitives.

## Shared Data Contract
Goal: skills remain swappable as long as these primitives and path rules stay stable.

### Required Shared Primitives
These paths are reserved and must remain valid:
- `<DATA_ROOT>/user_preferences.json`
- `<DATA_ROOT>/idea-screens/`
- `<DATA_ROOT>/companies/`
- `<DATA_ROOT>/improvement-log.md`

### Company Package Primitive
Each company package lives at:
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/`

Rules:
- `<EXCHANGE_COUNTRY>` is uppercase ISO 3166-1 alpha-2 for the country where the listing exchange is located (for example `US`, `JP`, `GB`).
- Company package should contain:
  - `data/`
  - `reports/`

### Research Run Primitive
Each report run instance lives at:
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`

`<REPORT_DATE_DIR>` must match:
- `YYYY-MM-DD`
- `YYYY-MM-DD-##` (additional runs for the same as-of date)

A completed run must contain:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

Report directory allocation rule:
- Never overwrite a completed package.
- If `reports/YYYY-MM-DD/valuation/inputs.yaml` exists and the package is incomplete (missing `report.md` or `valuation/outputs.json`), complete `YYYY-MM-DD` before creating a suffixed directory.

### Screener Results Primitive (`idea-screens/**/screener-results.jsonl`)
Each screener run writes one JSONL queue file in its own run folder:
- `<DATA_ROOT>/idea-screens/<SCREEN_RUN_ID>/screener-results.jsonl`

`<SCREEN_RUN_ID>` must match strict format:
- `YYYY-MM-DD-HHMMSS`

One JSON object per line.

Required fields:
- `ticker`
- `exchange_country` (ISO alpha-2 for the country where the listing exchange is located)

Recommended fields:
- `company`
- `exchange`
- `sector`
- `industry`
- `thesis`
- `market`

Current screener behavior note:
- `fetch-us-investment-ideas` is LLM-first (Finviz-first with web-search fallback when needed) and targets `screener-results.jsonl` as the final durable output.
- Sidecar files (for example `finviz-candidates.json` or temporary selection payloads) are helper artifacts and must not be treated as required downstream primitives.

Legacy row compatibility:
- Historical rows may contain metadata fields such as `source`, `generated_at_utc`, `queued_at_utc`, or `source_output`.
- New rows should not rely on those metadata fields being present.

### Preferences Primitive (`user_preferences.json`)
Required top-level keys:
- `markets`
- `sector_and_industry_preferences`
- `investment_strategy_preferences`
- `report_preferences`
- `updated_at_utc`

`markets.included_countries` accepts ISO 3166-1 alpha-2 uppercase country codes only.

### Skill Extension Rules
Allowed:
- New top-level namespaces under `<DATA_ROOT>/<skill-or-purpose>/...`
- Additional files under canonical company/report package paths

Not allowed:
- Renaming or repurposing required shared primitive paths
- Writing non-canonical valuation files such as `valuation/output.json`
- Overwriting completed report packages

### Contract Validation
Validate shared contract compliance with:

```bash
.venv/bin/python ".agents/skills/chadwin-setup/scripts/validate_data_contract.py"
```

## Getting Started
1. Work from repository root: `chadwin-agent`.
2. If the user asks to begin setup (for example, "let's get started"), run:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

3. Treat this as the required setup handoff:
   - the human uses natural-language chat prompts only,
   - the LLM executes this bundled setup entrypoint and all required follow-on commands.
4. Use `.venv` for Python commands.
5. Follow the relevant skill `SKILL.md` for any task-specific workflow.
6. Run the shared contract validator after setup and after any contract-affecting changes.

## Setup Command Reference
Primary setup entrypoint from repo root:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

Default setup mode follows refs from `.agents/skills/chadwin-setup/assets/skills.lock.json`.
Repository default is floating `main` refs, so each setup run syncs skills to the latest `origin/main` commit.
Setup also self-updates the app workspace:
- git clone installs: fetch + fast-forward pull on the default branch when the worktree is clean
- downloaded archive installs: initialize `.git`, attach official origin, and align to the remote default branch

Bootstrap does not require EDGAR identity. Configure it as part of onboarding:
- ask the user for SEC identity in the form `Full Name <email@example.com>`,
- write it to repo `.env` as:

```bash
EDGAR_IDENTITY="Full Name <email@example.com>"
```

Optional shortcut (also writes/updates repo `.env`):

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --edgar-identity "Full Name <email@example.com>"
```

Bootstrap responsibilities:
- self-update app workspace from `https://github.com/chadwinco/chadwin-agent` when safe (or initialize git metadata for downloaded copies)
- ensure app `.venv` exists
- install/update required core external skills from `.agents/skills/chadwin-setup/assets/skills.lock.json` into selected runtime targets (default both `~/.codex/skills` and `~/.claude/skills`; bundled skills are excluded from this manifest)
- sync bundled project skills from `.agents/skills/` to `.claude/skills/`
- run `chadwin-setup` shared `<DATA_ROOT>` bootstrap + validation scripts

Runtime target controls:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target both
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target codex
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --runtime-target claude
```

Runtime path overrides:

```bash
export CHADWIN_CODEX_SKILLS_DIR="$HOME/.codex/skills"
export CHADWIN_CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
```

Dry-run planning:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --dry-run
```

Skip app workspace self-update:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --skip-self-update
```

Install/update using each repo's default branch tip (ignores manifest refs):

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --latest
```

Check whether installed core skills are aligned with manifest refs (default: `main`):

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check
```

Check against latest default-branch tips:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check --latest
```

`--check` cannot be combined with `--dry-run`.

## Skill Freshness Policy
Goal: keep clients current with upstream skill changes while still supporting optional reproducible releases.

Baseline rules:
- Keep `.agents/skills/chadwin-setup/assets/skills.lock.json` on floating `main` refs for normal operation.
- Use `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"` at session start (or when session-start recency is unknown) to sync each core external skill to the latest `origin/main` commit.
- Tagged releases are still allowed; use pinned tags or commit SHAs only when intentionally creating a release snapshot.

Periodic drift check:
- Run this when you need an explicit status check without mutating state:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check
```

- Exit `0`: installed skills match manifest refs (default `main`).
- Exit `2`: one or more skills are behind manifest refs; summarize which skills drifted and run setup sync.

Optional release snapshot flow (main -> pinned):
1. Pin `.agents/skills/chadwin-setup/assets/skills.lock.json` refs to tags or SHAs for the intended release snapshot.
2. Run required smoke checks and shared contract validation.
3. Re-run setup with the pinned manifest for validation:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

4. Restore refs to `main` after release validation if you are returning to default latest-sync behavior.

## Core Skill Manifest
The distributed core-skill release contract is `.agents/skills/chadwin-setup/assets/skills.lock.json`.

It defines:
- required core external skills + git refs (default `main`; optional pinned tags/SHAs for release snapshots)
- full git clone sources per skill (URL, SSH, or filesystem path)
- optional deprecated skills excluded from install

Bundled required skills live in `.agents/skills/` and must not be listed in the external manifest.

## General Ways of Working
- Execute tasks directly in the workspace; do not stop at planning when execution is possible.
- Treat skill docs as authoritative for skill behavior; do not duplicate or invent alternate workflows here.
- Treat scripts and shell commands as helpers, not substitutes for reasoning.
- Keep work traceable: explicit dates, assumptions, and file references.
- After each command/edit, review outputs for errors and correct issues immediately.
- Keep changes minimal and auditable.
- Preserve existing user changes unless explicitly asked to modify them.
- Prefer `rg` / `rg --files` for search.

## Completion and Validation
A task is not done until:
- requested artifacts are present and internally consistent,
- affected shared contract rules are still satisfied,
- the shared contract validator passes.

When a repeatable process issue is found:
- update the owning skill or reference,
- append the implemented improvement to `<DATA_ROOT>/improvement-log.md`.
