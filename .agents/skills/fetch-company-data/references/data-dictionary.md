# Data Dictionary

This repo expects company financial data under `companies/<TICKER>/data`. The pipeline uses these files and columns.

## Required Files
- `company_profile.csv`
- `financial_statements/annual/income_statement.csv`
- `financial_statements/annual/balance_sheet.csv`
- `financial_statements/annual/cash_flow_statement.csv`

## Optional Files
- `financial_statements/quarterly/` (full EDGAR statement exports)
- `filings/` (10-K/10-Q/8-K markdown + earnings call transcripts)
  - For recent IPOs without annual reports, registration forms such as `S-1`/`S-1-A` and `F-1`/`F-1-A` may be present instead.
- `analyst_estimates.csv` (analyst revenue forecasts)

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

## Normalized Annual Frames (Pipeline Internal)
The loader derives normalized annual frames from `financial_statements/annual/*.csv` with these columns:

### Income Frame
- `date`, `fiscalYear`, `period`
- `revenue`
- `grossProfit`
- `ebit`, `ebitda`
- `incomeBeforeTax`, `incomeTaxExpense`
- `netIncome`
- `weightedAverageShsOut`, `weightedAverageShsOutDil`

### Balance Sheet Frame
- `date`, `fiscalYear`, `period`
- `cashAndCashEquivalents`
- `totalAssets`
- `totalDebt`
- `totalEquity`
- `netDebt` (computed when source does not provide it)

### Cash Flow Frame
- `date`, `fiscalYear`, `period`
- `operatingCashFlow`
- `capitalExpenditure`
- `freeCashFlow` (computed when source does not provide it)

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
- `companies/<TICKER>/data/financial_statements/annual/`
- `companies/<TICKER>/data/financial_statements/quarterly/`

Each directory contains:
- `income_statement.csv`
- `balance_sheet.csv`
- `cash_flow_statement.csv`
- `statement_of_equity.csv`
- `comprehensive_income.csv`

These are the canonical statement sources used by the analysis workflow.

## Filings and Transcripts
Filings and transcript markdown files are stored under:
- `companies/<TICKER>/data/filings/`

## Date Alignment
For each fiscal year, income, balance sheet, and cash flow rows should align on `fiscalYear` and be within the same `date` range. The quality checker flags mismatches.
