# Research Workflow

## Objective
Build repeatable, LLM-driven company research that outputs:
- A concise investment summary.
- A transparent base/bull/bear valuation.

Canonical workflow details are maintained in:
- `.agents/skills/run-company-research/SKILL.md`
- `.agents/skills/run-company-research/references/research-workflow.md`
- `.agents/skills/run-company-research/references/research-checklist.md`

## Inputs
- `companies/<TICKER>/data/*` (filings, statements, transcript, profile, optional analyst estimates)
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

## Process
1. If data is missing, run `$fetch-company-data`.
2. Run `$run-company-research` to produce:
   - `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`
   - `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
   - `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`
3. Apply the checklist in `.agents/skills/run-company-research/references/research-checklist.md`.
4. Log external sources in `docs/source-log.md`.
5. Log process improvements in `docs/improvement-log.md`.

## Guardrails
- Do not run `scripts/run_company.py` for the research workflow.
- Keep report output concise and decision-oriented.
- Cite local file paths for factual claims.
