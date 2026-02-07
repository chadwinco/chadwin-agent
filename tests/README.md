# Tests and Scenarios

These are manual validation steps for the research workflow.

1. End-to-end run for PEP
   - `python3 -m venv /Users/chad/source/chadwin-codex/.venv`
   - `source /Users/chad/source/chadwin-codex/.venv/bin/activate`
   - `python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt`
   - `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker PEP --asof 2026-02-06 --skip-analysis`
   - Run `$run-company-research` for `PEP` as of `2026-02-06`.
   - Confirm these artifacts exist:
     - `companies/PEP/reports/2026-02-06/report.md`
     - `companies/PEP/reports/2026-02-06/valuation/inputs.yaml`
     - `companies/PEP/reports/2026-02-06/valuation/outputs.json`

2. Create a new company from EDGAR
   - Add `EDGAR_IDENTITY` to `/Users/chad/source/chadwin-codex/.env`
   - `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker AAPL --asof 2026-02-06 --skip-analysis`
   - Confirm data files are created in `companies/AAPL/data/`.
   - Confirm `companies/<TICKER>/data/filings/earnings-call-*.md` exists.

3. Missing data scenario
   - Temporarily rename one CSV and re-run to confirm clear error output.

4. Statement alignment
   - Verify fiscal years align across income, balance sheet, and cash flow.

5. Valuation sanity
   - Adjust discount rates in `valuation/inputs.yaml` and confirm value-per-share shifts as expected.

6. Checklist gate
   - Run through `docs/research-checklist.md` and confirm all items pass before finalizing.
