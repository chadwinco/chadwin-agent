# US Fetch Data Contract and Dictionary (EDGAR)

This document is the single reference for fetch output expectations and column definitions for US company packages.

## Output Roots
- Company data root: `.chadwin-data/companies/US/<TICKER>/data`
- Bootstrap valuation output: `.chadwin-data/companies/US/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`

## Output Contract

### Required Outputs
- `company_profile.csv`
- `financial_statements/annual/income_statement.csv`
- `financial_statements/annual/balance_sheet.csv`
- `financial_statements/annual/cash_flow_statement.csv`

### Optional Outputs
- `financial_statements/quarterly/*.csv`
- `filings/10-K-*.md` or `filings/20-F-*.md`
- `filings/10-Q-*.md`, `filings/8-K-*.md`, `filings/6-K-*.md`
- `filings/S-1-*.md`, `filings/S-1-A-*.md`, `filings/F-1-*.md`, `filings/F-1-A-*.md`
- `filings/earnings-call-<YYYY-MM-DD>-<source>.md`
- `analyst_revenue_estimates.csv`
- `analyst_price_targets.csv`
- `analyst_consensus.csv`
- `analyst_eps_estimates.csv`
- `analyst_eps_forward_pe_estimates.csv`
- `analyst_ratings_actions_12m.csv`

For recent IPOs without annual reports, registration forms such as `S-1`/`S-1-A` and `F-1`/`F-1-A` may be present instead of `10-K`/`20-F`.

For `8-K`/`6-K`, markdown should include attachment sections (`### Attachment: ...`) when exhibit text is extractable.

## File Dictionaries

### `company_profile.csv`
- `symbol`, `companyName`, `currency`
- `price`, `marketCap`, `beta`, `lastDividend`, `range`, `change`, `changePercentage`, `volume`
- `cik`, `isin`, `cusip`
- `exchange`, `exchangeFullName`
- `industry`, `sector`, `country`, `fullTimeEmployees`, `ceo`
- `website`, `phone`, `address`, `city`, `state`, `zip`
- `isEtf`, `isAdr`, `isActivelyTrading`

Values may be blank when source data is unavailable, but the column set should be present.

### `analyst_revenue_estimates.csv`
- `metric` (currently `revenue`)
- `fiscalYear`
- `high`, `avg`, `low` (forecast values in absolute dollars)
- `highRaw`, `avgRaw`, `lowRaw` (raw page text; captures locked values such as `Pro`)
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

### `analyst_price_targets.csv`
- `low`, `average`, `median`, `high` (price targets in absolute dollars)
- `lowChangePct`, `averageChangePct`, `medianChangePct`, `highChangePct` (percent upside/downside)
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

### `analyst_consensus.csv`
- `consensus` (for example `Buy`, `Hold`, `Sell`)
- `analystCount`
- `averagePriceTarget`
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

### `analyst_eps_estimates.csv`
- `fiscalYear`
- `periodEnding`
- `eps`
- `epsGrowthPct` (percentage points)
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

### `analyst_eps_forward_pe_estimates.csv`
- `fiscalYear`
- `periodEnding`
- `forwardPE`
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

### `analyst_ratings_actions_12m.csv`
- `rating`
- `action`
- `priceTarget`, `priceTargetOld`, `priceTargetNew`
- `upsidePct`
- `date` (YYYY-MM-DD)
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

## Normalized Annual Frames (Pipeline Internal)
The loader derives normalized annual frames from `financial_statements/annual/*.csv`.

### Income Frame Columns
- `date`, `fiscalYear`, `period`
- `revenue`
- `grossProfit`
- `ebit`, `ebitda`
- `incomeBeforeTax`, `incomeTaxExpense`
- `netIncome`
- `weightedAverageShsOut`, `weightedAverageShsOutDil`

### Balance Sheet Frame Columns
- `date`, `fiscalYear`, `period`
- `cashAndCashEquivalents`
- `totalAssets`
- `totalDebt`
- `totalEquity`
- `netDebt` (computed when source does not provide it)

### Cash Flow Frame Columns
- `date`, `fiscalYear`, `period`
- `operatingCashFlow`
- `capitalExpenditure`
- `freeCashFlow` (computed when source does not provide it)

## Derived Metrics
- Revenue growth: year-over-year percent change.
- Gross margin: `grossProfit / revenue`.
- EBIT margin: `ebit / revenue`.
- FCF margin: `freeCashFlow / revenue`.
- ROIC: `NOPAT / Invested Capital`.
- NOPAT: `ebit * (1 - tax_rate)`.
- Tax rate: `incomeTaxExpense / incomeBeforeTax` (fallback 21%).
- Invested Capital: `totalDebt + totalEquity - cashAndCashEquivalents`.
- Reinvestment rate: `abs(capitalExpenditure) / revenue`.
- Leverage: `netDebt / ebitda`.

## EDGAR Statement Exports
When EDGAR data is fetched, the pipeline stores full statements in:
- `.chadwin-data/companies/US/<TICKER>/data/financial_statements/annual/`
- `.chadwin-data/companies/US/<TICKER>/data/financial_statements/quarterly/`

Each directory can include:
- `income_statement.csv`
- `balance_sheet.csv`
- `cash_flow_statement.csv`
- `statement_of_equity.csv`
- `comprehensive_income.csv`

These files are the canonical statement sources for downstream analysis.

## Consistency Check
For each fiscal year, income, balance sheet, and cash flow rows should align on `fiscalYear` and be within a consistent date range. The quality checker flags mismatches.
