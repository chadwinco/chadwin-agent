# Tests and Scenarios

These are manual validation steps for the research workflow.

1. End-to-end run for PEP
   - `python3 -m venv /Users/chad/source/chadwin-codex/.venv`
   - `source /Users/chad/source/chadwin-codex/.venv/bin/activate`
   - `python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt`
   - `python /Users/chad/source/chadwin-codex/scripts/run_company.py --ticker PEP --asof 2026-02-06`

2. Create a new company from EDGAR
   - Add `EDGAR_IDENTITY` to `/Users/chad/source/chadwin-codex/.env`
   - `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker AAPL --asof 2026-02-06`
   - Confirm the report file is created.
   - Confirm `companies/<TICKER>/data/filings/earnings-call-*.md` exists.

2. Missing data scenario
   - Temporarily rename one CSV and re-run to confirm clear error output.

3. Statement alignment
   - Verify fiscal years align across income, balance sheet, and cash flow.

4. Valuation sanity
   - Adjust discount rates and confirm valuation shifts as expected.

5. Template rendering
   - Confirm all placeholders are populated in output markdown.
