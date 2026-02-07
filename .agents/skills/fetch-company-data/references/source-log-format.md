# Source Log Format

Update `docs/source-log.md` when this skill adds external sources.

## Table format
`| Date | Company | Source | URL or File | Notes |`

## Required entries from this skill
- Transcript row if a transcript is found.
- Local data snapshot row is written by the analysis pipeline (`scripts/run_company.py`).

## Transcript example
`| 2026-02-06 | NFLX | Earnings Call Transcript | https://www.fool.com/... | Saved to companies/NFLX/data/filings/earnings-call-2026-01-20-fool.com.md |`
