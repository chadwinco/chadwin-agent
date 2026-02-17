---
name: chadwin-research
description: Thin orchestration wrapper for fetch + research + progressive escalation. Use when you want one entrypoint that (1) auto-selects a company from `<DATA_ROOT>/idea-screens/company-ideas-log.jsonl` when no ticker is provided, fetches market-appropriate data, and runs research, or (2) when a ticker is provided, determines market (US vs non-US), checks existing company data/report freshness, fetches if needed, and skips research only when no new data was fetched and the latest report is already current. After initial report generation, it routes follow-up runs using the report's Research Stop Gate confidence criteria.
---

# Research

## Overview
Use this as the default entrypoint for autonomous runs. It delegates to:
- `$fetch-us-company-data`
- an installed market-specific fetch skill for non-US companies
- `$run-llm-workflow`

Company packages are organized by exchange country under `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/...`.
When present, `<DATA_ROOT>/user_preferences.json` is used by default to filter queue picks (market + sector/industry) and guard against running excluded markets.

## Workflow

1. Run the router script from repo root:

```bash
python3 .agents/skills/chadwin-research/scripts/run_research.py [--ticker <TICKER>] --asof <YYYY-MM-DD>
```

2. Read JSON output fields:
- `resolved_ticker`
- `market`
- `new_data_fetched`
- `next_action`
- `reason`

3. Follow decision:
- If `next_action` is `done`, stop.
- If `next_action` is `run_research`, run `$run-llm-workflow` for `resolved_ticker` and the same `asof` date.

4. Follow-up routing (same skill, deeper focus):

```bash
python3 .agents/skills/chadwin-research/scripts/run_research.py --ticker <RESOLVED_TICKER> --asof <YYYY-MM-DD> --post-report-check
```

- If `next_action` is `run_research`, run `$run-llm-workflow` again using:
  - `resolved_ticker`
  - same `asof` date
  - `baseline_report_dir` from JSON output as the starting reference package
  - `followup_focus` from JSON output (typically highest-impact unresolved lever from the report gate)
- If `next_action` is `done`, stop.

5. When research is complete, remove ticker from queue:

```bash
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py remove --ticker <RESOLVED_TICKER>
```

- Remove only after required output files exist in the final report package:
  - `report.md`
  - `valuation/inputs.yaml`
  - `valuation/outputs.json`

6. Run post-run introspection via `$run-llm-workflow` `references/improvement-loop.md` after every completed run, apply workflow/reference updates in the same turn when repeatable workflow gaps are found, and only append to `improvement-log.md` when an actual improvement is shipped (no no-change entries).

## Behavior Contract

- No ticker provided:
  - Select from `<DATA_ROOT>/idea-screens/company-ideas-log.jsonl`, filtered by `<DATA_ROOT>/user_preferences.json` when present.
  - Use selected company's market to run the correct fetch script.
  - Set `next_action` to `run_research`.

- Ticker provided:
  - Infer market from existing company profile, queue metadata, and ticker pattern.
  - If preferences exclude inferred market, return an error (unless `--ignore-preferences` is set).
  - Run correct fetch script for that market.
  - If no new data was fetched and an up-to-date report already exists, set `next_action` to `done`.
  - Otherwise set `next_action` to `run_research`.

- Post-report follow-up routing (`--post-report-check`):
  - Load latest report package for the same as-of date (`YYYY-MM-DD` or `YYYY-MM-DD-*`).
  - Read the report `## Research Stop Gate` section and check:
    - `Research complete: Yes`
    - `Diminishing returns from additional research: Yes`
    - `Open thesis-critical levers: 0`
    - `Thesis confidence` vs `--followup-confidence-threshold` (default `0.80`)
  - If the confidence gate passes, set `next_action` to `done`.
  - If the confidence gate is not met, set `next_action` to `run_research` and carry forward `followup_focus` from `Next best research focus`.

## Options

- `--ticker <TICKER>`: Optional explicit ticker/identifier.
- `--asof <YYYY-MM-DD>`: As-of date (default: today).
- `--market us|non-us`: Optional override if market inference is ambiguous.
- `--fetch-script <PATH>`: Optional override path to a market fetch `add_company.py` script.
- `--identity "<NAME EMAIL>"`: EDGAR identity for US fetch runs.
- `--isin <ISIN>`: Optional identifier used by non-US fetch scripts that accept it.
- `--ideas-log <PATH>`: Override queue log path.
- `--preferences-path <PATH>`: Override preferences path (default `<DATA_ROOT>/user_preferences.json`).
- `--ignore-preferences`: Disable preference-based queue filtering and market guardrails.
- `--overwrite-assumptions`: Pass through to fetch scripts.
- `--dry-run`: Emit decision without running fetch.
- `--post-report-check`: Evaluate latest same-date report package and emit follow-up routing decision.
- `--followup-confidence-threshold <FLOAT>`: Confidence threshold for post-report confidence gating (0-1, default `0.80`).

## Validation Reference

- For end-to-end manual checks (fetch, research, valuation artifacts, queue behavior), use:
  - `references/workflow-validation-scenarios.md`
