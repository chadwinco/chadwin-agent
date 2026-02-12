# SEC Access Policy (Required for SEC Retrieval)

Use these rules whenever this workflow pulls SEC evidence.

## Rules
- Do not call `sec.gov` directly with ad-hoc `curl`, `wget`, `requests`, `urllib`, or browser-scrape commands.
- Use skill-provided SEC helpers only:
  - `.agents/skills/run-llm-workflow/scripts/fetch_historical_filings.py`
  - `.agents/skills/run-llm-workflow/scripts/fetch_sec_filing_markdown.py`
- Default SEC identity source must be `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) from `.env`.
- Identity overrides are exceptional and must be explicit and auditable using `--allow-identity-override`.

## Why
- Keeps SEC retrieval behavior consistent via `edgartools`.
- Prevents accidental placeholder or mismatched identities.
- Produces local markdown artifacts that can be cited in reports.

## Minimal Usage
Historical filings:

```bash
python3 .agents/skills/run-llm-workflow/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K,10-Q,8-K \
  --limit 6 \
  --before <YYYY-MM-DD>
```

Single targeted filing:

```bash
python3 .agents/skills/run-llm-workflow/scripts/fetch_sec_filing_markdown.py \
  --ticker <TICKER> \
  --form 8-K \
  --filed-date <YYYY-MM-DD> \
  --output-path companies/US/<PRIMARY_TICKER>/data/filings/third_party/<NAME>.md
```
