# AGENTS.md

## Project Identity
This repository is a local, Codex-operated equity research system.

It is intentionally different from a traditional app:
- An LLM agent is always the active operator.
- Deterministic Python code is used for bounded automation only (fetching, parsing, transformations, calculations).
- The LLM is always responsible for sanity checks, error recovery, and final outcome quality.

If you are acting as an agent in this repo, treat successful end-to-end delivery as your responsibility.

## Non-Negotiable Operating Contract
1. Execute tasks directly in the local workspace; do not stop at planning if execution is possible.
2. Use skills in `.agents/skills/*/SKILL.md` as the authoritative workflows.
3. Do not replace the LLM research workflow with a one-command deterministic analyzer.
4. After every command or edit, inspect outputs for errors or inconsistencies and fix them immediately.
5. Never leave known breakage behind; rerun affected steps until outputs are correct.
6. Keep work traceable: explicit dates, explicit assumptions, explicit file references.

## Skill Selection Protocol
- Treat `$research` as the default top-level skill for semi-autonomous runs.
- If a user names a skill (for example, `$run-llm-workflow`) or the request clearly matches a skill's purpose, use that skill.
- Direct use of non-`$research` skills means the user is intentionally taking tighter control of the workflow; execute exactly at that level.
- Read the target `SKILL.md` first, then load only the references needed for the task.
- Resolve relative paths in skill docs from that skill's directory first.
- Prefer skill-provided scripts/assets/templates over re-creating equivalents.
- If multiple skills apply, use the smallest set that covers the request and execute in explicit order.
- If a skill is missing or blocked, state the issue briefly and continue with the closest valid fallback.

## Canonical Entry Modes
Use one of these modes explicitly:

1. Top-level (default): `$research`
   - This is the semi-autonomous orchestrator.
   - It wraps market selection, fetch, and research steps by calling other skills as needed.
2. Manual control (advanced): direct skill invocation
   - `$fetch-us-investment-ideas`
   - `$fetch-us-company-data`
   - `$fetch-japanese-company-data`
   - `$run-llm-workflow`
   - Choosing these directly indicates the user wants finer-grained process control.

If no specific lower-level control is requested, prefer `$research`.

## Canonical Manual Order (When Not Using `$research`)
1. (Optional) Seed ideas: `$fetch-us-investment-ideas`
2. Fetch company data by market:
   - `$fetch-us-company-data` for US tickers
   - `$fetch-japanese-company-data` for JP tickers
3. Produce research outputs: `$run-llm-workflow`
4. Validate artifacts and pass quality gate
5. Remove completed ticker from `idea-screens/company-ideas-log.jsonl`
6. Record repeatable process improvements in `docs/improvement-log.md`

## Required Outputs Per Completed Run
For `companies/<TICKER>/reports/<YYYY-MM-DD>/`:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

A run is not complete until all required files exist and are internally consistent.

## LLM-First Execution Rules
- Treat scripts and shell commands as helpers, not substitutes for reasoning.
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
- Local files under `companies/<TICKER>/data/` are the primary evidence base.
- Use only evidence dated on or before the selected as-of date.
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
- Run-LLM workflow quality checklist is satisfied:
  - `.agents/skills/run-llm-workflow/references/research-workflow.md`

## Improvement Loop (Mandatory for Repeatable Issues)
When you find a repeatable problem or process weakness:
1. Append a concise row to `docs/improvement-log.md`.
2. Update the relevant skill reference under `.agents/skills/.../references/`.
3. Validate with at least one end-to-end ticker run when process logic changes.

Do not only patch a single report output when the issue is systemic.

## Practical Conventions
- Work from repo root: `/Users/chad/source/chadwin-codex`
- Use `.venv` for Python execution.
- Prefer `rg`/`rg --files` for search.
- Keep changes minimal, concrete, and auditable.
- Preserve existing user changes unless explicitly asked to alter them.
