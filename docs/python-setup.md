# Python Setup (venv)

Use a local virtual environment stored at `.venv/` in the repo root.

## Create and Activate
```
python3 -m venv /Users/chad/source/chadwin-codex/.venv
source /Users/chad/source/chadwin-codex/.venv/bin/activate
```

## Install Dependencies
```
python -m pip install -r /Users/chad/source/chadwin-codex/requirements.txt
```

## SEC Identity (Required for EDGAR Fetching)
Create a `.env` file in the repo root with your EDGAR identity (name + email):
```
EDGAR_IDENTITY="Your Name your.email@example.com"
```

If you already use `SEC_IDENTITY_EMAIL`, it will be accepted as a fallback.

## Run Workflow
```
python /Users/chad/source/chadwin-codex/.agents/skills/fetch-company-data/scripts/add_company.py --ticker PEP --asof 2026-02-06
```

Research generation is LLM-first via `$run-company-research`.
