# Deep Research Workflow (Falsification-First)

## Objective
Produce a revised investment view after aggressively testing whether the baseline thesis can fail.

Required deliverables:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`
- `deep-dive-plan.md`
- `deep-dive-changes.md`
- `third-party-sources.md`

## Execution Mode (Read First)
- This is an LLM workflow, not a one-command script.
- Use deterministic tools only where they add reliability (fetching, parsing, calculations).
- Completion requires all outputs plus passed quality gate checks in Step 8.

## Inputs
Baseline package:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/report.md`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/valuation/inputs.yaml`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/valuation/outputs.json`

Company evidence base:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/...`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_estimates.csv` (optional)

Optional controls:
- `preferences/user_preferences.json`
- `.agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py` (US)
- `.agents/skills/run-llm-deep-dive/scripts/fetch_sec_filing_markdown.py` (US, targeted SEC filings)
- `references/sec-access-policy.md` (required SEC-access guardrails)

## Step 1: Confirm Scope and Dates
- Confirm ticker, exchange country, revised as-of date, and baseline report directory explicitly.
- Confirm baseline files exist and are readable.
- Resolve a new output report directory (`<REPORT_DATE_DIR>`) using:
  - first run on revised as-of date: `YYYY-MM-DD`
  - additional runs for same revised as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.
- Do not revise output files in-place inside an existing report directory.
- Ensure all evidence used (local and external) is dated on or before the revised as-of date.

## Step 2: Extract Baseline Failure Points
- Parse the baseline thesis and identify assumptions that, if wrong, can destroy intrinsic value.
- Include at least:
  - demand durability / pricing power
  - margin durability / cost structure
  - capital allocation quality
  - balance-sheet or funding fragility
  - regulatory or legal exposure
- Score each assumption using:
  - downside impact (1-5)
  - probability baseline is wrong (1-5)
  - current evidence gap (1-5)
- Prioritize top 3-6 assumptions by combined severity.

## Step 3: Design an Original Research Plan
- Write `deep-dive-plan.md` using this run's own hypotheses (do not copy prior plans verbatim).
- For each prioritized assumption define:
  - falsification question
  - evidence needed to confirm or break it
  - target sources (local + external)
  - pass/fail threshold that would force a valuation change
- Use `assets/research-plan-template.md` as a skeleton only.

## Step 4: Execute Local Evidence Pass
- Pull decision-critical evidence from local filings/statements/transcripts first.
- Focus on signals that can break the thesis:
  - weakening segment economics
  - customer concentration changes
  - covenant stress, refinancing wall, liquidity dependence
  - persistent guidance misses
  - dilution or misaligned buybacks
- Record file paths for every factual claim you may use later.

## Step 5: Execute Targeted External Research
- Use `references/source-quality-and-search.md`.
- Run targeted searches for each falsification question; avoid broad narrative searching.
- Prefer primary, high-quality sources (regulatory, company counterparties, industry bodies, top-tier data providers).
- For any material external claim, collect at least two independent sources when feasible.
- Log every accepted source in `third-party-sources.md` with publication date and access date.
- For SEC sources, follow `references/sec-access-policy.md` and use skill SEC scripts only.

## Step 6: Pull Older SEC Filings if Needed (US)
- Use this when multi-year risks cannot be resolved from current local files.
- Follow `references/historical-sec-fetch.md`.
- Typical uses:
  - past cycle margin stress behavior
  - litigation, accounting, or governance pattern checks
  - prior disclosure language versus current messaging

## Step 7: Revise Valuation
- Start from baseline `valuation/inputs.yaml`.
- Change only assumptions with explicit supporting evidence.
- Document each changed assumption (old value, new value, reason, sources).
- Recompute outputs in `valuation/outputs.json` using:
  - `.agents/skills/run-llm-workflow/references/valuation-method.md`
- Keep model choice aligned with business economics (DCF vs residual income).

## Step 8: Draft Revised Deliverables
- Draft revised `report.md` via `references/report-format.md`.
- Draft `deep-dive-changes.md` with:
  - verdict delta (baseline vs revised)
  - assumption delta table with evidence
  - valuation output delta table (base/bull/bear)
  - what did not change and why
- If nothing changed materially, say so explicitly and justify with evidence.

## Step 9: Quality Gate
All checks must pass before completion.

Scope and data:
- [ ] Ticker, revised as-of date, baseline report directory, and output report directory are explicit.
- [ ] Required baseline and output files exist and are readable.
- [ ] Evidence used is dated on or before revised as-of date.
- [ ] Workflow was executed as LLM reasoning, not delegated to one deterministic analyzer.

Falsification rigor:
- [ ] Top downside hypotheses are explicitly prioritized.
- [ ] Research plan defines pass/fail thresholds for each top hypothesis.
- [ ] At least one serious disconfirming test was performed for each top hypothesis.

Evidence quality:
- [ ] Every factual claim cites local file paths.
- [ ] External claims are logged in `third-party-sources.md` with source quality notes.
- [ ] Source quality hierarchy was followed; low-credibility sources were excluded.
- [ ] SEC retrievals followed `references/sec-access-policy.md` (no ad-hoc direct `sec.gov` HTTP calls).

Valuation integrity:
- [ ] Every revised assumption has evidence-backed rationale.
- [ ] `valuation/inputs.yaml` and `valuation/outputs.json` are internally consistent.
- [ ] Margin-of-safety conclusion matches revised valuation outputs and current price.

Output quality:
- [ ] `report.md` is concise and decision-oriented.
- [ ] `deep-dive-plan.md` is original to this run.
- [ ] `deep-dive-changes.md` clearly explains what changed (or why not).

## Step 10: Improvement Loop
- If this run exposes a repeatable process failure, append a row to `docs/improvement-log.md`.
- When repeat issues are detected, patch this skill reference set rather than only patching a single report.
