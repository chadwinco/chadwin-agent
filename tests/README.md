# Tests and Scenarios

These are manual validation steps for the research workflow.

1. End-to-end run for PEP
   - `python3 -m venv /Users/chad/source/chadwin-codex/.venv`
   - `source /Users/chad/source/chadwin-codex/.venv/bin/activate`
   - `python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt`
   - `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker PEP --asof <YYYY-MM-DD>`
   - Run `$run-company-research` for `PEP` as of `<YYYY-MM-DD>`.
   - Confirm these artifacts exist:
     - `companies/PEP/reports/<YYYY-MM-DD>/report.md`
     - `companies/PEP/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
     - `companies/PEP/reports/<YYYY-MM-DD>/valuation/outputs.json`

2. Create a new company from EDGAR
   - Add `EDGAR_IDENTITY` to `/Users/chad/source/chadwin-codex/.env`
   - `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker AAPL --asof <YYYY-MM-DD>`
   - Confirm data files are created in `companies/AAPL/data/`.
   - Confirm `companies/AAPL/data/filings/earnings-call-*.md` exists.

3. Missing data scenario
   - Temporarily rename one required CSV in `companies/<TICKER>/data/financial_statements/annual/`.
   - Run `$run-company-research` for that ticker/date.
   - Confirm the workflow blocks and indicates the missing local data before report generation.

4. Statement alignment
   - Verify fiscal years align across income, balance sheet, and cash flow.

5. Valuation sanity
   - Adjust discount rates in `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
   - Re-run `$run-company-research` for the same ticker/date.
   - Confirm value-per-share shifts in `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`.

6. Checklist gate
   - Run through Step 6 in `.agents/skills/run-company-research/references/research-workflow.md` and confirm all items pass before finalizing.
