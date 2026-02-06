---
name: run-company-research
description: Run the company research pipeline for this repo, including quality checks, metrics, valuation, and report generation. Use when regenerating `companies/TICKER/analysis/*`, updating `companies/TICKER/model/outputs.json`, or validating data after edits to assumptions or source files.
---

# Run Company Research

## Overview
Run the analysis workflow that validates data, computes metrics, values the business, and writes the report for a ticker.

## Quick Start
1. Ensure `companies/<TICKER>/data` is populated.
2. Update `companies/<TICKER>/model/assumptions.yaml` if needed.
3. Run the pipeline from the repo root.

```bash
python3 scripts/run_company.py --ticker <TICKER> --asof <YYYY-MM-DD>
```

## Workflow
1. Confirm inputs.
2. Run the analysis script.
3. Run the LLM analysis (assistant step).
4. Validate against the checklist.
5. Review outputs and logs.

### 1. Confirm inputs
- If data is missing, use `$fetch-company-data` first.
- Ensure required files exist per `docs/data-dictionary.md`.
- Edit `companies/<TICKER>/model/assumptions.yaml` for scenario changes.

### 2. Run the analysis script
Execute the pipeline from the repo root:

```bash
python3 scripts/run_company.py --ticker <TICKER> --asof <YYYY-MM-DD>
```


### 3. Run the LLM analysis (assistant step)
- Read the prompt files in `prompts/` and the workflow docs in `docs/research-workflow.md`.
- **Agentic search:** use `grep` (or `rg` if available) against the raw files in `companies/<TICKER>/data` to find relevant sections in real time.
  - Examples: search for `## Business`, `Segment Information`, `Risk Factors`, `Management's Discussion`, `catastrophe`, `combined ratio`, `net premiums`, `reserve`, `reinsurance`, `dividend`, `buyback`.
  - Iterate queries until you have coverage for each prompt section (don’t settle for the first match).
- Produce:
  - `companies/<TICKER>/analysis/<YYYY-MM-DD>-report.md`
- Cite sources inline with file paths and log any external sources in `docs/source-log.md` if needed.

### 4. Validate against the checklist
- Use `docs/research-checklist.md` as a quality gate before finalizing the report.
- Fix any checklist gaps before delivering the final report.

### 5. Review outputs and logs
Validate the generated artifacts:
- `companies/<TICKER>/model/outputs.json`
- `companies/<TICKER>/analysis/<YYYY-MM-DD>-report.md`
- `docs/source-log.md` updated with a data snapshot entry

## Troubleshooting
- If quality checks fail, fix missing columns or dates in the CSVs and rerun.
- Use `docs/research-checklist.md` to confirm data integrity, financial quality, and valuation coverage.
- If narrative sections look thin, update inputs in `companies/<TICKER>/data` or edit templates in `templates/report.md`.

## Related References
- `docs/research-workflow.md` for the end-to-end pipeline.
- `docs/data-dictionary.md` for required data files and columns.
