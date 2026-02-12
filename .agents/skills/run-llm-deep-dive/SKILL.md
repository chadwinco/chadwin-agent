---
name: run-llm-deep-dive
description: Run a falsification-first deep diligence workflow for companies that looked attractive after `run-llm-workflow`: design an original downside-focused research plan, execute local plus targeted third-party research (with optional older SEC pulls), then publish revised report and valuation outputs with explicit deltas.
---

# Run LLM Deep Dive

## Overview
Use this skill after an initial report suggests a company may be investable, and you need higher-conviction downside analysis before acting.

This workflow is intentionally adversarial to the baseline thesis: prioritize evidence that could flip the conclusion from positive to negative.

## Execution Mode (Required)
- Execute this skill as an LLM-first workflow.
- Do not replace this process with a one-command deterministic analyzer.
- Scripts are helper tools only (fetching, extraction, arithmetic).

## When to Use
- The initial report verdict is `Attractive` or `Watch`.
- Position sizing depends on resolving tail risks.
- You suspect unpriced risks (competition, regulation, accounting quality, capital allocation, balance sheet).

## Inputs
Required:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/report.md`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/valuation/inputs.yaml`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_REPORT_DIR>/valuation/outputs.json`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/...`

Optional:
- `preferences/user_preferences.json`
- Extra US historical filings from `scripts/fetch_historical_filings.py`

## Report Directory Convention
Use `<REPORT_DATE_DIR>` for deep-dive outputs:
- First run for revised as-of date: `YYYY-MM-DD`
- Additional runs for that same revised as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.

Never rewrite an existing report package during deep-dive runs.

## Quick Start
1. Confirm ticker, exchange country, baseline report directory, and revised as-of date.
2. Resolve a new output directory:

```bash
REPORTS_ROOT="companies/<EXCHANGE_COUNTRY>/<TICKER>/reports"
ASOF_DATE="<YYYY-MM-DD>"
REPORT_DATE_DIR="$ASOF_DATE"
if [ -e "$REPORTS_ROOT/$REPORT_DATE_DIR" ]; then
  IDX=1
  while [ -e "$REPORTS_ROOT/${ASOF_DATE}-$(printf '%02d' "$IDX")" ]; do
    IDX=$((IDX + 1))
  done
  REPORT_DATE_DIR="${ASOF_DATE}-$(printf '%02d' "$IDX")"
fi
REPORT_DIR="$REPORTS_ROOT/$REPORT_DATE_DIR"
mkdir -p "$REPORT_DIR/valuation"
echo "Using REPORT_DATE_DIR=$REPORT_DATE_DIR"
```

3. Execute `references/deep-research-workflow.md`.
4. Draft the revised report using `references/report-format.md`.
5. Apply `references/source-quality-and-search.md` for third-party research quality controls.
6. Follow `references/sec-access-policy.md` for all SEC retrievals (required).
7. Pull older SEC filings when needed via `references/historical-sec-fetch.md`.
8. Finalize required outputs and pass the quality gate.

## Required Outputs
Under `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`
- `deep-dive-plan.md`
- `deep-dive-changes.md`
- `third-party-sources.md`

## Workflow
1. Start from baseline report and valuation assumptions.
2. Build and rank thesis-breaker hypotheses by downside impact.
3. Design an original research plan (`deep-dive-plan.md`) focused on top hypothesis risk.
4. Execute mixed evidence collection:
   - local filings/statements/transcripts
   - targeted high-quality third-party sources
   - optional older SEC filing pull (US)
5. Update valuation assumptions only when evidence supports a change.
6. Recompute valuation outputs.
7. Produce revised report and explicit delta file (`deep-dive-changes.md`).

## Constraints
- Every factual claim in final outputs must cite local file paths.
- External claims must be logged in `third-party-sources.md` with URL and access date.
- Use evidence dated on or before the revised as-of date.
- Prioritize disconfirming evidence over confirming evidence.
- Paraphrase sources; avoid verbatim copying.
- SEC retrievals must use skill SEC scripts and configured `EDGAR_IDENTITY`; do not use ad-hoc direct `sec.gov` HTTP calls.

## Related References
- `references/deep-research-workflow.md`
- `references/report-format.md`
- `references/source-quality-and-search.md`
- `references/sec-access-policy.md`
- `references/historical-sec-fetch.md`
- `.agents/skills/run-llm-workflow/references/valuation-method.md`
