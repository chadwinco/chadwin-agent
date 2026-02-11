---
name: fetch-us-investment-ideas
description: Fetch a structured list of possible US stock investment ideas with ticker-level value and quality rationale. Use when you need fresh NASDAQ/NYSE/AMEX candidates for idea generation, watchlist seeding, or downstream research workflows that require machine-readable `ticker` plus short thesis output.
---

# Fetch US Investment Ideas

## Overview
Screen US exchange-listed stocks with a value + quality filter and output structured JSON that is easy for other app components to consume.

Each run also appends newly discovered companies to the central queue log at `idea-screens/company-ideas-log.jsonl` so downstream skills can run without an explicitly provided ticker.
When present, `preferences/user_preferences.json` is applied by default:
- US market guardrail (skip/fail if US is excluded)
- sector/industry include/exclude filtering

## Skill Path (set once)
Repo-local:

```bash
export FETCH_US_INVESTMENT_IDEAS_ROOT=".agents/skills/fetch-us-investment-ideas"
export FETCH_US_INVESTMENT_IDEAS_CLI="$FETCH_US_INVESTMENT_IDEAS_ROOT/scripts/fetch_us_investment_ideas.py"
```

## Quick Start
1. Follow `references/python-setup.md`.
2. Run the screener:

```bash
python3 "$FETCH_US_INVESTMENT_IDEAS_CLI" \
  --limit 25 \
  --output idea-screens/$(date +%F)/us-investment-ideas.json
```

3. Consume `ideas[]` in the output JSON for `ticker` + short `thesis`.
4. Check `idea-screens/company-ideas-log.jsonl` for appended queue entries.

## Required Output Shape
The script emits JSON with this top-level structure:

```json
{
  "generated_at_utc": "2026-02-07T18:00:00+00:00",
  "source": "finviz_screener",
  "universe": {"country": "USA", "exchanges": ["NASDAQ", "NYSE", "AMEX"]},
  "filters": {...},
  "ideas": [
    {
      "ticker": "EXAMPLE",
      "company": "Example Inc.",
      "exchange": "NASDAQ",
      "sector": "Technology",
      "industry": "Software - Application",
      "score": 87.5,
      "thesis": "Possible value-quality setup: ...",
      "metrics": {...}
    }
  ]
}
```

Downstream consumers should read `ideas[*].ticker` and `ideas[*].thesis`.

## Workflow
1. Run `scripts/fetch_us_investment_ideas.py` with the desired thresholds.
2. Keep default exchange scope (NASDAQ/NYSE/AMEX only) unless explicitly asked to broaden.
3. By default, apply `preferences/user_preferences.json` for market + sector/industry filtering.
4. Use `--output` for deterministic handoff to other app components.
5. Verify the result contains non-empty `ideas` and each idea has `ticker` + `thesis`.
6. Confirm new tickers were appended to `idea-screens/company-ideas-log.jsonl`.

## Key Flags
- `--limit`: max number of returned ideas.
- `--max-pages-per-exchange`: controls breadth of scan per exchange.
- `--min-market-cap-b`: minimum market cap in billions USD.
- `--max-pe`: valuation cap (trailing P/E).
- `--min-roe`, `--min-roic`, `--min-operating-margin`, `--min-profit-margin`, `--max-debt-to-equity`: quality gates.
- `--output`: write JSON to file.
- `--compact`: emit minified JSON.
- `--ideas-log`: override central queue log path (defaults to `idea-screens/company-ideas-log.jsonl`).
- `--base-dir`: override repo root used for queue log resolution.
- `--preferences-path`: override preferences path (default `preferences/user_preferences.json`).
- `--ignore-preferences`: ignore preference-based market/sector filters.

## Troubleshooting
- If output is empty, loosen thresholds (for example raise `--max-pe` or lower `--min-roic`).
- If preferences exclude US market, update `preferences/user_preferences.json` or rerun with `--ignore-preferences`.
- If requests fail intermittently, raise `--request-delay` and retry.
- If `beautifulsoup4` is missing, install dependencies from `requirements.txt`.

## Related References
- `references/python-setup.md`
