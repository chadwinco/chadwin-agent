# Historical SEC Fetch (US, Optional)

Use this when recent filings are insufficient to resolve a high-impact downside hypothesis.

Helper script:
- `.agents/skills/run-llm-deep-dive/scripts/fetch_historical_filings.py`
- `.agents/skills/run-llm-deep-dive/scripts/fetch_sec_filing_markdown.py` (targeted filing fetch)

## Typical Use Cases
- Check how margins and disclosure language behaved in prior downturns.
- Validate whether management repeated patterns in accounting or guidance quality.
- Pull older 8-K/10-Q events around specific stress periods.

## Prerequisites
- US ticker package exists under `companies/US/<TICKER>/data`.
- `EDGAR_IDENTITY` set in `.env` (or pass `--identity` with explicit override intent).
- Follow `references/sec-access-policy.md`.

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

Pull a specific filing (for example peer 8-K) into local markdown:

```bash
python3 .agents/skills/run-llm-deep-dive/scripts/fetch_sec_filing_markdown.py \
  --ticker <PEER_TICKER> \
  --form 8-K \
  --filed-date <YYYY-MM-DD> \
  --output-path companies/US/<PRIMARY_TICKER>/data/filings/third_party/<PEER_FILE>.md
```

Files are written to:
- `companies/US/<TICKER>/data/filings/historical/`

## Guardrails
- Keep pull scope tight to the hypothesis you are testing.
- Respect revised as-of date; do not include future-dated evidence.
- Treat fetched files as candidate evidence, not automatic truth. Validate claim relevance before using.
- Do not fetch SEC pages with ad-hoc direct HTTP tooling; use the skill SEC scripts so identity and provenance are controlled.
- `fetch_historical_filings.py` and `fetch_sec_filing_markdown.py` default to `.env` identity and block mismatched `--identity` unless `--allow-identity-override` is set.
