---
name: run-company-research
description: Run the company research pipeline for this repo, including quality checks, metrics, valuation, and report/appendix generation. Use when regenerating `companies/TICKER/analysis/*`, updating `companies/TICKER/model/outputs.json`, or validating data after edits to assumptions or source files.
---

# Run Company Research

## Overview
Run the analysis workflow that validates data, computes metrics, values the business, and writes the report and appendix for a ticker.

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
3. Prepare the LLM context pack.
4. Run the LLM analysis (assistant step).
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


### 3. Prepare the LLM context pack
Generate a deterministic context bundle for the LLM to use:

```bash
python3 scripts/prepare_llm_context.py --ticker <TICKER> --asof <YYYY-MM-DD>
```

This writes:
- `companies/<TICKER>/analysis/<YYYY-MM-DD>-llm-context.md`

### 4. Run the LLM analysis (assistant step)
- Read the prompt files in `prompts/`.
- Read the context pack generated in step 3.
- Produce:
  - `companies/<TICKER>/analysis/<YYYY-MM-DD>-report.md`
  - `companies/<TICKER>/analysis/<YYYY-MM-DD>-appendix.md`
- Cite sources from the context pack and log any external sources in `docs/source-log.md`.

### 5. Review outputs and logs
Validate the generated artifacts:
- `companies/<TICKER>/model/outputs.json`
- `companies/<TICKER>/analysis/<YYYY-MM-DD>-report.md`
- `companies/<TICKER>/analysis/<YYYY-MM-DD>-appendix.md`
- `docs/source-log.md` updated with a data snapshot entry

## Troubleshooting
- If quality checks fail, fix missing columns or dates in the CSVs and rerun.
- Use `docs/research-checklist.md` to confirm data integrity, financial quality, and valuation coverage.
- If narrative sections look thin, update inputs in `companies/<TICKER>/data` or edit templates in `templates/report.md` and `templates/appendix.md`.

## Related References
- `docs/research-workflow.md` for the end-to-end pipeline.
- `docs/data-dictionary.md` for required data files and columns.
