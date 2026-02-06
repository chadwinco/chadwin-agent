---
name: fetch-company-data
description: Fetch EDGAR filings, XBRL-based financial statements, and earnings call transcripts for this repo's company research pipeline. Use when adding a new ticker, refreshing `companies/TICKER/data`, or regenerating `companies/TICKER/model/assumptions.yaml` before running analysis.
---

# Fetch Company Data

## Overview
Fetch filings, financials, and transcripts into `companies/<TICKER>/data` and optionally bootstrap model assumptions for a new or refreshed ticker.

## Quick Start
1. Activate the repo virtual environment and install dependencies if needed.
2. Set `EDGAR_IDENTITY` in `.env`, or plan to pass `--identity`.
3. Run the bootstrap script from the repo root.

```bash
python3 scripts/add_company.py --ticker <TICKER> --asof <YYYY-MM-DD>
```

## Workflow
1. Confirm prerequisites.
2. Bootstrap or refresh company data.
3. Verify outputs and source logging.

### 1. Confirm prerequisites
- Follow `docs/python-setup.md` if the virtual environment or dependencies are missing.
- Ensure `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) is set in `.env`, or pass `--identity`.

### 2. Bootstrap or refresh company data
Run the data fetcher from the repo root:

```bash
python3 scripts/add_company.py --ticker <TICKER> --asof <YYYY-MM-DD>
```

Optional flags:
- `--identity "Name email@domain.com"` to override `.env`.
- `--skip-analysis` to fetch data only.
- `--overwrite-assumptions` to replace `companies/<TICKER>/model/assumptions.yaml`.

### 3. Verify outputs and source logging
Check that these files exist:
- `companies/<TICKER>/data/financials/annual/income_statement.csv`
- `companies/<TICKER>/data/financials/annual/balance_sheet.csv`
- `companies/<TICKER>/data/financials/annual/cash_flow_statement.csv`
- `companies/<TICKER>/data/10-K-*.md` or `companies/<TICKER>/data/20-F-*.md`
- `companies/<TICKER>/data/earnings-call-<YYYY-MM-DD>-<source>.md` if a transcript was found
- `companies/<TICKER>/model/assumptions.yaml`
- `docs/source-log.md` updated with transcript and data snapshot entries

## Troubleshooting
- If EDGAR identity errors appear, set `EDGAR_IDENTITY` in `.env` or pass `--identity`.
- If transcript fetching returns nothing, ensure `beautifulsoup4` is installed and retry later.
- If annual statements fail to parse, inspect `companies/<TICKER>/data/financials/annual/*.csv` and review `docs/data-dictionary.md`.

## Related References
- `docs/research-workflow.md` for the end-to-end pipeline.
- `docs/data-dictionary.md` for required data files and columns.
