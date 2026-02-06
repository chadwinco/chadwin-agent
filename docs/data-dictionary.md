# Data Dictionary

This repo expects company financial data under `companies/<TICKER>/data`. The pipeline uses these files and columns.

## Required Files
- `income_statement_annual.csv`
- `balance_sheet_annual.csv`
- `cash_flow_statement_annual.csv`
- `company_profile.csv`

## Optional Files
- `key_metrics.csv`
- `ratios.csv`
- `analyst_estimates.csv`
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
- `price`, `marketCap`
- `industry`, `sector`
- `description`, `website`

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

## Date Alignment
For each fiscal year, income, balance sheet, and cash flow rows should align on `fiscalYear` and be within the same `date` range. The quality checker flags mismatches.
