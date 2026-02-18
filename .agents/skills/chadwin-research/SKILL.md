---
name: chadwin-research
description: Produce a concise, LLM-written investment report and scenario valuation using a progressive, issue-driven workflow that fetches evidence on demand as uncertainties are discovered. Use for creating or refreshing `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md` and valuation files.
---

# Run LLM Workflow

## Overview
This is the canonical LLM-first research workflow.

Target output:
1. A decision-oriented investment report.
2. A transparent base/bull/bear valuation.

Core operating model:
- research is progressive and issue-driven,
- data fetch is on-demand inside the research loop,
- stop when thesis-critical uncertainty is resolved and additional work has diminishing returns.

Do not require a fully populated data package before starting.

## Execution Mode (Required)
- Execute this skill by reasoning through the workflow and writing outputs.
- Do not look for or invent a single `scripts/*.py` command that completes the report.
- Helper commands are fine for extraction or arithmetic, but they do not replace the LLM workflow.
- The task is complete only when all required output files are written and the goal gate in `references/research-workflow.md` passes.

## Data Acquisition Model (Required)
- Treat data acquisition as part of research, not a separate prerequisite stage.
- For US SEC evidence, use `$fetch-us-company-data` as the default fetch operator.
- For missing ticker selection or fresh idea generation, use `$fetch-us-investment-ideas`.
- Preferred inter-skill communication is natural language objective statements.
- Use deterministic wrapper requests only when reproducibility or replay is needed.

Natural-language fetch example:
- "For MSFT as of 2026-02-18, fetch the latest 10-K, all later 10-Q filings, relevant 8-K filings with attachments, and Form 4 transactions for the last 6 months. Save artifacts under the company data path."

## Report Directory Convention
Use `<REPORT_DATE_DIR>` for outputs:
- First run for an as-of date: `YYYY-MM-DD`
- Additional runs for that same as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.
- Exception: if `reports/YYYY-MM-DD/valuation/inputs.yaml` already exists and the package is incomplete (missing `report.md` or `valuation/outputs.json`), continue writing into `YYYY-MM-DD` instead of creating a suffixed directory.

## Quick Start
1. Resolve ticker and as-of date explicitly.
If ticker is omitted, pick from queue:

```bash
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py pick --task chadwin-research
```

If queue has no suitable ticker or user asks for fresh ideas, run `$fetch-us-investment-ideas`, append ideas to queue, then pick again.
2. Load `<DATA_ROOT>/user_preferences.json` when present and apply:
   - strategy preferences to framing and valuation emphasis
   - report preferences to section emphasis/content inclusion
3. Resolve the output directory from repo root:

```bash
REPORTS_ROOT="<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports"
ASOF_DATE="<YYYY-MM-DD>"
PRIMARY_DIR="$REPORTS_ROOT/$ASOF_DATE"
REPORT_DATE_DIR="$ASOF_DATE"
if [ -d "$PRIMARY_DIR" ]; then
  # Resume incomplete package when valuation inputs exist but outputs are incomplete.
  if [ -f "$PRIMARY_DIR/valuation/inputs.yaml" ] && [ ! -f "$PRIMARY_DIR/report.md" ]; then
    REPORT_DATE_DIR="$ASOF_DATE"
  elif [ -f "$PRIMARY_DIR/valuation/inputs.yaml" ] && [ ! -f "$PRIMARY_DIR/valuation/outputs.json" ]; then
    REPORT_DATE_DIR="$ASOF_DATE"
  else
    IDX=1
    while [ -e "$REPORTS_ROOT/${ASOF_DATE}-$(printf '%02d' "$IDX")" ]; do
      IDX=$((IDX + 1))
    done
    REPORT_DATE_DIR="${ASOF_DATE}-$(printf '%02d' "$IDX")"
  fi
fi
REPORT_DIR="$REPORTS_ROOT/$REPORT_DATE_DIR"
mkdir -p "$REPORT_DIR/valuation"
echo "Using REPORT_DATE_DIR=$REPORT_DATE_DIR"
```

4. Execute `references/research-workflow.md`.
5. Fetch additional evidence on demand whenever a thesis-critical uncertainty is blocked by missing data.
6. After goal-gate pass, remove the researched ticker from `<DATA_ROOT>/idea-screens/company-ideas-log.jsonl`.

## Queue Helpers
Use the queue CLI in this skill from repo root:

```bash
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py pick --task chadwin-research
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py remove --ticker <TICKER>
```

- If ticker is omitted, `pick` is the default selection source.
- Run `remove` only after required outputs are finalized and the goal gate passes.

## Required Outputs
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/inputs.yaml`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/outputs.json`

## Inputs to Prioritize
Existing local evidence (if present):
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/*.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`

Market-expectation anchors (fetch on demand when needed):
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_revenue_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_forward_pe_estimates.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_price_targets.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_consensus.csv`
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_ratings_actions_12m.csv`

## Workflow
1. Execute the progressive loop in `references/research-workflow.md`.
2. Build valuation assumptions and outputs using `references/valuation-method.md`, reconciling assumptions with available market expectations.
3. Draft the report using `references/report-format.md`, honoring report-content preferences.
4. Use `references/source-quality-and-search.md` for targeted external checks when local and fetched filing evidence cannot resolve high-impact questions.
5. For US SEC deep/history pulls, follow `references/sec-access-policy.md` and `references/historical-sec-fetch.md`.
6. Run mandatory post-run introspection using `references/improvement-loop.md`, apply same-run workflow/reference updates when introspection finds repeatable or workflow-caused issues, and log to `improvement-log.md` only when a real improvement is implemented.

## Constraints
- Keep the report concise and decision-oriented.
- Default to tight prose over fragmented bullets/tables when either form can work.
- Make the valuation argument legible: each core pillar should connect evidence to specific model inputs.
- Paraphrase source text; no verbatim copying from filings or transcripts.
- Every factual claim needs local file-path citations.
- External claims must be cross-checked and traceable.
- Do not violate explicit user exclusions in `<DATA_ROOT>/user_preferences.json` unless the user explicitly asks to override.

## Troubleshooting
- If you are looking for a one-command analyzer (for example, `scripts/analyze_company.py`), stop and return to the LLM workflow.
- If no ticker was supplied and queue selection fails, run `$fetch-us-investment-ideas`, append to queue, then rerun the queue helper (`pick --task chadwin-research`).
- If a lever is blocked by missing evidence, run a focused fetch via `$fetch-us-company-data` and continue the same research loop.
- If valuation looks inconsistent, re-check units and net-debt sign in `references/valuation-method.md`.
- If write-up quality is weak, rerun the goal gate in `references/research-workflow.md` and close every unresolved high-impact lever before finalizing.

## Related References
- `references/research-workflow.md`
- `references/report-format.md`
- `references/valuation-method.md`
- `references/source-quality-and-search.md`
- `references/sec-access-policy.md`
- `references/historical-sec-fetch.md`
- `references/improvement-loop.md`
