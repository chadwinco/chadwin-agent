---
name: research
description: Thin orchestration wrapper for the existing company fetch and research skills. Use when you want one entrypoint that (1) auto-selects a company from `idea-screens/company-ideas-log.jsonl` when no ticker is provided, fetches market-appropriate data, and runs research, or (2) when a ticker is provided, determines market (US vs JP), checks existing company data/report freshness, fetches if needed, and skips research only when no new data was fetched and the latest report is already current.
---

# Research

## Overview

Use this as the default entrypoint for autonomous runs. It delegates to:
- `$fetch-us-company-data`
- `$fetch-japanese-company-data`
- `$run-llm-workflow`

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

4. When research completes, ensure queue removal is handled (the `$run-llm-workflow` workflow already includes this):

```bash
python3 .agents/skills/research/scripts/company_idea_queue.py remove --ticker <RESOLVED_TICKER>
```

## Behavior Contract

- No ticker provided:
  - Select from `idea-screens/company-ideas-log.jsonl`.
  - Use the selected company's market to run the correct fetch script.
  - Set `next_action` to `run_research`.

- Ticker provided:
  - Infer market from existing company profile, queue metadata, and ticker pattern.
  - Run the correct fetch script for that market.
  - If no new data was fetched and an up-to-date report already exists, set `next_action` to `done`.
  - Otherwise set `next_action` to `run_research`.

## Options

- `--ticker <TICKER>`: Optional explicit ticker/identifier.
- `--asof <YYYY-MM-DD>`: As-of date (default: today).
- `--market us|jp`: Optional override if market inference is ambiguous.
- `--identity "<NAME EMAIL>"`: EDGAR identity for US fetch runs.
- `--isin <ISIN>`: Optional ISIN for JP fetch runs.
- `--ideas-log <PATH>`: Override queue log path.
- `--overwrite-assumptions`: Pass through to fetch scripts.
- `--dry-run`: Emit decision without running fetch.
