# Tests and Scenarios

These are manual validation steps for the research workflow.

1. End-to-end run for BBCP
   - `python3 -m venv /Users/chad/source/chadwin-codex/.venv`
   - `source /Users/chad/source/chadwin-codex/.venv/bin/activate`
   - `python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt`
   - `python /Users/chad/source/chadwin-codex/scripts/run_company.py --ticker BBCP --asof 2026-02-06`
   - Confirm report and appendix files are created.

2. Missing data scenario
   - Temporarily rename one CSV and re-run to confirm clear error output.

3. Statement alignment
   - Verify fiscal years align across income, balance sheet, and cash flow.

4. Valuation sanity
   - Adjust discount rates and confirm valuation shifts as expected.

5. Template rendering
   - Confirm all placeholders are populated in output markdown.
