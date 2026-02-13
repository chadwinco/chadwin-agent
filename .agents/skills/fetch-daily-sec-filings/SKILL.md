---
name: fetch-daily-sec-filings
description: Fetch daily SEC filing lists for 10-K, 10-Q, 20-F, 8-K, 6-K, and S-1 and write them to .chadwin-data/daily-sec-filings/FORM/YYYY-MM-DD.jsonl with company name, ticker, form type, filing date, and accession number. Use when you need a deterministic business-day filing feed, a historical backfill of filing events, or machine-readable per-form filing snapshots for downstream workflows.
---

# Fetch Daily SEC Filings

## Overview
Generate daily JSON snapshots from EDGAR using `edgartools` for these forms only:
- `10-K`
- `10-Q`
- `20-F`
- `8-K`
- `6-K`
- `S-1`

Write one JSONL file per business day per form to `.chadwin-data/daily-sec-filings/<FORM>/YYYY-MM-DD.jsonl`.

## Quick Start
Run from repo root:

```bash
.venv/bin/python .agents/skills/fetch-daily-sec-filings/scripts/fetch_daily_sec_filings.py
```

By default this resolves to the latest completed filing day (not necessarily today).

Force same-day output:

```bash
.venv/bin/python .agents/skills/fetch-daily-sec-filings/scripts/fetch_daily_sec_filings.py \
  --date-mode today
```

Fetch an arbitrary single date:

```bash
.venv/bin/python .agents/skills/fetch-daily-sec-filings/scripts/fetch_daily_sec_filings.py \
  --date 2026-02-12
```

Fetch a backfill range:

```bash
.venv/bin/python .agents/skills/fetch-daily-sec-filings/scripts/fetch_daily_sec_filings.py \
  --start-date 2026-02-10 \
  --end-date 2026-02-13
```

Pass identity directly when needed:

```bash
.venv/bin/python .agents/skills/fetch-daily-sec-filings/scripts/fetch_daily_sec_filings.py \
  --date 2026-02-12 \
  --identity "Your Name your_email@domain.com"
```

## Inputs
- `--date` (optional): `YYYY-MM-DD` single-day fetch
- `--start-date` (optional): `YYYY-MM-DD` range start
- `--end-date` (optional): `YYYY-MM-DD`, defaults to `--start-date`
- `--date-mode` (optional): `latest-complete` or `today`; used only when no explicit date args are passed
- `--lookback-days` (optional): backward scan depth for `latest-complete` mode (default `14`)
- `--identity` (optional): SEC User-Agent identity string; if omitted, use `EDGAR_IDENTITY` or `SEC_IDENTITY_EMAIL`
- `--output-root` (optional): output directory; defaults to `.chadwin-data/daily-sec-filings`
- If no date argument is provided, default mode is `latest-complete`.

## Output Layout
- `.chadwin-data/daily-sec-filings/10-K/YYYY-MM-DD.jsonl`
- `.chadwin-data/daily-sec-filings/10-Q/YYYY-MM-DD.jsonl`
- `.chadwin-data/daily-sec-filings/20-F/YYYY-MM-DD.jsonl`
- `.chadwin-data/daily-sec-filings/8-K/YYYY-MM-DD.jsonl`
- `.chadwin-data/daily-sec-filings/6-K/YYYY-MM-DD.jsonl`
- `.chadwin-data/daily-sec-filings/S-1/YYYY-MM-DD.jsonl`

Each JSONL line is one filing object with:
- `company_name`
- `ticker`
- `form_type`
- `filing_date`
- `accession_number`

## Workflow
1. Resolve date window (`--date`, `--start-date/--end-date`, or `--date-mode`; default `latest-complete`).
2. Resolve SEC identity from `--identity` or environment.
3. Fetch filings for the date window with `get_filings(..., form=[...], amendments=False)`.
4. Map `CIK -> primary ticker` from SEC company tickers data.
5. Write one JSONL per business day (Mon-Fri) for each target form.
6. Overwrite existing day files to keep reruns deterministic.

## Why JSONL
- Keep files append/stream-friendly for downstream pipelines.
- Keep diffs compact for line-oriented reviews.
- Avoid loading a full array in memory in simple consumers.

## Notes
- Keep `ticker` nullable because some filers do not have exchange tickers in SEC mappings.
- Expect multiple tickers for some CIKs; the script picks one deterministic primary ticker.
