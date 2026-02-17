---
name: run-llm-workflow
description: Produce a concise, LLM-written investment report and scenario valuation from `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data` using a progressive, issue-driven workflow that starts with early key-lever mapping and continues until confidence is high and incremental research has diminishing returns. Use after running the market-appropriate fetch skill (for example, `$fetch-us-company-data`) when creating or refreshing `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md` and valuation files.
---

# Run LLM Workflow

## Overview
This is the canonical LLM-first research workflow.

The target output is intentionally simple and auditable:
1. A decision-oriented investment report.
2. A transparent base/bull/bear valuation.

The report style is narrative-first by default:
- explain the few valuation pillars that matter most,
- show how evidence changed (or did not change) assumptions,
- avoid checklist-style fact dumps.

The research process is progressive, not fixed-stage by default:
- identify the highest-impact unresolved investment questions,
- investigate them to required depth,
- stop when key decision points are resolved to expert-level confidence.

## Execution Mode (Required)
- Execute this skill by reasoning through the workflow and writing outputs.
- Do not look for or invent a single `scripts/*.py` command that completes the report.
- Helper commands are fine for extraction or arithmetic, but they do not replace the LLM workflow.
- The task is complete only when all required output files are written and the goal gate in `references/research-workflow.md` passes.

## Report Directory Convention
Use `<REPORT_DATE_DIR>` for outputs:
- First run for an as-of date: `YYYY-MM-DD`
- Additional runs for that same as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.
- Exception: if `reports/YYYY-MM-DD/valuation/inputs.yaml` already exists and the package is incomplete (missing `report.md` or `valuation/outputs.json`), continue writing into `YYYY-MM-DD` instead of creating a suffixed directory.

## Quick Start
1. Resolve ticker and as-of date explicitly.
2. Ensure `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data` is populated. If not, run the appropriate market fetch skill first (for example, `$fetch-us-company-data`).
3. If you plan to use optional SEC helper scripts in this skill, install helper dependencies listed in `agents/openai.yaml`.

4. Load `.chadwin-data/user_preferences.json` when present and apply:
   - strategy preferences to framing and valuation emphasis
   - report preferences to section emphasis/content inclusion
5. Resolve the output directory from repo root:

```bash
REPORTS_ROOT=".chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports"
ASOF_DATE="<YYYY-MM-DD>"
PRIMARY_DIR="$REPORTS_ROOT/$ASOF_DATE"
REPORT_DATE_DIR="$ASOF_DATE"
if [ -d "$PRIMARY_DIR" ]; then
  # Resume fetch-bootstrap package if valuation inputs exist but outputs are incomplete.
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

6. Work through `references/research-workflow.md` as an LLM task.
7. After report completion and goal-gate pass, remove the researched ticker from `.chadwin-data/idea-screens/company-ideas-log.jsonl`.

## Queue Helpers
Use the queue CLI owned by the `$chadwin-research` skill from repo root:

```bash
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py pick --task run-llm-workflow
python3 .agents/skills/chadwin-research/scripts/company_idea_queue.py remove --ticker <TICKER>
```

- If ticker is omitted, `pick` is the default selection source.
- Run `remove` only after required outputs are finalized and the goal gate passes.

## Required Outputs
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/inputs.yaml`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/outputs.json`

## Inputs to Prioritize
Core local evidence:
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/*.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`

Market-expectation anchors (when available):
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_revenue_estimates.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_estimates.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_eps_forward_pe_estimates.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_price_targets.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_consensus.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_ratings_actions_12m.csv`

## Workflow
1. Execute the progressive workflow in `references/research-workflow.md`.
2. Build valuation assumptions and outputs using `references/valuation-method.md`, explicitly reconciling your assumptions with analyst-implied market expectations.
3. Draft the report using `references/report-format.md`, honoring report-content preferences.
4. Use `references/source-quality-and-search.md` for targeted external checks when local files cannot resolve high-impact lever questions.
5. For US SEC historical pulls, follow `references/sec-access-policy.md` and `references/historical-sec-fetch.md`.
6. Run mandatory post-run introspection using `references/improvement-loop.md`, apply same-run workflow/reference updates when introspection finds repeatable or workflow-caused issues, and log to `improvement-log.md` only when a real improvement is implemented (no no-change entries).

## Constraints
- Keep the report concise and decision-oriented.
- Default to tight prose over fragmented bullets/tables when either form can work.
- Make the valuation argument legible: each core pillar should connect evidence to specific model inputs.
- Paraphrase source text; no verbatim copying from filings or transcripts.
- Every factual claim needs a local file citation.
- External claims must be cross-checked and traceable.
- Do not violate explicit user exclusions in `.chadwin-data/user_preferences.json` unless the user explicitly asks to override.

## Troubleshooting
- If you are looking for a one-command analyzer (for example, `scripts/analyze_company.py`), stop and return to the LLM workflow in `references/research-workflow.md`.
- If no ticker was supplied and queue selection fails, run the queue helper (`pick --task run-llm-workflow`) and confirm the log has candidates.
- If required data is missing, run the appropriate market fetch skill for that ticker/date (for example, `$fetch-us-company-data`).
- If valuation looks inconsistent, re-check units and net-debt sign in `references/valuation-method.md`.
- If the write-up is weak, rerun the goal gate in `references/research-workflow.md` and close every unresolved high-impact lever before finalizing.

## Related References
- `references/research-workflow.md`
- `references/report-format.md`
- `references/valuation-method.md`
- `references/source-quality-and-search.md`
- `references/sec-access-policy.md`
- `references/historical-sec-fetch.md`
- `references/improvement-loop.md`
