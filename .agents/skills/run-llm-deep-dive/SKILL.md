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
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_DATE>/report.md`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_DATE>/valuation/inputs.yaml`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<BASELINE_DATE>/valuation/outputs.json`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/...`

Optional:
- `preferences/user_preferences.json`
- Extra US historical filings from `scripts/fetch_historical_filings.py`

## Quick Start
1. Confirm ticker, exchange country, baseline date, and revised as-of date.
2. Create output directory:

```bash
mkdir -p companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation
```

3. If `<YYYY-MM-DD>` already contains a prior report package, snapshot it before rewriting:

```bash
cp companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/report.md \
  companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/report.initial.md
cp companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml \
  companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.initial.yaml
cp companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json \
  companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.initial.json
```

4. Execute `references/deep-research-workflow.md`.
5. Draft the revised report using `references/report-format.md`.
6. Apply `references/source-quality-and-search.md` for third-party research quality controls.
7. Follow `references/sec-access-policy.md` for all SEC retrievals (required).
8. Pull older SEC filings when needed via `references/historical-sec-fetch.md`.
9. Finalize required outputs and pass the quality gate.

## Required Outputs
Under `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/`:
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
