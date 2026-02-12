---
name: fetch-us-company-data
description: Fetch US/SEC-available filings, XBRL-based financial statements, and earnings call transcripts for this repo's company research pipeline. Use when adding a US ticker, refreshing `companies/US/<TICKER>/data`, or regenerating `companies/US/<TICKER>/reports/<DATE>/valuation/inputs.yaml` before LLM-driven research.
---

# Fetch US Company Data

## Overview
Fetch filings, financials, analyst forecasts, and transcripts into `companies/US/<TICKER>/data` and bootstrap valuation assumptions in `companies/US/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
When present, `preferences/user_preferences.json` is respected by default for queue selection and US market guardrails.

This skill keeps fetch logic inside the skill package (`scripts/`) so it is easier to share and update independently from the main codebase.

## Skill Path (set once)
Repo-local:

```bash
export FETCH_US_COMPANY_DATA_ROOT=".agents/skills/fetch-us-company-data"
export FETCH_US_COMPANY_DATA_CLI="$FETCH_US_COMPANY_DATA_ROOT/scripts/add_company.py"
```

Installed skill:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export FETCH_US_COMPANY_DATA_ROOT="$CODEX_HOME/skills/fetch-us-company-data"
export FETCH_US_COMPANY_DATA_CLI="$FETCH_US_COMPANY_DATA_ROOT/scripts/add_company.py"
```

## Quick Start
1. Follow `references/python-setup.md`.
2. Confirm as-of date with the user. Ticker is optional.
3. Run the skill script from the repo root:

```bash
python3 "$FETCH_US_COMPANY_DATA_CLI" --asof <YYYY-MM-DD> [--ticker <TICKER>]
```

## Workflow
1. Confirm prerequisites.
2. Resolve ticker and as-of date.
3. Run fetch/bootstrap.
4. Verify outputs.

### 1. Confirm prerequisites
- Use `references/python-setup.md` for environment setup and dependencies.
- Ensure `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) is set in `.env`, or pass `--identity`.

### 2. Resolve ticker and as-of date
- If `--ticker` is provided, use it.
- If `--ticker` is omitted, select the next US candidate from `idea-screens/company-ideas-log.jsonl`, filtered by preferences when present.
- If the queue log has no US candidate, stop and ask for a ticker or run `$fetch-us-investment-ideas`.
- If preferences exclude US market, stop and ask to update preferences or rerun with `--ignore-preferences`.
- Echo back the resolved ticker and as-of date before execution.

### 3. Run fetch/bootstrap
```bash
python3 "$FETCH_US_COMPANY_DATA_CLI" --asof <YYYY-MM-DD> [--ticker <TICKER>]
```

Optional flags:
- `--identity "Name email@domain.com"` overrides `.env`.
- `--overwrite-assumptions` replaces `companies/US/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
- `--ideas-log "<PATH>"` overrides the central queue log path (default `idea-screens/company-ideas-log.jsonl`).
- `--preferences-path "<PATH>"` overrides preferences path (default `preferences/user_preferences.json`).
- `--ignore-preferences` disables preference-based queue filtering and market guardrails.
- `--transcript-url "<URL>"` bypasses search and attempts extraction from one known transcript URL.
- `--transcript-max-results <N>` controls search breadth for transcript candidates (default `20`).
- `--transcript-min-body-chars <N>` controls minimum extracted body length to accept transcript text (default `1000`).

### 4. Verify outputs
Validate outputs described in `references/data-outputs.md` and `references/data-dictionary.md`, including:
- `companies/US/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/US/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/US/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/US/<TICKER>/data/filings/10-K-*.md` or `companies/US/<TICKER>/data/filings/20-F-*.md`
  - If no annual filing exists yet (common for recent IPOs), expect registration-form fallback files such as `companies/US/<TICKER>/data/filings/S-1-*.md` or `companies/US/<TICKER>/data/filings/S-1-A-*.md`
- `companies/US/<TICKER>/data/filings/8-K-*.md` (and `6-K-*.md` for FPIs) should include `### Attachment: ...` sections when exhibit content is extractable.
- `companies/US/<TICKER>/data/filings/earnings-call-<YYYY-MM-DD>-<source>.md` if a transcript was found
- `companies/US/<TICKER>/data/filings/earnings-call-fetch-report-<YYYY-MM-DD>.json` containing URL attempts and failure reasons
- `companies/US/<TICKER>/data/analyst_revenue_estimates.csv` if analyst revenue forecasts were available
- `companies/US/<TICKER>/data/analyst_price_targets.csv` when StockAnalysis price targets are available
- `companies/US/<TICKER>/data/analyst_consensus.csv` when analyst consensus is available
- `companies/US/<TICKER>/data/analyst_eps_estimates.csv` when annual EPS / EPS growth estimates are available
- `companies/US/<TICKER>/data/analyst_eps_forward_pe_estimates.csv` when annual forward P/E values are available
- `companies/US/<TICKER>/data/analyst_ratings_actions_12m.csv` when ratings table rows are available
- `companies/US/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## Troubleshooting
- If EDGAR identity errors appear, set `EDGAR_IDENTITY` in `.env` or pass `--identity`.
- If `--ticker` is omitted and no US queue candidate exists, run `$fetch-us-investment-ideas` first or pass a ticker explicitly.
- If preferences exclude US market, update `preferences/user_preferences.json` or rerun with `--ignore-preferences`.
- If transcript fetching returns nothing, ensure `beautifulsoup4` is installed and retry later.
- If annual statements fail to parse, inspect `companies/US/<TICKER>/data/financial_statements/annual/*.csv` and review `references/data-outputs.md`.

## Related References
- `references/python-setup.md`
- `references/data-outputs.md`
- `references/data-dictionary.md`
