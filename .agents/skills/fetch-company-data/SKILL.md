---
name: fetch-company-data
description: Fetch EDGAR filings, XBRL-based financial statements, and earnings call transcripts for this repo's company research pipeline. Use when adding a new ticker, refreshing `companies/TICKER/data`, or regenerating `companies/TICKER/reports/<DATE>/valuation/inputs.yaml` before running analysis.
---

# Fetch Company Data

## Overview
Fetch filings, financials, analyst forecasts, and transcripts into `companies/<TICKER>/data` and bootstrap valuation assumptions in `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.

This skill keeps fetch logic inside the skill package (`scripts/` + `src/`) so it is easier to share and update independently from the main codebase.

## Skill Path (set once)
Repo-local:

```bash
export FETCH_COMPANY_DATA_ROOT=".agents/skills/fetch-company-data"
export FETCH_COMPANY_DATA_CLI="$FETCH_COMPANY_DATA_ROOT/scripts/add_company.py"
```

Installed skill:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export FETCH_COMPANY_DATA_ROOT="$CODEX_HOME/skills/fetch-company-data"
export FETCH_COMPANY_DATA_CLI="$FETCH_COMPANY_DATA_ROOT/scripts/add_company.py"
```

## Quick Start
1. Follow `references/python-setup.md`.
2. Confirm ticker and as-of date with the user.
3. Run the skill script from the repo root:

```bash
python3 "$FETCH_COMPANY_DATA_CLI" --ticker <TICKER> --asof <YYYY-MM-DD>
```

## Workflow
1. Confirm prerequisites.
2. Confirm ticker and as-of date (do not infer from open files or prior context).
3. Run fetch/bootstrap.
4. Verify outputs and source logging.

### 1. Confirm prerequisites
- Use `references/python-setup.md` for environment setup and dependencies.
- Ensure `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) is set in `.env`, or pass `--identity`.

### 2. Confirm ticker and as-of date
- Only proceed if the user explicitly provided a ticker in the current request.
- If no ticker is specified, ask: `Which ticker should I fetch?`
- If multiple tickers are mentioned, ask which one to run first.
- Echo back ticker and as-of date before execution.

### 3. Run fetch/bootstrap
```bash
python3 "$FETCH_COMPANY_DATA_CLI" --ticker <TICKER> --asof <YYYY-MM-DD>
```

Optional flags:
- `--identity "Name email@domain.com"` overrides `.env`.
- `--skip-analysis` fetches data only.
- `--overwrite-assumptions` replaces `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.

### 4. Verify outputs and source logging
Validate outputs described in `references/data-outputs.md`, including:
- `companies/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/<TICKER>/data/filings/10-K-*.md` or `companies/<TICKER>/data/filings/20-F-*.md`
- `companies/<TICKER>/data/filings/earnings-call-<YYYY-MM-DD>-<source>.md` if a transcript was found
- `companies/<TICKER>/data/analyst_estimates.csv` if analyst revenue forecasts were available
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `docs/source-log.md` updated per `references/source-log-format.md`

## Troubleshooting
- If EDGAR identity errors appear, set `EDGAR_IDENTITY` in `.env` or pass `--identity`.
- If transcript fetching returns nothing, ensure `beautifulsoup4` is installed and retry later.
- If annual statements fail to parse, inspect `companies/<TICKER>/data/financial_statements/annual/*.csv` and review `references/data-outputs.md`.

## Related References
- `references/python-setup.md`
- `references/data-outputs.md`
- `references/source-log-format.md`
