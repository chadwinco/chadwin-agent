# SEC Access Policy (Required for SEC Retrieval)

Use these rules whenever this workflow pulls SEC evidence.

## Rules
- Do not call `sec.gov` directly with ad-hoc `curl`, `wget`, `requests`, `urllib`, or browser scraping.
- Use `$fetch-us-company-data` as the SEC retrieval operator for this workflow.
- Preferred interface is natural-language fetch objectives.
- Deterministic wrapper requests are optional when replay/auditability is required.
- Default SEC identity source is `EDGAR_IDENTITY` (or `SEC_IDENTITY_EMAIL`) from repo `.env`.
- Identity overrides are exceptional and must be explicit and auditable.
- Enforce as-of date cutoffs in every SEC fetch objective.

## Why
- Keeps SEC retrieval behavior consistent through one skill surface.
- Preserves LLM-first flexibility while retaining deterministic execution options.
- Produces local artifacts that can be cited directly in reports.

## Natural-Language Usage Pattern
When a lever is blocked, request focused evidence from `$fetch-us-company-data`, for example:
- "For `<TICKER>` as of `<YYYY-MM-DD>`, fetch the latest 10-K, all subsequent 10-Q filings, and 8-K filings related to guidance/capital allocation. Include attachments and save markdown under the company data filings path."
- "For `<TICKER>`, fetch Form 4 transactions for the last 6 months and save structured CSV outputs under the company data path."

## Deterministic Mode (Optional)
If strict replay is needed, run the fetch skill wrapper explicitly:

```bash
python3 "${CHADWIN_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}/fetch-us-company-data/scripts/edgartools_wrapper.py" \
  --request-file <request.json> \
  --pretty
```
