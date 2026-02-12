# Research Workflow (LLM-First, Progressive)

## Objective
Generate a decision-grade investment write-up and scenario valuation from local company data by resolving the highest-impact investment questions in descending priority and expressing conclusions through valuation pillars.

## Execution Mode (Read First)
- This workflow is intentionally LLM-first and non-scripted.
- Do not treat this as a one-command pipeline.
- Use shell/Python snippets only as helpers for extraction or arithmetic.
- Completion requires writing all required outputs and passing the goal gate in Step 7.

## Inputs
Primary local inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`

Analyst/market expectation anchors (optional but prioritized when present):
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_revenue_estimates.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_estimates.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_forward_pe_estimates.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_price_targets.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_consensus.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_ratings_actions_12m.csv`

Optional controls:
- `preferences/user_preferences.json`
- `references/source-quality-and-search.md` for targeted external checks
- `references/historical-sec-fetch.md` for US historical SEC pulls

Drafting assets:
- `.agents/skills/run-llm-workflow/assets/investment-summary.md`
- `.agents/skills/run-llm-workflow/assets/business-and-competitive-position.md`
- `.agents/skills/run-llm-workflow/assets/financial-quality.md`
- `.agents/skills/run-llm-workflow/assets/valuation.md`
- `.agents/skills/run-llm-workflow/assets/key-risks-and-disconfirming-signals.md`
- `.agents/skills/run-llm-workflow/assets/conclusion.md`

## Step 1: Confirm Scope and Data Fitness
- Confirm ticker and as-of date explicitly.
- Confirm all evidence used is dated on or before as-of date.
- Check recent local 8-K files for announced name or ticker changes; keep package paths on current ticker unless already effective, and disclose pending changes.
- If ticker is not provided, pick from queue:
  - `python3 .agents/skills/research/scripts/company_idea_queue.py pick --task run-llm-workflow`
- Load `preferences/user_preferences.json` when present and apply strategy/report preferences.
- If local data is missing, stop and run the market fetch skill first.

## Step 2: Build the Fact Base and Market Baseline
Create two baselines before drafting conclusions.

Operating baseline (company evidence):
- Business model, segment mix, and key economics from filings.
- Financial trend summary from annual statements.

Market baseline (analyst evidence):
- Consensus stance and analyst count (`analyst_consensus.csv`).
- Price target range and implied upside/downside (`analyst_price_targets.csv`).
- Near-term revenue and EPS trajectory (`analyst_revenue_estimates.csv`, `analyst_eps_estimates.csv`).
- Implied valuation sentiment via forward P/E (`analyst_eps_forward_pe_estimates.csv`).
- Revision momentum from rating/target actions (`analyst_ratings_actions_12m.csv`).

If analyst files are unavailable or sparse, say so explicitly and use filing-guidance plus historical ranges as fallback.

## Step 3: Build an Early Lever Map
Before deep dives, write an initial 3-7 lever map with explicit valuation links:
- `Lever`: what moves intrinsic value most.
- `Direction`: what outcome improves or hurts value.
- `Why material`: sensitivity to value per share / MOS.
- `Current evidence quality`: high / medium / low.
- `Current confidence`: 0-100%.
- `Priority`: rank by `decision impact x uncertainty`.

This is your working research backlog. Update it every loop.
Then select the top 3-5 levers as provisional valuation pillars and draft a one-line assumption mapping for each (which scenario input each lever controls most).

## Step 4: Progressive Resolution Loop (Highest Impact First)
For each unresolved high-priority lever, run this loop:
1. Define the core test question (falsification + confirmation framing).
2. Pull best local evidence first (filings/statements/transcripts).
3. If still unresolved and impact is material, run targeted external checks using `references/source-quality-and-search.md`.
4. For US historical SEC evidence, use `references/sec-access-policy.md` and `references/historical-sec-fetch.md`.
5. Update lever status: `resolved`, `bounded`, or `open`.
6. Update assumptions (no change / tighten / widen / shift central case) and log the valuation impact.
7. Re-score confidence for that lever and estimate incremental insight from one more loop (`high`, `medium`, `low`).

Mandatory event-risk sweep before final assumptions:
- Check for signed/proposed M&A, take-private, spin-off, tender, or special-committee processes.
- If signed deal exists, model event-risk framing (deal-cap upside, break-risk downside) before relying on standalone compounding assumptions.

## Step 5: Build and Reconcile Valuation Inputs
- Create `valuation/inputs.yaml` using `references/valuation-method.md`.
- Match model to economics (`three-stage-dcf-fade` vs `two-stage-residual-income`).
- Make base/bull/bear assumptions explicit and evidence-backed.
- Reconcile assumptions against analyst baseline:
  - show where base case aligns with consensus,
  - and where it differs, state why with evidence.
- If analyst revisions conflict with management guidance or filing evidence, explain which source set is leading and why.

## Step 6: Compute Outputs and Draft Report
- Compute valuation outputs and write `valuation/outputs.json`.
- Draft `report.md` using `references/report-format.md`.
- Keep report concise, decision-oriented, and explicit about what is resolved vs still uncertain.
- Draft in narrative-first style:
  - lead with the argument, not raw fact lists;
  - for each pillar, show `claim -> evidence -> model input impact`;
  - explain why assumptions are central estimates rather than arbitrary midpoints.
- Include a `## Research Stop Gate` section in the report with:
  - `Thesis confidence`,
  - `Highest-impact levers`,
  - `Levers resolved`,
  - `Open thesis-critical levers`,
  - `Diminishing returns from additional research`,
  - `Research complete`,
  - `Next best research focus`.

## Step 7: Goal Gate (Stop Rule)
Stop when all conditions below are true:
- Required outputs exist and are internally consistent.
- Highest-impact levers are resolved or explicitly bounded with valuation sensitivity.
- Valuation assumptions are linked to evidence and reconciled with analyst-implied market expectations.
- Margin-of-safety conclusion matches `valuation/outputs.json` and current price input.
- The write-up clearly explains the valuation pillars and how evidence translated into model assumptions and scenario ranges.
- `Research Stop Gate` indicates:
  - high thesis confidence,
  - zero open thesis-critical levers,
  - diminishing returns from additional research.
- Remaining open items are monitoring items, not thesis-critical unknowns.
- Every factual claim has local file-path citations.

If any condition fails, continue the resolution loop instead of finalizing.

## Step 8: Queue and Improvement
- Remove ticker from queue only after Step 7 passes:
  - `python3 .agents/skills/research/scripts/company_idea_queue.py remove --ticker <TICKER>`
- Record repeatable process improvements in `docs/improvement-log.md` using `references/improvement-loop.md`.
