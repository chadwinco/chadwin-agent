# Data Dictionary (Japan / Yahoo Finance)

This repo expects company financial data under `companies/<TICKER>/data`. The pipeline uses these files and columns.

## Required Files
- `company_profile.csv`
- `financial_statements/annual/income_statement.csv`
- `financial_statements/annual/balance_sheet.csv`
- `financial_statements/annual/cash_flow_statement.csv`

## Optional Files
- `filings/` (earnings call transcript markdown + fetch report)
- `filings/official-ir-fetch-report-<YYYY-MM-DD>.json` and `filings/ir-document-*.md` (official company IR document captures; Nintendo path available)
- `analyst_estimates.csv` (if another process populates analyst forecasts)

### `company_profile.csv`
- `symbol`, `companyName`, `currency`
- `price`, `marketCap`, `beta`, `lastDividend`, `range`, `change`, `changePercentage`, `volume`
- `cik`, `isin`, `cusip`
- `exchange`, `exchangeFullName`
- `industry`, `sector`, `country`, `fullTimeEmployees`, `ceo`
- `website`, `phone`, `address`, `city`, `state`, `zip`
- `isEtf`, `isAdr`, `isActivelyTrading`

Values may be blank when source data is unavailable, but the column set should be present.

## Annual Statement Row Contract
Each annual statement CSV is stored in wide format with:
- Leading columns: `concept`, `label`
- Fiscal period columns: `YYYY-MM-DD`

Concept and label mappings are normalized to the same schema used by the US fetch flow so downstream loaders can compute metrics consistently.
Rows include both required mapped metrics and additional source rows to preserve available financial detail.

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
- `netDebt`

### Cash Flow Frame
- `date`, `fiscalYear`, `period`
- `operatingCashFlow`
- `capitalExpenditure`
- `freeCashFlow`

## Derived Metrics (Definitions)
- Revenue growth: year-over-year % change.
- Gross margin: `grossProfit / revenue`.
- EBIT margin: `ebit / revenue`.
- FCF margin: `freeCashFlow / revenue`.
- ROIC: `NOPAT / Invested Capital`.
- Reinvestment rate: `abs(capitalExpenditure) / revenue`.
- Leverage: `netDebt / ebitda`.
