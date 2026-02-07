# Research Workflow

## Objective
Build repeatable, LLM-driven company research that outputs:
- A fair-value estimate grounded in long-term economics.
- A concise report explaining competitive position and margin of safety.

Prerequisite: set up the Python virtual environment described in `docs/python-setup.md`.

## Inputs (LLM Must Use)
- `companies/<TICKER>/data/*` (filings, transcripts, analyst estimates, profiles).
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml` and `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`.
- `prompts/*.md` for section-by-section guidance.
- `docs/data-dictionary.md` for metric definitions.
- `docs/research-checklist.md` as the quality gate.

## Deterministic Pipeline (Run First)
1. If data is missing, run `scripts/add_company.py` to fetch filings, financials, transcripts, and analyst estimates.
2. Run `scripts/run_company.py` to refresh metrics, valuation outputs, and the report scaffold.

## LLM Report Workflow
1. Read all prompt files in `prompts/` before drafting.
2. Use agentic search (`rg`/`grep`) directly against `companies/<TICKER>/data` for each section; do not rely on pre-sliced context.
3. Draft the report in `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`, following the report template structure.
4. Apply the checklist in `docs/research-checklist.md` and fix any gaps before finalizing.
5. Log any external sources in `docs/source-log.md` and record process improvements in `docs/improvement-log.md`.

## Quality Gates
- No verbatim copying from filings; paraphrase and synthesize.
- Cite file paths inline for all factual claims from local data.
- Ensure valuation narrative aligns with `valuation/inputs.yaml` and `valuation/outputs.json` for the selected report date.

## Output Locations
- Report: `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`
- Valuation inputs: `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- Valuation outputs: `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`
- Transcript: `companies/<TICKER>/data/filings/earnings-call-<YYYY-MM-DD>-<source>.md`
