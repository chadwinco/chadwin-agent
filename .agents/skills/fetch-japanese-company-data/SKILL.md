---
name: fetch-japanese-company-data
description: Fetch Japanese listed company data (profile, annual statements, transcript attempts) for this repo's research pipeline. Use when adding a TSE-listed company, refreshing `companies/Japan/<TICKER>/data`, or regenerating `companies/Japan/<TICKER>/reports/<DATE>/valuation/inputs.yaml` before LLM-driven research.
---

# Fetch Japanese Company Data

## Overview
Fetch Japanese company profile data and annual financial statements into `companies/Japan/<TICKER>/data` and bootstrap valuation assumptions in `companies/Japan/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
When present, `preferences/user_preferences.json` is respected by default for queue selection and Japan market guardrails.

Primary market/profile source is Yahoo Finance (`yfinance`) for Japan tickers (for example `7974.T`).
For selected issuers, this skill also pulls official IR PDFs and extracts local markdown files:
- Nintendo (`7974` / `79740`) from Nintendo's IR news feed.
- Fast Retailing (`9983` / `99830`) from Fast Retailing's English IR library and IR news pages.

Fast Retailing deep-search sources currently used:
- `https://www.fastretailing.com/eng/ir/library/earning.html`
- `https://www.fastretailing.com/eng/ir/library/annual.html`
- `https://www.fastretailing.com/eng/ir/news/`

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
2. Confirm as-of date with the user. Identifier is optional.
3. Run the skill script from the repo root:

```bash
python3 "$FETCH_JAPANESE_COMPANY_DATA_CLI" --asof <YYYY-MM-DD> [--ticker <JP_IDENTIFIER>]
```

## Workflow
1. Confirm prerequisites.
2. Resolve identifier and as-of date.
3. Run fetch/bootstrap.
4. Verify outputs.

### 1. Confirm prerequisites
- Use `references/python-setup.md` for environment setup and dependencies.

### 2. Resolve identifier and as-of date
- Acceptable identifiers:
  - 4-digit TSE code (example: `7974`)
  - 5-digit JP code ending in `0` (example: `79740`)
  - Yahoo Japan symbol (example: `7974.T`)
  - Seeded ISINs (example: `JP3756600007` for Nintendo)
- If `--ticker` is provided, use it.
- If `--ticker` is omitted, select the next JP candidate from `idea-screens/company-ideas-log.jsonl`, filtered by preferences when present.
- If the queue log has no JP candidate, stop and ask for a ticker.
- If preferences exclude Japan market, stop and ask to update preferences or rerun with `--ignore-preferences`.
- Echo back the resolved identifier and as-of date before execution.

### 3. Run fetch/bootstrap
```bash
python3 "$FETCH_JAPANESE_COMPANY_DATA_CLI" --asof <YYYY-MM-DD> [--ticker <JP_IDENTIFIER>]
```

Optional flags:
- `--isin <ISIN>` adds an explicit ISIN for identifier resolution.
- `--overwrite-assumptions` replaces `companies/Japan/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
- `--ideas-log "<PATH>"` overrides the central queue log path (default `idea-screens/company-ideas-log.jsonl`).
- `--preferences-path "<PATH>"` overrides preferences path (default `preferences/user_preferences.json`).
- `--ignore-preferences` disables preference-based queue filtering and market guardrails.
- `--transcript-url "<URL>"` bypasses search and attempts extraction from one known transcript URL.
- `--transcript-max-results <N>` controls search breadth for transcript candidates (default `20`).
- `--transcript-min-body-chars <N>` controls minimum extracted body length to accept transcript text (default `1000`).

### 4. Verify outputs
Validate outputs described in `references/data-outputs.md` and `references/data-dictionary.md`, including:
- `companies/Japan/<TICKER>/data/company_profile.csv`
- `companies/Japan/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/Japan/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/Japan/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/Japan/<TICKER>/data/source-metadata.json`
- `companies/Japan/<TICKER>/data/filings/official-ir-fetch-report-<YYYY-MM-DD>.json` (supported issuers)
- `companies/Japan/<TICKER>/data/filings/ir-document-<YYYY-MM-DD>-*.md` (supported issuers)
- `companies/Japan/<TICKER>/data/filings/earnings-call-<YYYY-MM-DD>-nintendo-co-jp.md` (Nintendo Q&A)
- `companies/Japan/<TICKER>/data/filings/earnings-call-fetch-report-<YYYY-MM-DD>.json`
- `companies/Japan/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## Current Limits
- This skill currently does not pull Japanese statutory filings from EDINET yet.
- Official IR PDF extraction is currently implemented for Nintendo and Fast Retailing.
- For other issuers, transcript discovery remains generic and official-IR collection may require manual operator-led search and capture.

## Related References
- `references/python-setup.md`
- `references/identifier-mapping.md`
- `references/data-outputs.md`
- `references/data-dictionary.md`
