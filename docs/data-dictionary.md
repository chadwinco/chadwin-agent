# Data Dictionary

This repo expects company financial data under `companies/<TICKER>/data`. The pipeline uses these files and columns.

## Required Files
- `company_profile.csv`
- `financials/annual/income_statement.csv`
- `financials/annual/balance_sheet.csv`
- `financials/annual/cash_flow_statement.csv`

## Optional Files
- `financials/quarterly/` (full EDGAR statement exports)
- `earnings-call-*.md` (latest earnings call transcript)
- `income_statement_annual.csv` (derived summary)
- `balance_sheet_annual.csv` (derived summary)
- `cash_flow_statement_annual.csv` (derived summary)
- `key_metrics.csv`
- `ratios.csv`
- `analyst_estimates.csv` (analyst revenue forecasts)
- Transcripts, filings, and other markdown files

## Core Columns (Required)
### `income_statement_annual.csv`
- `date`, `fiscalYear`, `period`
- `revenue`
- `grossProfit` (for gross margin)
- `ebit`, `ebitda`
- `incomeBeforeTax`, `incomeTaxExpense`
- `netIncome`
- `weightedAverageShsOut`, `weightedAverageShsOutDil`

### `balance_sheet_annual.csv`
- `date`, `fiscalYear`, `period`
- `cashAndCashEquivalents`
- `totalAssets`
- `totalDebt`
- `totalEquity`
- `netDebt` (preferred; otherwise computed)

### `cash_flow_statement_annual.csv`
- `date`, `fiscalYear`, `period`
- `operatingCashFlow`
- `capitalExpenditure`
- `freeCashFlow` (preferred; otherwise computed)

### `company_profile.csv`
- `symbol`, `companyName`, `currency`
- `price`, `marketCap`, `beta`, `lastDividend`, `range`, `change`, `changePercentage`, `volume`
- `cik`, `isin`, `cusip`
- `exchange`, `exchangeFullName`
- `industry`, `sector`, `country`, `fullTimeEmployees`, `ceo`
- `website`, `phone`, `address`, `city`, `state`, `zip`
- `isEtf`, `isAdr`, `isActivelyTrading`

Values may be blank when the source data is unavailable, but the column set should be present.

### `analyst_estimates.csv`
- `metric` (currently `revenue`)
- `fiscalYear`
- `high`, `avg`, `low` (forecast values in absolute dollars)
- `source` (URL)
- `retrieved` (YYYY-MM-DD)

## Derived Metrics (Definitions)
- Revenue growth: year-over-year % change.
- Gross margin: `grossProfit / revenue`.
- EBIT margin: `ebit / revenue`.
- FCF margin: `freeCashFlow / revenue`.
- ROIC: `NOPAT / Invested Capital`.
  - `NOPAT = ebit * (1 - tax_rate)`.
  - `tax_rate = incomeTaxExpense / incomeBeforeTax` (fallback to 21%).
  - `Invested Capital = totalDebt + totalEquity - cashAndCashEquivalents`.
- Reinvestment rate: `abs(capitalExpenditure) / revenue`.
- Leverage: `netDebt / ebitda`.

## EDGAR Financial Statement Exports
When EDGAR data is fetched, the pipeline stores full statements in:
- `companies/<TICKER>/data/financials/annual/`
- `companies/<TICKER>/data/financials/quarterly/`

Each directory contains:
- `income_statement.csv`
- `balance_sheet.csv`
- `cash_flow_statement.csv`
- `statement_of_equity.csv`
- `comprehensive_income.csv`

These are the canonical statement sources. The `*_annual.csv` and `*_quarterly.csv` files in the root `data/` folder are derived summaries used by the analysis workflow.

## Date Alignment
For each fiscal year, income, balance sheet, and cash flow rows should align on `fiscalYear` and be within the same `date` range. The quality checker flags mismatches.
