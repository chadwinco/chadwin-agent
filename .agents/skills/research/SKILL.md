---
name: research
description: Thin orchestration wrapper for fetch + research + escalation. Use when you want one entrypoint that (1) auto-selects a company from `idea-screens/company-ideas-log.jsonl` when no ticker is provided, fetches market-appropriate data, and runs research, or (2) when a ticker is provided, determines market (US vs non-US), checks existing company data/report freshness, fetches if needed, and skips research only when no new data was fetched and the latest report is already current. After initial report generation, it can route promising names to deep-dive.
---

# Research

## Overview

Use this as the default entrypoint for autonomous runs. It delegates to:
- `$fetch-us-company-data`
- an installed market-specific fetch skill for non-US companies
- `$run-llm-workflow`
- `$run-llm-deep-dive` (auto-routed for promising initial reports)

Company packages are organized by exchange country under `companies/<EXCHANGE_COUNTRY>/<TICKER>/...`.
When present, `preferences/user_preferences.json` is used by default to filter queue picks (market + sector/industry) and guard against running excluded markets.

## Workflow

1. Run the router script from repo root:

```bash
python3 .agents/skills/research/scripts/run_research.py [--ticker <TICKER>] --asof <YYYY-MM-DD>
```

2. Read the JSON output fields:
- `resolved_ticker`
- `market`
- `new_data_fetched`
- `next_action`
- `reason`

3. Follow decision:
- If `next_action` is `done`, stop.
- If `next_action` is `run_research`, run `$run-llm-workflow` for `resolved_ticker` and the same `asof` date.

4. After `$run-llm-workflow` completes, run post-report routing check:

```bash
python3 .agents/skills/research/scripts/run_research.py --ticker <RESOLVED_TICKER> --asof <YYYY-MM-DD> --post-report-check
```

- If `next_action` is `run_deep_dive`, run `$run-llm-deep-dive` using:
  - `resolved_ticker`
  - `asof` as revised as-of date
  - `baseline_report_dir` from the JSON output
- If `next_action` is `done`, stop.

5. When research and optional deep-dive complete, ensure queue removal is handled:

```bash
python3 .agents/skills/research/scripts/company_idea_queue.py remove --ticker <RESOLVED_TICKER>
```

- If a deep-dive was run, verify all required deep-dive outputs exist before queue removal:
  - `report.md`
  - `valuation/inputs.yaml`
  - `valuation/outputs.json`
  - `deep-dive-plan.md`
  - `deep-dive-changes.md`
  - `third-party-sources.md`
- Do not run `--post-report-check` again after deep-dive finalization for the same as-of date; it is a baseline-to-deep-dive routing gate, not a completion gate.

## Behavior Contract

- No ticker provided:
  - Select from `idea-screens/company-ideas-log.jsonl`, filtered by `preferences/user_preferences.json` when present.
  - Use the selected company's market to run the correct fetch script.
  - Set `next_action` to `run_research`.

- Ticker provided:
  - Infer market from existing company profile, queue metadata, and ticker pattern.
  - If preferences exclude the inferred market, return an error (unless `--ignore-preferences` is set).
  - Run the correct fetch script for that market.
  - If no new data was fetched and an up-to-date report already exists, set `next_action` to `done`.
  - Otherwise set `next_action` to `run_research`.

- Post-report deep-dive routing (`--post-report-check`):
  - Load the latest report package for the same as-of date (`YYYY-MM-DD` or `YYYY-MM-DD-*`).
  - Read base scenario `margin_of_safety` from `valuation/outputs.json`.
  - If base MoS is greater than or equal to `--deep-dive-mos-threshold` (default `0.25`) and report verdict is not `Avoid`, set `next_action` to `run_deep_dive`.
  - Otherwise set `next_action` to `done`.

## Options

- `--ticker <TICKER>`: Optional explicit ticker/identifier.
- `--asof <YYYY-MM-DD>`: As-of date (default: today).
- `--market us|non-us`: Optional override if market inference is ambiguous.
- `--fetch-script <PATH>`: Optional override path to a market fetch `add_company.py` script.
- `--identity "<NAME EMAIL>"`: EDGAR identity for US fetch runs.
- `--isin <ISIN>`: Optional identifier used by non-US fetch scripts that accept it.
- `--ideas-log <PATH>`: Override queue log path.
- `--preferences-path <PATH>`: Override preferences path (default `preferences/user_preferences.json`).
- `--ignore-preferences`: Disable preference-based queue filtering and market guardrails.
- `--overwrite-assumptions`: Pass through to fetch scripts.
- `--dry-run`: Emit decision without running fetch.
- `--post-report-check`: Evaluate latest same-date report package and emit deep-dive routing decision.
- `--deep-dive-mos-threshold <FLOAT>`: Base MoS threshold for auto deep-dive routing (default `0.25`).

## Validation Reference

- For end-to-end manual checks (fetch, research, valuation artifacts, queue behavior), use:
  - `references/workflow-validation-scenarios.md`
