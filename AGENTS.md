# AGENTS.md

## Table of Contents
- [Project Identity](#project-identity)
- [Data Root Convention](#data-root-convention)
- [Shared Data Contract](#shared-data-contract)
- [Non-Negotiable Operating Contract](#non-negotiable-operating-contract)
- [Skill Selection Protocol](#skill-selection-protocol)
- [Required Outputs Per Completed Run](#required-outputs-per-completed-run)
- [LLM-First Execution Rules](#llm-first-execution-rules)
- [Real-Time Error Handling Loop](#real-time-error-handling-loop)
- [Evidence and Citation Discipline](#evidence-and-citation-discipline)
- [Quality Gate Requirements](#quality-gate-requirements)
- [Improvement Loop (Mandatory for Repeatable Issues)](#improvement-loop-mandatory-for-repeatable-issues)
- [Practical Conventions](#practical-conventions)

## Project Identity
This repository is a local, Codex-operated equity research system.

It is intentionally different from a traditional app:
- An LLM agent is always the active operator.
- Deterministic Python code is used only for bounded automation that is materially faster/easier than agent-native execution (for example: `edgartools` SEC fetches, strict parsers, deterministic transformations, repeatable calculations).
- The LLM is always responsible for sanity checks, error recovery, and final outcome quality.

If you are acting as an agent in this repo, treat successful end-to-end delivery as your responsibility.

## Data Root Convention
`<DATA_ROOT>` resolves to:
- `CHADWIN_DATA_DIR` when set.
- Otherwise OS default app data location:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

This file is the canonical shared contract and operating guide.

Ownership rule:
- `chadwin-setup` creates shared primitives only:
  - `<DATA_ROOT>/`
  - `<DATA_ROOT>/user_preferences.json`
  - `<DATA_ROOT>/idea-screens/`
  - `<DATA_ROOT>/companies/`
  - `<DATA_ROOT>/improvement-log.md`
- Every other skill may create and own additional subdirectories/files under `<DATA_ROOT>`, but must not repurpose or break shared primitives.
- Do not assume other non-required skills are installed when creating directories.

## Shared Data Contract
This section defines the shared local-data primitives that all skills must respect.

Goal: skills are swappable as long as they preserve these primitives.

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
- `<EXCHANGE_COUNTRY>` must be uppercase ISO 3166-1 alpha-2 for the country where the company's exchange is located (for example `US`, `JP`, `GB`).
- Company package should contain:
  - `data/`
  - `reports/`

### Research Run Primitive
Each report run instance lives at:
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`

`<REPORT_DATE_DIR>` must match:
- `YYYY-MM-DD`
- `YYYY-MM-DD-##` (for additional runs on the same as-of date)

A completed run must contain:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

### Screener Results Primitive (`idea-screens/**/screener-results.jsonl`)
Each screener run must write one JSONL result file inside its own run folder:
- `<DATA_ROOT>/idea-screens/<SCREEN_RUN_ID>/screener-results.jsonl`

One JSON object per line.

Required fields:
- `ticker`
- `exchange_country` (ISO alpha-2 for the country where the company's exchange is located; use `US` for US listings)

Recommended fields:
- `company`
- `exchange`
- `sector`
- `industry`
- `thesis`
- `source`
- `generated_at_utc`
- `queued_at_utc`
- `source_output`

### Preferences Primitive (`user_preferences.json`)
Required top-level keys:
- `markets`
- `sector_and_industry_preferences`
- `investment_strategy_preferences`
- `report_preferences`
- `updated_at_utc`

`markets.included_countries` accepts:
- ISO 3166-1 alpha-2 uppercase country codes only (for example `US`, `JP`, `GB`).

### Skill Extension Rules
Skills may store additional data if they do not violate shared primitives.

Allowed extension zones:
- New top-level namespaces under `<DATA_ROOT>/<skill-or-purpose>/...`
- Additional files under company packages (for example `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/<custom>/...`)
- Additional files under report packages (for example `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/<custom>/...`)

Not allowed:
- Renaming or repurposing required shared primitive paths.
- Writing non-canonical valuation output files such as `valuation/output.json`.
- Overwriting completed report packages.

### Validation
Validate contract compliance with:

```bash
.venv/bin/python "${CHADWIN_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}/chadwin-setup/scripts/validate_data_contract.py"
```

## Non-Negotiable Operating Contract
1. Execute tasks directly in the local workspace; do not stop at planning if execution is possible.
2. Use installed skills in `${CODEX_HOME:-/.codex}/skills/*/SKILL.md` as the authoritative workflows.
3. After every command or edit, inspect outputs for errors or inconsistencies and fix them immediately.
4. Never leave known breakage behind; rerun affected steps until outputs are correct.
5. Keep work traceable: explicit dates, explicit assumptions, explicit file references.
6. Do not add deterministic wrappers for tasks the LLM can already do directly (for example generic web search/browsing, routine file reads/writes, or simple routing decisions).

## Skill Selection Protocol
- Discover available skills from `${CODEX_HOME:-/.codex}/skills/*/SKILL.md` before selecting a workflow.
- If a user names a skill (for example, `$chadwin-research`) or the request clearly matches a skill's purpose, use that skill.
- If no skill is named, prefer an installed orchestrator skill when one exists; otherwise compose the smallest set of concrete skills needed for the request.
- Direct invocation of a lower-level skill means the user is intentionally taking tighter control; execute exactly at that level.
- Read the target `SKILL.md` first, then load only the references needed for the task.
- Resolve relative paths in skill docs from that skill's directory first.
- Prefer skill-provided scripts/assets/templates over re-creating equivalents.
- If multiple skills apply, use the smallest set that covers the request and execute in explicit order.
- If a skill is missing or blocked, state the issue briefly and continue with the closest valid fallback.

## Required Outputs Per Completed Run
For `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

A run is not complete until all required files exist and are internally consistent.

`<REPORT_DATE_DIR>` naming convention:
- First run for an as-of date: `YYYY-MM-DD`
- Additional runs for the same as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.
- Exception: if `reports/YYYY-MM-DD/valuation/inputs.yaml` already exists and the package is incomplete (missing `report.md` or `valuation/outputs.json`), complete `YYYY-MM-DD` instead of allocating a suffix.

## LLM-First Execution Rules
- Treat scripts and shell commands as helpers, not substitutes for reasoning.
- Default to direct LLM execution for open-ended work (web research, source triage, synthesis, file drafting/edits).
- Do not build or expand script-level API plumbing for generic web search or generic repository file operations when the agent can do the task directly.
- Add deterministic code only when it clearly improves speed, reliability, or reproducibility for a bounded step.
- If uncertain whether code is justified, do the task directly with the LLM first and only then codify the narrow repeated bottleneck.
- Perform cross-checks the scripts cannot guarantee (units, sign conventions, date cutoffs, claim-evidence alignment).
- Validate that conclusions match computed valuation outputs and cited evidence.
- If data is missing or malformed, resolve it (or fetch again) before writing final conclusions.

## Real-Time Error Handling Loop
For each major step:
1. Run command/workflow step.
2. Review stdout/stderr and generated files.
3. If anything fails or looks suspicious, diagnose root cause.
4. Apply fix (input correction, script patch, workflow adjustment, or rerun).
5. Re-validate all downstream artifacts impacted by the fix.

Do not defer known issues to a later run when they block correctness now.

## Evidence and Citation Discipline
- Local files under `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/` are the primary evidence base.
- Every factual claim in final write-ups must cite local file paths.
- Prefer filings for core financial/forecast claims; use transcripts for supporting qualitative color.
- Paraphrase source content; avoid verbatim copying.

## Quality Gate Requirements
Before marking done:
- Required outputs are present and readable.
- Ticker and as-of date are explicit and consistent across files.
- Valuation method matches business model (DCF vs residual-income where applicable).
- Base/bull/bear assumptions are explicit and defensible.
- Margin-of-safety conclusion reconciles with valuation outputs and current price input.
- Active research-skill quality checklist is satisfied (for example, when installed: `${CODEX_HOME:-/.codex}/skills/chadwin-research/references/research-workflow.md`).
- Shared data contract validation passes:
  - `.venv/bin/python "${CHADWIN_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}/chadwin-setup/scripts/validate_data_contract.py"`

## Improvement Loop (Mandatory for Repeatable Issues)
When you find a repeatable problem or process weakness:
1. Update the relevant skill.
2. Append a concise row to `<DATA_ROOT>/improvement-log.md`.
3. Validate with at least one end-to-end ticker run when process logic changes.

Only append rows for actual process improvements that were implemented.
Do not add no-change introspection rows.

Do not only patch a single report output when the issue is systemic.

## Practical Conventions
- Work from repo root: `chadwin-codex`
- Use `python3 scripts/chadwin_setup.py` as the canonical setup/install entrypoint for new machines and fresh worktrees (locked refs by default; use `--latest` only when intentionally tracking latest skill branches).
- Store company packages by exchange country code (for example `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY_CODE>/<TICKER>/...`).
- Under `<DATA_ROOT>/companies/`, country folders must use uppercase ISO 3166-1 alpha-2 codes (for example `US`, `JP`, `GB`), not exchange names or 3-letter country codes.
- Use only canonical company layout paths: `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY_CODE>/<TICKER>/...`.
- For report outputs, never overwrite a completed report package; allocate the next `reports/<REPORT_DATE_DIR>` directory for that as-of date. If `reports/YYYY-MM-DD` is an incomplete fetch-bootstrap package (has `valuation/inputs.yaml` but missing `report.md` or `valuation/outputs.json`), finish that package first.
- Honor `<DATA_ROOT>/user_preferences.json` in queue selection and reporting unless the user explicitly asks to override.
- Use `.venv` for Python execution.
- Prefer `rg`/`rg --files` for search.
- Keep changes minimal, concrete, and auditable.
- Preserve existing user changes unless explicitly asked to alter them.
