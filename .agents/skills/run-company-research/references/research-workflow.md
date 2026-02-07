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

Drafting assets:
- `.agents/skills/run-company-research/assets/investment-summary.md`
- `.agents/skills/run-company-research/assets/business-and-competitive-position.md`
- `.agents/skills/run-company-research/assets/financial-quality.md`
- `.agents/skills/run-company-research/assets/valuation.md`
- `.agents/skills/run-company-research/assets/key-risks-and-disconfirming-signals.md`
- `.agents/skills/run-company-research/assets/conclusion.md`

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
- Explicitly set and justify competitive-advantage period (`stage1_years`) and fade length.
- If the company has durable advantages, do not default to a five-year horizon.

## Step 4: Compute Valuation Outputs
- Compute scenario values with the DCF method in `references/valuation-method.md`.
- Write results to `valuation/outputs.json`.

## Step 5: Draft the Report
- Use `references/report-format.md`.
- Keep the report in the 500-900 word range.
- State intrinsic value versus current price and margin of safety clearly.

## Step 6: Run the Quality Gate
All checks below must pass before finalizing.

Scope and data:
- [ ] Ticker and as-of date are explicit.
- [ ] Required local files exist and load without errors.
- [ ] Latest filing/transcript evidence used is dated on or before the as-of date.

Evidence discipline:
- [ ] No verbatim copying from filings or transcripts.
- [ ] Every factual claim cites local file paths.

Thesis quality:
- [ ] Thesis explains why returns can persist and what can break the thesis.
- [ ] Competitive position is described with evidence.
- [ ] Capital allocation quality is assessed.

Financial quality:
- [ ] Revenue trend is quantified (CAGR plus recent year-over-year change).
- [ ] EBIT and FCF margin trends are quantified.
- [ ] ROIC proxy and leverage are evaluated.

Valuation quality:
- [ ] Base/bull/bear assumptions are explicit and defensible.
- [ ] Assumptions are written to `valuation/inputs.yaml`.
- [ ] Valuation outputs are written to `valuation/outputs.json`.
- [ ] Margin of safety reconciles with current price and value per share.
- [ ] Competitive-advantage period and fade assumptions are justified with filing evidence.
- [ ] Terminal growth and terminal margin are explicit and economically plausible.

Output quality:
- [ ] Report is concise (target: 500-900 words) and decision-oriented.
- [ ] Top 3-5 risks are prioritized by cash-flow impact.
- [ ] Conclusion states a clear action at current price.
- [ ] Improvement notes are added to `docs/improvement-log.md`.

## Step 7: Log and Improve
- Process improvements: append rows to `docs/improvement-log.md` using `references/improvement-loop.md`.
