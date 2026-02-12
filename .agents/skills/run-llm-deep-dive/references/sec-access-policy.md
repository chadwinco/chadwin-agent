# SEC Access Policy (Required for Deep Dive)

This skill has strict SEC-fetch rules to keep identity handling and evidence provenance auditable.

## Rules
- Do not call `sec.gov` directly with ad-hoc `curl`, `wget`, `requests`, `urllib`, or browser-scrape commands during deep dives.
- Use skill-provided SEC helpers only:
  - `.agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py`
  - `.agents/skills/run-llm-deep-dive/scripts/fetch_sec_filing_markdown.py`
- Default SEC identity source must be `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) from `.env`.
- Identity overrides are exceptional; if needed, they must be explicit and auditable using `--allow-identity-override`.

## Why
- Ensures consistent `edgartools` retrieval behavior.
- Prevents accidental use of incorrect or placeholder identities.
- Produces local markdown artifacts and metadata that can be cited in reports.

## Minimal Usage

Historical filings:

```bash
python3 .agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K,10-Q,8-K \
  --limit 6 \
  --before <YYYY-MM-DD>
```

Single targeted filing (including peer filings):

```bash
python3 .agents/skills/run-llm-deep-dive/scripts/fetch_sec_filing_markdown.py \
  --ticker <TICKER> \
  --form 8-K \
  --filed-date <YYYY-MM-DD> \
  --output-path companies/US/<PRIMARY_TICKER>/data/filings/third_party/<NAME>.md
```
