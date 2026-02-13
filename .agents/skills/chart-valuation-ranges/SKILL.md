---
name: chart-valuation-ranges
description: "Build a deterministic cross-ticker margin-of-safety snapshot for all companies folders by selecting each ticker's latest dated reports folder and reading valuation outputs.json (fallback: output.json), then generating a range-bar chart and JSON dataset. Use when the user asks to compare bear/base/bull margin_of_safety ranges across countries, see latest downside/upside dispersion, or present a portfolio-style valuation dashboard in Codex chat."
---

# Chart Valuation Ranges

## Overview
Render a single deterministic chart and machine-readable snapshot of latest margin-of-safety ranges (bear/base/bull) across all country folders from local report outputs.

## Quick Start
Run from repo root:

```bash
.venv/bin/python .agents/skills/chart-valuation-ranges/scripts/render_valuation_ranges.py
```

Generated files:
- `.chadwin-data/valuation-ranges/valuation-ranges.svg`
- `.chadwin-data/valuation-ranges/valuation-ranges.json`

## Workflow
1. Run the script.
2. Read stdout for skipped tickers and include that note if relevant.
3. Use the generated SVG in chat and the JSON for deterministic row values.

## Selection Rules
- Enumerate all company directories under `.chadwin-data/companies/<COUNTRY>/<TICKER>`.
- Backward-compatible mode: if `--companies-root` points to a single-country folder (for example `.chadwin-data/companies/US`), treat direct children as ticker folders.
- For each ticker, inspect `reports/` and choose the latest folder matching:
  - `YYYY-MM-DD`
  - `YYYY-MM-DD-01`, `YYYY-MM-DD-02`, etc.
- Resolve latest by `(date, run-suffix)` where missing suffix = `00`.
- Parse valuation data from:
  - preferred: `valuation/outputs.json`
  - fallback: `valuation/output.json`

## Output Semantics
- Plot one row per `COUNTRY/TICKER`:
  - Bear = `scenarios.bear.margin_of_safety`
  - Base = `scenarios.base.margin_of_safety`
  - Bull = `scenarios.bull.margin_of_safety`
- Render horizontal range bars (bear-to-bull span) with a base marker.
- Export JSON rows with country, ticker, label, as-of date, report path, and bear/base/bull margin-of-safety plus scenario value-per-share fields.

## Optional Flags
```bash
.venv/bin/python .agents/skills/chart-valuation-ranges/scripts/render_valuation_ranges.py \
  --sort-by spread --order desc --limit 20 \
  --title "Global Valuation Ranges - Top 20 by Spread"
```

Supported options:
- `--companies-root` (default `companies`)
- `--output-dir` (default `.chadwin-data/valuation-ranges`)
- `--sort-by` (`ticker|base|spread`)
- `--order` (`asc|desc`)
- `--limit` (`0` means no limit)
- `--title`
