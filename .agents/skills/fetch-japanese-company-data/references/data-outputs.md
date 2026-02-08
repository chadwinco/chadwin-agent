# Fetch Output Contract (Japan / Yahoo Finance)

The fetch step writes data under `companies/<TICKER>/data`.

## Required outputs
- `company_profile.csv`
- `financial_statements/annual/income_statement.csv`
- `financial_statements/annual/balance_sheet.csv`
- `financial_statements/annual/cash_flow_statement.csv`

## Optional outputs
- `filings/earnings-call-<YYYY-MM-DD>-<source>.md`
- `filings/earnings-call-fetch-report-<YYYY-MM-DD>.json`
- `filings/official-ir-fetch-report-<YYYY-MM-DD>.json` (supported issuers: Nintendo, Fast Retailing)
- `filings/ir-document-<YYYY-MM-DD>-*.md` (supported issuers: Nintendo, Fast Retailing)
- `analyst_estimates.csv`

## Metadata output
- `source-metadata.json`

## Bootstrap output
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## `company_profile.csv` columns
- `symbol`, `companyName`, `currency`
- `price`, `marketCap`, `beta`, `lastDividend`, `range`, `change`, `changePercentage`, `volume`
- `cik`, `isin`, `cusip`
- `exchange`, `exchangeFullName`
- `industry`, `sector`, `country`, `fullTimeEmployees`, `ceo`
- `website`, `phone`, `address`, `city`, `state`, `zip`
- `isEtf`, `isAdr`, `isActivelyTrading`
