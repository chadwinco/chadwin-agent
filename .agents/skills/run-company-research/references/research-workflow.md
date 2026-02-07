# Research Workflow (LLM-First)

## Objective
Generate a concise investment write-up and a scenario valuation from local company data.

## Inputs
Primary local inputs:
- `companies/<TICKER>/data/company_profile.csv`
- `companies/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/<TICKER>/data/filings/*.md`
- `companies/<TICKER>/data/analyst_estimates.csv` (optional)

Legacy fallback paths:
- `companies/<TICKER>/data/income_statement_annual.csv`
- `companies/<TICKER>/data/balance_sheet_annual.csv`
- `companies/<TICKER>/data/cash_flow_statement_annual.csv`

Drafting prompts:
- `.agents/skills/run-company-research/prompts/investment-summary.md`
- `.agents/skills/run-company-research/prompts/business-and-competitive-position.md`
- `.agents/skills/run-company-research/prompts/financial-quality.md`
- `.agents/skills/run-company-research/prompts/valuation.md`
- `.agents/skills/run-company-research/prompts/key-risks-and-disconfirming-signals.md`
- `.agents/skills/run-company-research/prompts/conclusion.md`

## Step 1: Confirm Scope
- Confirm ticker and as-of date explicitly.
- Use filings/transcripts dated on or before the as-of date.
- If local data is missing, stop and run `$fetch-company-data`.

## Step 2: Build the Fact Base
- Use `grep` against `companies/<TICKER>/data/filings/*.md` for:
  - business model and segment mix
  - competitive strengths and weak points
  - capital allocation behavior
  - growth drivers and risk factors
- Extract key financial trends from annual statements:
  - revenue CAGR (3-5 years)
  - EBIT margin trend
  - FCF margin trend
  - leverage (net debt, net debt/EBITDA)
  - ROIC proxy
- Track source file paths for every factual claim.

## Step 3: Build Valuation Inputs
- Create `valuation/inputs.yaml` using `references/valuation-method.md`.
- Keep assumptions explicit for base, bull, and bear.
- Ensure base assumptions align with observed history.

## Step 4: Compute Valuation Outputs
- Compute scenario values with the DCF method in `references/valuation-method.md`.
- Write results to `valuation/outputs.json`.

## Step 5: Draft the Report
- Use `references/report-format.md`.
- Keep the report in the 500-900 word range.
- State intrinsic value versus current price and margin of safety clearly.

## Step 6: Run the Quality Gate
- Apply `references/research-checklist.md`.
- Fix all unchecked items before finalizing.

## Step 7: Log and Improve
- External sources: append rows to `docs/source-log.md` using `references/source-log-format.md`.
- Process improvements: append rows to `docs/improvement-log.md` using `references/improvement-loop.md`.
