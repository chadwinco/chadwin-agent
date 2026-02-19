---
name: fetch-us-investment-ideas
description: Fetch a structured list of possible US stock investment ideas with ticker-level value and quality rationale. Use when you need fresh NASDAQ/NYSE/AMEX candidates for idea generation, watchlist seeding, or downstream research workflows that require machine-readable ticker plus short thesis output.
---

# Fetch US Investment Ideas

## Overview
This skill is LLM-driven. Do not force all idea generation through one deterministic screen.

Use one of these paths per run:
- LLM web-research path (default when user asks for flexibility): use native browsing/search, then emit structured JSON.
- Finviz helper path (optional): run `scripts/fetch_us_investment_ideas.py` when a deterministic value/quality seed list is useful.
- Optional local filing-seeded path: if filing snapshot JSONL files already exist under `<DATA_ROOT>/daily-sec-filings/*/*.jsonl` from an external process, use them as a seed universe before thesis selection.

Each completed run appends newly discovered companies to a per-screen queue file at `<DATA_ROOT>/idea-screens/<SCREEN_RUN_ID>/screener-results.jsonl` so downstream skills can choose among distinct screen lists.

When present, apply `<DATA_ROOT>/user_preferences.json` by default:
- US market guardrail (skip/fail if US is excluded)
- sector/industry include/exclude filtering

## Skill Path (set once)

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export CHADWIN_SKILLS_DIR="${CHADWIN_SKILLS_DIR:-$CODEX_HOME/skills}"
export FETCH_US_INVESTMENT_IDEAS_ROOT="$CHADWIN_SKILLS_DIR/fetch-us-investment-ideas"
export FETCH_US_INVESTMENT_IDEAS_CLI="$FETCH_US_INVESTMENT_IDEAS_ROOT/scripts/fetch_us_investment_ideas.py"
```

## Quick Start
1. Ensure `.venv` is active and install this skill's optional script dependencies from `agents/openai.yaml` (`dependencies.python_packages`).
2. Choose path:
- LLM web-research path: gather ideas with native web tools and write output JSON directly.
- Finviz helper path:

```bash
python3 "$FETCH_US_INVESTMENT_IDEAS_CLI" \
  --limit 25 \
  --output <DATA_ROOT>/idea-screens/$(date +%F)/us-investment-ideas.json
```

3. Ensure output JSON has an `ideas` array with `ticker` and `thesis`.
4. Append new ideas to queue log if not already appended by script:

```bash
python3 "${CHADWIN_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}/chadwin-research/scripts/company_idea_queue.py" append-json \
  --ideas-json <DATA_ROOT>/idea-screens/$(date +%F)/us-investment-ideas.json \
  --source fetch-us-investment-ideas
```

## Required Output Shape
The output JSON must follow this top-level shape:

```json
{
  "generated_at_utc": "2026-02-12T18:00:00+00:00",
  "source": "finviz_screener | llm_web_research | filing_seeded",
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
      "thesis": "Concise rationale",
      "metrics": {...}
    }
  ]
}
```

Downstream consumers should read `ideas[*].ticker` and `ideas[*].thesis`.

## Workflow
1. Decide path first:
- If user asked for broad/flexible sourcing, use LLM web research directly.
- If user asked for deterministic screening, use the Finviz helper script.
- If user asked for filing-date- or filing-form-driven ideas and local filing snapshots already exist, seed from those files.
2. Keep exchange scope to NASDAQ/NYSE/AMEX unless explicitly asked to broaden.
3. Apply preferences unless user overrides.
4. Write output JSON for deterministic handoff.
5. Verify non-empty `ideas`, with `ticker` + `thesis` per entry.
6. Confirm queue append in `<DATA_ROOT>/idea-screens/<SCREEN_RUN_ID>/screener-results.jsonl`.

## Key Flags (Finviz helper script)
- `--limit`: max number of returned ideas.
- `--max-pages-per-exchange`: controls scan breadth per exchange.
- `--min-market-cap-b`: minimum market cap in billions USD.
- `--max-pe`: valuation cap (trailing P/E).
- `--min-roe`, `--min-roic`, `--min-operating-margin`, `--min-profit-margin`, `--max-debt-to-equity`: quality gates.
- `--output`: write JSON to file.
- `--compact`: emit minified JSON.
- `--ideas-log`: override screener results path (file or directory; defaults to `<DATA_ROOT>/idea-screens/**/screener-results.jsonl`).
- `--base-dir`: override repo root used for queue log resolution.
- `--preferences-path`: override preferences path (default `<DATA_ROOT>/user_preferences.json`).
- `--ignore-preferences`: ignore preference-based market/sector filters.

## Troubleshooting
- If Finviz output is empty, loosen thresholds (for example raise `--max-pe` or lower `--min-roic`).
- If preferences exclude US market, update `<DATA_ROOT>/user_preferences.json` or rerun with `--ignore-preferences`.
- If requests fail intermittently, raise `--request-delay` and retry.
- If script dependencies are missing, install the packages listed in `agents/openai.yaml`.
