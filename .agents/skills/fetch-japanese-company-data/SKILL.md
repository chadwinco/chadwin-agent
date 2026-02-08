---
name: fetch-japanese-company-data
description: Fetch Japanese listed company data (profile, annual statements, transcript attempts) for this repo's research pipeline. Use when adding a TSE-listed company, refreshing `companies/TICKER/data`, or regenerating `companies/TICKER/reports/<DATE>/valuation/inputs.yaml` before LLM-driven research.
---

# Fetch Japanese Company Data

## Overview
Fetch Japanese company profile data and annual financial statements into `companies/<TICKER>/data` and bootstrap valuation assumptions in `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.

Primary market/profile source is Yahoo Finance (`yfinance`) for Japan tickers (for example `7974.T`).
For Nintendo, this skill also pulls official IR PDFs from Nintendo's own website feed and extracts local markdown files.

## Skill Path (set once)
Repo-local:

```bash
export FETCH_JAPANESE_COMPANY_DATA_ROOT=".agents/skills/fetch-japanese-company-data"
export FETCH_JAPANESE_COMPANY_DATA_CLI="$FETCH_JAPANESE_COMPANY_DATA_ROOT/scripts/add_company.py"
```

Installed skill:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export FETCH_JAPANESE_COMPANY_DATA_ROOT="$CODEX_HOME/skills/fetch-japanese-company-data"
export FETCH_JAPANESE_COMPANY_DATA_CLI="$FETCH_JAPANESE_COMPANY_DATA_ROOT/scripts/add_company.py"
```

## Quick Start
1. Follow `references/python-setup.md`.
2. Confirm identifier and as-of date with the user.
3. Run the skill script from the repo root:

```bash
python3 "$FETCH_JAPANESE_COMPANY_DATA_CLI" --ticker <JP_IDENTIFIER> --asof <YYYY-MM-DD>
```

## Workflow
1. Confirm prerequisites.
2. Confirm identifier and as-of date (do not infer from open files or prior context).
3. Run fetch/bootstrap.
4. Verify outputs.

### 1. Confirm prerequisites
- Use `references/python-setup.md` for environment setup and dependencies.

### 2. Confirm identifier and as-of date
- Only proceed if the user explicitly provided a ticker/identifier in the current request.
- Acceptable identifiers:
  - 4-digit TSE code (example: `7974`)
  - 5-digit JP code ending in `0` (example: `79740`)
  - Yahoo Japan symbol (example: `7974.T`)
  - Seeded ISINs (example: `JP3756600007` for Nintendo)
- If no identifier is specified, ask: `Which Japanese ticker should I fetch?`
- Echo back identifier and as-of date before execution.

### 3. Run fetch/bootstrap
```bash
python3 "$FETCH_JAPANESE_COMPANY_DATA_CLI" --ticker <JP_IDENTIFIER> --asof <YYYY-MM-DD>
```

Optional flags:
- `--isin <ISIN>` adds an explicit ISIN for identifier resolution.
- `--overwrite-assumptions` replaces `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
- `--transcript-url "<URL>"` bypasses search and attempts extraction from one known transcript URL.
- `--transcript-max-results <N>` controls search breadth for transcript candidates (default `20`).
- `--transcript-min-body-chars <N>` controls minimum extracted body length to accept transcript text (default `1000`).

### 4. Verify outputs
Validate outputs described in `references/data-outputs.md` and `references/data-dictionary.md`, including:
- `companies/<TICKER>/data/company_profile.csv`
- `companies/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/<TICKER>/data/source-metadata.json`
- `companies/<TICKER>/data/filings/official-ir-fetch-report-<YYYY-MM-DD>.json` (Nintendo)
- `companies/<TICKER>/data/filings/ir-document-<YYYY-MM-DD>-*.md` (Nintendo)
- `companies/<TICKER>/data/filings/earnings-call-<YYYY-MM-DD>-nintendo-co-jp.md` (Nintendo Q&A)
- `companies/<TICKER>/data/filings/earnings-call-fetch-report-<YYYY-MM-DD>.json`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## Current Limits
- This skill currently does not pull Japanese statutory filings from EDINET yet.
- Official IR PDF extraction is currently implemented for Nintendo as the first high-quality path; other issuers currently use generic transcript discovery only.

## Related References
- `references/python-setup.md`
- `references/identifier-mapping.md`
- `references/data-outputs.md`
- `references/data-dictionary.md`
