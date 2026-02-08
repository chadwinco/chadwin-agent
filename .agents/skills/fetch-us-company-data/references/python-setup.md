# Python Setup (Fetch US Company Data)

Use a local virtual environment in the repository root (`.venv/`).

## Create and activate
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies
```bash
python3 -m pip install -r requirements.txt
```

## Required EDGAR identity
Create `.env` in the repo root with one of these variables:

```bash
EDGAR_IDENTITY="Your Name your.email@example.com"
# or
SEC_IDENTITY_EMAIL="your.email@example.com"
```

You can also pass `--identity "Your Name your.email@example.com"` to the CLI.
