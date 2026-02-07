---
name: run-company-research
description: Produce a concise, LLM-written investment summary and scenario valuation from `companies/TICKER/data`. Use after `$fetch-company-data` when creating or refreshing `companies/TICKER/reports/<DATE>/report.md` and valuation files.
---

# Run Company Research

## Overview
This is an LLM-first research workflow. The target output is intentionally simple:
1. A short investment summary for a company.
2. A transparent base/bull/bear valuation.

Do not use `scripts/run_company.py` for this skill.

## Quick Start
1. Confirm ticker and as-of date with the user.
2. Ensure `companies/<TICKER>/data` is populated. If not, run `$fetch-company-data` first.
3. Create the output directory from the repo root:

```bash
mkdir -p companies/<TICKER>/reports/<YYYY-MM-DD>/valuation
```
4. Follow `references/research-workflow.md`.

## Required Outputs
- `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

## Workflow
1. Run the end-to-end process in `references/research-workflow.md`.
2. Build valuation assumptions and outputs using `references/valuation-method.md`.
3. Draft the report using `references/report-format.md`.
4. Check all gates in `references/research-checklist.md` before finalizing.
5. Record learnings using `references/improvement-loop.md`.

## Constraints
- Keep the report concise and decision-oriented.
- Paraphrase source text; no verbatim copying from filings or transcripts.
- Every factual claim needs a local file citation.
- Log external sources in `docs/source-log.md`.

## Troubleshooting
- If required data is missing, run `$fetch-company-data` for that ticker/date.
- If valuation looks inconsistent, re-check units and net debt sign in `references/valuation-method.md`.
- If the write-up is weak, rerun the checklist and fix every unchecked item.

## Related References
- `references/research-workflow.md`
- `references/report-format.md`
- `references/valuation-method.md`
- `references/research-checklist.md`
- `references/improvement-loop.md`
- `references/source-log-format.md`
