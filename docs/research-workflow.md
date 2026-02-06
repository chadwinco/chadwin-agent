# Research Workflow

## Objective
Build repeatable company research that outputs:
- A fair-value estimate grounded in long-term economics.
- A concise write-up explaining competitive position and margin of safety.

Prerequisite: set up the Python virtual environment described in `docs/python-setup.md`.

## End-to-End Flow
0. Activate the Python virtual environment in `.venv/` and set `EDGAR_IDENTITY` in `.env` if fetching filings.
1. Ingest data from `companies/<TICKER>/data` (canonical statements live in `data/financials/annual` and `data/financials/quarterly` and feed the analysis outputs).
2. Run quality checks for missing files, inconsistent dates, and obvious data errors.
3. Compute core metrics (growth, margins, ROIC, leverage, FCF).
4. Build a base/bull/bear FCF DCF model.
5. Draft the report using templates and prompts.
6. Log sources and update the improvement log.

## New Company Bootstrap
Use `scripts/add_company.py` to create directories, fetch EDGAR filings and financials, pull the latest earnings call transcript, and run the analysis.

## Improvement Loop
- After each report, note gaps or errors in `docs/improvement-log.md`.
- Update prompts, metrics, or templates based on the gaps.
- Re-run the report for the same company to validate improvements.

## Output Locations
- Report: `companies/<TICKER>/analysis/<YYYY-MM-DD>-report.md`
- Model inputs: `companies/<TICKER>/model/assumptions.yaml`
- Model outputs: `companies/<TICKER>/model/outputs.json`
- Transcript: `companies/<TICKER>/data/earnings-call-<YYYY-MM-DD>-<source>.md`
