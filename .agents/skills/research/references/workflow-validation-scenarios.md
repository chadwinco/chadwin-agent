# Research Workflow Validation Scenarios

Manual validation checks for the end-to-end `$research` workflow and its delegated skills.

Use explicit as-of dates (for example, `2026-02-11`) and run commands from repo root unless noted.

## 1. End-to-end run for PEP
- `python3 -m venv /Users/chad/source/chadwin-codex/.venv`
- `source /Users/chad/source/chadwin-codex/.venv/bin/activate`
- `python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt`
- `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-us-company-data/scripts/add_company.py --ticker PEP --asof <YYYY-MM-DD>`
- Run `$run-llm-workflow` for `PEP` as of `<YYYY-MM-DD>`.
- Confirm these artifacts exist:
  - `companies/US/PEP/reports/<YYYY-MM-DD>/report.md`
  - `companies/US/PEP/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
  - `companies/US/PEP/reports/<YYYY-MM-DD>/valuation/outputs.json`

## 2. Create a new company from EDGAR
- Add `EDGAR_IDENTITY` to `/Users/chad/source/chadwin-codex/.env`
- `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-us-company-data/scripts/add_company.py --ticker AAPL --asof <YYYY-MM-DD>`
- Confirm data files are created in `companies/US/AAPL/data/`.
- Confirm `companies/US/AAPL/data/filings/earnings-call-*.md` exists.

## 3. Create a Japanese company package
- `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-japanese-company-data/scripts/add_company.py --ticker 79740 --asof <YYYY-MM-DD>`
- Confirm data files are created in `companies/Japan/79740/data/`.
- Confirm `companies/Japan/79740/reports/<YYYY-MM-DD>/valuation/inputs.yaml` exists.

## 4. Missing data scenario
- Temporarily rename one required CSV in `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/`.
- Run `$run-llm-workflow` for that ticker/date.
- Confirm the workflow blocks and indicates the missing local data before report generation.

## 5. Statement alignment
- Verify fiscal years align across income, balance sheet, and cash flow.

## 6. Valuation sanity
- Adjust discount rates in `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`.
- Re-run `$run-llm-workflow` for the same ticker/date.
- Confirm value-per-share shifts in `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`.

## 7. Checklist gate
- Run through Step 6 in `.agents/skills/run-llm-workflow/references/research-workflow.md` and confirm all items pass before finalizing.

## 8. Queue fallback behavior
- `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-us-investment-ideas/scripts/fetch_us_investment_ideas.py --limit 5 --output /Users/chad/source/chadwin-codex/idea-screens/<YYYY-MM-DD>/ideas.json`
- Confirm `idea-screens/company-ideas-log.jsonl` exists and includes appended entries.
- Run `python /Users/chad/source/chadwin-codex/.agents/skills/fetch-us-company-data/scripts/add_company.py --asof <YYYY-MM-DD>` with no `--ticker`.
- Confirm it selects the next US ticker from the queue.
- After completing `$run-llm-workflow`, run `python /Users/chad/source/chadwin-codex/.agents/skills/research/scripts/company_idea_queue.py remove --ticker <TICKER>` and confirm the ticker is removed from `idea-screens/company-ideas-log.jsonl`.
