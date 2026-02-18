# Research Workflow (LLM-First, Progressive, Baseline + Fetch-On-Demand)

## Objective
Generate a decision-grade investment write-up and scenario valuation by resolving the highest-impact investment questions in descending priority, fetching evidence as needed, and expressing conclusions through valuation pillars.

## Execution Mode (Read First)
- This workflow is intentionally LLM-first and non-scripted.
- Do not treat this as a one-command pipeline.
- Use shell/Python snippets only as helpers for extraction or arithmetic.
- Completion requires writing all required outputs and passing the goal gate in Step 8.
- Before ad-hoc helper commands, verify path targets exist from repo root (`pwd`, `test -d .agents`).
- For file discovery, prefer `rg --files <path>` before targeted `rg -n ... <path>`.

## Inputs
Initial local evidence (may be partial):
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/income_statement.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/balance_sheet.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/cash_flow_statement.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`

Market-expectation anchors (optional; fetch when useful):
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_revenue_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_forward_pe_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_price_targets.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_consensus.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_ratings_actions_12m.csv`

Controls and references:
- `<DATA_ROOT>/user_preferences.json`
- `references/source-quality-and-search.md`
- `references/sec-access-policy.md`
- `references/historical-sec-fetch.md`

Drafting assets:
- `.agents/skills/chadwin-research/assets/investment-summary.md`
- `.agents/skills/chadwin-research/assets/business-and-competitive-position.md`
- `.agents/skills/chadwin-research/assets/financial-quality.md`
- `.agents/skills/chadwin-research/assets/valuation.md`
- `.agents/skills/chadwin-research/assets/key-risks-and-disconfirming-signals.md`
- `.agents/skills/chadwin-research/assets/conclusion.md`

## Step 1: Confirm Scope, Run Baseline Filing Fetch, and Build an Initial Evidence Map
- Confirm ticker and as-of date explicitly.
- Confirm all evidence used is dated on or before as-of date.
- If ticker is missing, pick from queue:
  - `python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py pick --task chadwin-research`
- If queue is empty or stale for the active objective, run `$fetch-us-investment-ideas`, append ideas to queue, and pick again.
- Load `<DATA_ROOT>/user_preferences.json` when present and apply strategy/report preferences.
- Run baseline filing fetch coverage before deep lever analysis:
  - latest `10-K` (or latest `20-F` for FPIs),
  - all `10-Q` filings since latest `10-K` (US issuers),
  - all `8-K` (or `6-K` for FPIs) filings since the most recent annual or quarterly filing above.
- Include attachments when available and enforce the as-of cutoff on baseline pulls.
- Create an evidence map from currently available files:
  - what is already available,
  - what appears stale,
  - what is missing for thesis-critical questions.

## Step 2: Build an Early Lever Map and Data-Need Backlog
Before deep dives, write an initial 3-7 lever map:
- `Lever`
- `Direction`
- `Why material`
- `Current evidence quality` (high/medium/low)
- `Current confidence` (0-100%)
- `Priority` (`decision impact x uncertainty`)
- `Evidence needed next`

Use this as a working backlog. Update continuously.

## Step 3: Progressive Resolution Loop (Research + Fetch)
For each unresolved high-priority lever, run this loop:
1. Define the core test question (falsification + confirmation framing).
2. Pull best local evidence first.
3. If evidence is insufficient and impact is material, fetch targeted evidence on demand.
   - US SEC retrieval default: `$fetch-us-company-data` using a plain-language objective.
   - Keep baseline filing coverage complete first, then request lever-specific incremental fetches.
   - Keep fetch requests focused to the active lever; avoid broad undirected pulls.
   - Enforce as-of cutoff in every fetch objective.
4. Validate fetched artifacts (date bounds, relevance, parse quality, duplicates).
5. Update lever status: `resolved`, `bounded`, or `open`.
6. Update assumptions (no change / tighten / widen / shift central case) and log valuation impact.
7. Re-score confidence and estimate incremental value of one more loop (`high`/`medium`/`low`).

Mandatory event-risk sweep before final assumptions:
- Check for signed/proposed M&A, take-private, spin-off, tender, or special-committee processes.
- If signed deal exists, use event-risk framing (deal-cap upside, break-risk downside) before relying on standalone compounding assumptions.
- Verify current-report coverage is recent enough for event-risk checks (for US names, ensure `8-K` evidence covers at least the last 6 months); if local filings only include the latest annual filing and no recent current reports, run a targeted fetch before finalizing assumptions.

## Step 4: Build and Reconcile Market Baseline
Create/update market baseline using available analyst files and fetched expectations data:
- consensus stance and analyst count,
- target range and implied upside/downside,
- near-term revenue/EPS trajectory,
- revisions and momentum.

If analyst data is unavailable, say so explicitly and use filing guidance plus historical ranges as fallback.

## Step 5: Build and Reconcile Valuation Inputs
- Create `valuation/inputs.yaml` using `references/valuation-method.md`.
- Match model to economics (`three-stage-dcf-fade` vs `two-stage-residual-income`).
- Make base/bull/bear assumptions explicit and evidence-backed.
- Reconcile assumptions against market baseline:
  - where base case aligns,
  - where it differs and why.

## Step 6: Compute Outputs and Draft Report
- Compute valuation outputs and write `valuation/outputs.json`.
- Draft `report.md` using `references/report-format.md`.
- Keep report concise and decision-oriented.
- Use narrative-first argument structure:
  - `claim -> evidence -> model input impact`.
- Include `## Research Stop Gate` with:
  - `Thesis confidence`
  - `Highest-impact levers`
  - `Levers resolved`
  - `Open thesis-critical levers`
  - `Diminishing returns from additional research`
  - `Research complete`
  - `Next best research focus`

## Step 7: Citation and Consistency Check
Before final gate:
- Every factual claim must cite local file paths in ticker-root format (for example, `[Source: `AMZN/data/financial_statements/annual/cash_flow_statement.csv`]`).
- Ensure date consistency against as-of date.
- Ensure valuation outputs reconcile with narrative conclusions.
- Ensure margin-of-safety statement matches `valuation/outputs.json` and current price input.

## Step 8: Goal Gate (Stop Rule)
Stop when all are true:
- Required outputs exist and are internally consistent.
- Highest-impact levers are resolved or bounded with sensitivity.
- Assumptions are evidence-linked and reconciled vs available market expectations.
- Margin-of-safety conclusion matches valuation outputs.
- `Research Stop Gate` indicates:
  - high thesis confidence,
  - zero open thesis-critical levers,
  - diminishing returns from additional research.
- Remaining open items are monitoring items, not thesis-critical unknowns.

If any condition fails, continue Step 3 instead of finalizing.

## Step 9: Queue and Mandatory Post-Run Introspection
- Remove ticker from queue only after Step 8 passes:
  - `python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py remove --ticker <TICKER>`
- Run post-run introspection using `references/improvement-loop.md`.
- Apply smallest same-run workflow/reference improvement when repeatable workflow gaps are found.
- Record in `improvement-log.md` only when a real process improvement is implemented.
