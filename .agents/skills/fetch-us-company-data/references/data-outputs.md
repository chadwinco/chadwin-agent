# Fetch Output Contract (US / EDGAR)

The fetch step writes data under `companies/US/<TICKER>/data`.

## Required outputs
- `company_profile.csv`
- `financial_statements/annual/income_statement.csv`
- `financial_statements/annual/balance_sheet.csv`
- `financial_statements/annual/cash_flow_statement.csv`

## Optional outputs
- `filings/10-K-*.md` or `filings/20-F-*.md`
- `filings/10-Q-*.md`, `filings/8-K-*.md`, `filings/6-K-*.md`
  - For `8-K`/`6-K`, markdown should include attachment sections (`### Attachment: ...`) when exhibit text is extractable.
- `filings/S-1-*.md`, `filings/S-1-A-*.md`, `filings/F-1-*.md`, `filings/F-1-A-*.md`
- `filings/earnings-call-<YYYY-MM-DD>-<source>.md`
- `financial_statements/quarterly/*.csv`
- `analyst_revenue_estimates.csv`
- `analyst_price_targets.csv`
- `analyst_consensus.csv`
- `analyst_eps_estimates.csv`
- `analyst_eps_forward_pe_estimates.csv`
- `analyst_ratings_actions_12m.csv`

## Bootstrap output
- `companies/US/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## `company_profile.csv` columns
- `symbol`, `companyName`, `currency`
- `price`, `marketCap`, `beta`, `lastDividend`, `range`, `change`, `changePercentage`, `volume`
- `cik`, `isin`, `cusip`
- `exchange`, `exchangeFullName`
- `industry`, `sector`, `country`, `fullTimeEmployees`, `ceo`
- `website`, `phone`, `address`, `city`, `state`, `zip`
- `isEtf`, `isAdr`, `isActivelyTrading`
