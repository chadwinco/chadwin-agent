# Historical SEC Fetch (US, Optional)

Use this when recent filings are insufficient to resolve a high-impact issue.

Helper scripts:
- `.agents/skills/run-llm-workflow/scripts/fetch_historical_filings.py`
- `.agents/skills/run-llm-workflow/scripts/fetch_sec_filing_markdown.py`

## Typical Use Cases
- Check margin/disclosure behavior in prior downturns.
- Test repeat-pattern risk in accounting, guidance, or governance.
- Pull older event filings around stress periods.

## Prerequisites
- US package exists under `<DATA_ROOT>/companies/US/<TICKER>/data`.
- SEC helper deps listed in `../agents/openai.yaml` are installed.
- `EDGAR_IDENTITY` is set in repo `.env`.
- Follow `references/sec-access-policy.md`.

## Command Examples
Pull last 6 filings per form through cutoff date:

```bash
python3 .agents/skills/run-llm-workflow/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K,10-Q,8-K \
  --limit 6 \
  --before <YYYY-MM-DD>
```

Pull older annual filings only:

```bash
python3 .agents/skills/run-llm-workflow/scripts/fetch_historical_filings.py \
  --ticker <TICKER> \
  --forms 10-K \
  --limit 10 \
  --before <YYYY-MM-DD>
```

Pull one specific filing into local markdown:

```bash
python3 .agents/skills/run-llm-workflow/scripts/fetch_sec_filing_markdown.py \
  --ticker <PEER_TICKER> \
  --form 8-K \
  --filed-date <YYYY-MM-DD> \
  --output-path <DATA_ROOT>/companies/US/<PRIMARY_TICKER>/data/filings/third_party/<PEER_FILE>.md
```

Default output location:
- `<DATA_ROOT>/companies/US/<TICKER>/data/filings/historical/`

## Guardrails
- Keep pull scope tight to the issue being tested.
- Do not include evidence after the as-of date.
- Treat fetched files as candidate evidence; validate relevance before using.
