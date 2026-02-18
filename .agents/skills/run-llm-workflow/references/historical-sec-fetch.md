# Historical SEC Fetch (US, Optional, On-Demand)

Use this when currently available filings are insufficient to resolve a high-impact issue.

Default operator:
- `$fetch-us-company-data`

## Typical Use Cases
- Test margin/disclosure behavior in prior downturns.
- Check repeat-pattern risk in accounting, guidance, or governance.
- Pull older event filings around stress periods.
- Build insider-trading context (Form 4) around key thesis turns.

## Prerequisites
- SEC identity is configured in repo `.env` (`EDGAR_IDENTITY` or `SEC_IDENTITY_EMAIL`).
- Follow `references/sec-access-policy.md`.
- Keep requests bounded by as-of date.

## Natural-Language Request Patterns
Historical periodic/event set:
- "For `<TICKER>` as of `<YYYY-MM-DD>`, fetch historical `10-K`, `10-Q`, and `8-K` filings before cutoff; prioritize the last 6-10 filings per form; include attachments when relevant."

Older annual-only set:
- "For `<TICKER>`, fetch prior `10-K` history before `<YYYY-MM-DD>` to analyze long-cycle margin behavior."

Single targeted filing:
- "Fetch `<TICKER>` `<FORM>` filed on `<YYYY-MM-DD>` and save markdown under `<DATA_ROOT>/companies/US/<PRIMARY_TICKER>/data/filings/third_party/`."

Insider history:
- "For `<TICKER>`, fetch Form 4 data for the last `<N>` months ending `<YYYY-MM-DD>` and export transactions to CSV."

## Guardrails
- Keep pull scope tight to the active issue being tested.
- Do not include evidence after the as-of date.
- Validate fetched files for relevance before using them in assumptions.
