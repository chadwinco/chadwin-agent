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

## Run Workflow
```
python /Users/chad/source/chadwin-codex/scripts/run_company.py --ticker BBCP --asof 2026-02-06
```
