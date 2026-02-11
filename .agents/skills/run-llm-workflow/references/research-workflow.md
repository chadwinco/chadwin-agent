# Research Workflow (LLM-First)

## Objective
Generate a concise investment write-up and a scenario valuation from local company data.

## Execution Mode (Read First)
- This workflow is intentionally LLM-first and non-scripted.
- Do not treat this as a one-command pipeline.
- Use shell/Python snippets only as helpers for extraction or arithmetic.
- Completion requires writing all required outputs and passing Step 6 quality gates.

## Inputs
Primary local inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_estimates.csv` (optional)

Legacy fallback paths:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/income_statement_annual.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/balance_sheet_annual.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/cash_flow_statement_annual.csv`

Drafting assets:
- `.agents/skills/run-llm-workflow/assets/investment-summary.md`
- `.agents/skills/run-llm-workflow/assets/business-and-competitive-position.md`
- `.agents/skills/run-llm-workflow/assets/financial-quality.md`
- `.agents/skills/run-llm-workflow/assets/valuation.md`
- `.agents/skills/run-llm-workflow/assets/key-risks-and-disconfirming-signals.md`
- `.agents/skills/run-llm-workflow/assets/conclusion.md`

## Step 1: Confirm Scope
- Confirm ticker and as-of date explicitly.
- If ticker is not provided, pick the next candidate from the central queue:
  - `python3 .agents/skills/research/scripts/company_idea_queue.py pick --task run-llm-workflow`
- Use filings/transcripts dated on or before the as-of date.
- If local data is missing, stop and run the market-appropriate fetch skill (`$fetch-us-company-data` or `$fetch-japanese-company-data`).

## Step 2: Build the Fact Base
- Use `grep` against `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md` for:
  - business model and segment mix
  - competitive strengths and weak points
  - capital allocation behavior
  - growth drivers and risk factors
- Extract key financial trends from annual statements:
  - For most non-financial businesses:
    - revenue CAGR (3-5 years)
    - EBIT margin trend
    - FCF margin trend
    - leverage (net debt, net debt/EBITDA)
    - ROIC proxy
  - For financials (insurers, banks, brokers, asset managers):
    - premium/fee or revenue growth trend
    - operating profitability proxy (typically pre-tax or operating income margin)
    - ROE trend and book value per share trend
    - capital and liquidity sensitivity (RBC disclosures, ratings triggers, funding sources)
    - debt-to-equity or other capital-structure measures (avoid net debt/EBITDA if not meaningful)
- Track source file paths for every factual claim.

## Step 3: Build Valuation Inputs
- Create `valuation/inputs.yaml` using `references/valuation-method.md`.
- Choose a valuation model that matches business economics:
  - `three-stage-dcf-fade` for businesses where FCF is decision-useful.
  - `two-stage-residual-income` for financials where book value and ROE are more reliable anchors than FCF.
- Keep assumptions explicit for base, bull, and bear.
- Ensure base assumptions align with observed history.
- For DCF runs, explicitly set and justify competitive-advantage period (`stage1_years`) and fade length.
- If the company has durable advantages, do not default to a five-year horizon.

## Step 4: Compute Valuation Outputs
- Compute scenario values with the selected method in `references/valuation-method.md`.
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
- [ ] Workflow was executed as an LLM task, not delegated to a deterministic end-to-end script.

Evidence discipline:
- [ ] No verbatim copying from filings or transcripts.
- [ ] Every factual claim cites local file paths.

Thesis quality:
- [ ] Thesis explains why returns can persist and what can break the thesis.
- [ ] Competitive position is described with evidence.
- [ ] Capital allocation quality is assessed.

Financial quality:
- [ ] Revenue trend is quantified (CAGR plus recent year-over-year change).
- [ ] For non-financials: EBIT and FCF margin trends are quantified.
- [ ] For financials: ROE/book-value trend and capital/liquidity sensitivity are quantified.
- [ ] A returns metric (ROIC or ROE, depending on business model) and leverage/capital structure are evaluated.

Valuation quality:
- [ ] Base/bull/bear assumptions are explicit and defensible.
- [ ] Assumptions are written to `valuation/inputs.yaml`.
- [ ] Valuation outputs are written to `valuation/outputs.json`.
- [ ] Margin of safety reconciles with current price and value per share.
- [ ] Valuation method matches business model economics (DCF vs. residual income).
- [ ] If using DCF: competitive-advantage period/fade and terminal margin assumptions are explicit and justified.
- [ ] If using residual income: ROE, cost of equity, payout, and terminal assumptions are explicit and justified.

Output quality:
- [ ] Report is concise (target: 500-900 words) and decision-oriented.
- [ ] Top 3-5 risks are prioritized by cash-flow impact.
- [ ] Conclusion states a clear action at current price.
- [ ] Improvement notes are added to `docs/improvement-log.md`.

## Step 7: Log and Improve
- If all required outputs are complete, remove the researched ticker from the central queue:
  - `python3 .agents/skills/research/scripts/company_idea_queue.py remove --ticker <TICKER>`
- Process improvements: append rows to `docs/improvement-log.md` using `references/improvement-loop.md`.
