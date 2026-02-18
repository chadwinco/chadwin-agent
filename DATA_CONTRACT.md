# Chadwin Data Contract

This file defines the shared local-data primitives that all skills must respect.

Goal: skills are swappable as long as they preserve these primitives.

## Data Root

`<DATA_ROOT>` resolves to:
- `CHADWIN_DATA_DIR` when set.
- Otherwise OS app-data:
  - macOS: `~/Library/Application Support/Chadwin`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/Chadwin`
  - Windows: `%APPDATA%/Chadwin`

## Required Shared Primitives

These paths are reserved and must remain valid:

- `<DATA_ROOT>/user_preferences.json`
- `<DATA_ROOT>/idea-screens/company-ideas-log.jsonl`
- `<DATA_ROOT>/companies/`
- `<DATA_ROOT>/improvement-log.md`

### Company Package Primitive

Each company package lives at:

- `<DATA_ROOT>/companies/<COUNTRY_CODE>/<TICKER>/`

Rules:
- `<COUNTRY_CODE>` must be uppercase ISO 3166-1 alpha-2 (for example `US`, `JP`, `GB`).
- Company package should contain:
  - `data/`
  - `reports/`

### Research Run Primitive

Each report run instance lives at:

- `<DATA_ROOT>/companies/<COUNTRY_CODE>/<TICKER>/reports/<REPORT_DATE_DIR>/`

`<REPORT_DATE_DIR>` must match:
- `YYYY-MM-DD`
- `YYYY-MM-DD-##` (for additional runs on the same as-of date)

A completed run must contain:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

## Queue Primitive (`company-ideas-log.jsonl`)

One JSON object per line.

Required fields:
- `ticker`
- `market` (`us` or `non-us`)

Recommended fields:
- `exchange_country` (ISO alpha-2; use `US` for US listings)
- `company`
- `exchange`
- `sector`
- `industry`
- `thesis`
- `source`
- `generated_at_utc`
- `queued_at_utc`
- `source_output`

## Preferences Primitive (`user_preferences.json`)

Required top-level keys:
- `markets`
- `sector_and_industry_preferences`
- `investment_strategy_preferences`
- `report_preferences`
- `updated_at_utc`

`markets.included_countries` accepts:
- ISO 3166-1 alpha-2 uppercase country codes only (for example `US`, `JP`, `GB`).
- Non-country tokens (for example `NON-US`, `GLOBAL`) are not valid in this field.

## Skill Extension Rules

Skills may store additional data if they do not violate shared primitives.

Allowed extension zones:
- New top-level namespaces under `<DATA_ROOT>/<skill-or-purpose>/...`
- Additional files under company packages (for example `<DATA_ROOT>/companies/<COUNTRY>/<TICKER>/data/<custom>/...`)
- Additional files under report packages (for example `<DATA_ROOT>/companies/<COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/<custom>/...`)

Not allowed:
- Renaming or repurposing required shared primitive paths.
- Writing non-canonical valuation output files such as `valuation/output.json`.
- Overwriting completed report packages.

## Validation

Validate contract compliance with:

```bash
.venv/bin/python .agents/skills/chadwin-setup/scripts/validate_data_contract.py
```
