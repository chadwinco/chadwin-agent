# Historical SEC Fetch (US, Optional)

Use this when recent filings are insufficient to resolve a high-impact downside hypothesis.

Helper script:
- `.agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py`

## Typical Use Cases
- Check how margins and disclosure language behaved in prior downturns.
- Validate whether management repeated patterns in accounting or guidance quality.
- Pull older 8-K/10-Q events around specific stress periods.

## Prerequisites
- US ticker package exists under `companies/US/<TICKER>/data`.
- `EDGAR_IDENTITY` set in `.env` (or pass `--identity`).

## Command Examples

Pull last 6 filings per form through a cutoff date:

```bash
python3 .agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K,10-Q,8-K \
  --limit 6 \
  --before <YYYY-MM-DD>
```

Pull only older annual filings:

```bash
python3 .agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K \
  --limit 10 \
  --before <YYYY-MM-DD>
```

Files are written to:
- `companies/US/<TICKER>/data/filings/historical/`

## Guardrails
- Keep pull scope tight to the hypothesis you are testing.
- Respect revised as-of date; do not include future-dated evidence.
- Treat fetched files as candidate evidence, not automatic truth. Validate claim relevance before using.
