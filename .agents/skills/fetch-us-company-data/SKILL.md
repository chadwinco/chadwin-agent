---
name: fetch-us-company-data
description: LLM-first edgartools operator skill for US/SEC data retrieval. Use when another skill needs specific EDGAR data and wants this skill to execute the fetch plan from natural-language instructions or an explicit wrapper request.
---

# Fetch US Company Data

## Overview
This skill is an LLM-focused edgartools operator.

It is designed for other skills to say what they want in plain language (for example: "Fetch the most recent 10-K and any subsequent 10-Qs") and have this skill execute the right edgartools calls.

`scripts/add_company.py` is not part of this skill contract and is unsupported.

## Interaction Model (LLM-First)
Preferred mode between skills: natural language.

Use structured request JSON/YAML only when you explicitly need reproducibility or deterministic replay.

Natural-language request example:
- "Fetch the latest 10-K for AAPL, then all 10-Q filings after that 10-K, include filing markdown plus XBRL statements, and also fetch last 6 months of Form 4 filings as CSV."

## Skill Paths (set once)
Installed skill (default):

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export FETCH_US_COMPANY_DATA_ROOT="$CODEX_HOME/skills/fetch-us-company-data"
export FETCH_US_COMPANY_DATA_WRAPPER="$FETCH_US_COMPANY_DATA_ROOT/scripts/edgartools_wrapper.py"
```

Standalone clone (development):

```bash
export FETCH_US_COMPANY_DATA_ROOT="/path/to/fetch-us-company-data"
export FETCH_US_COMPANY_DATA_WRAPPER="$FETCH_US_COMPANY_DATA_ROOT/scripts/edgartools_wrapper.py"
```

## Full Data Availability
Complete catalog of fetchable data (from current edgartools docs):
- `references/edgartools-data-catalog.md`

This catalog is the source of truth for what this skill can fetch.

## Execution

### A) Natural-language mode (default)
1. Read the caller's objective.
2. Map objective to edgartools operations.
3. Execute via `scripts/edgartools_wrapper.py`.
4. Save outputs requested by caller (CSV/JSON/Markdown/etc).
5. Return artifact paths and short execution summary.

### B) Structured request mode (optional)
Run with explicit request file:

```bash
python3 "$FETCH_US_COMPANY_DATA_WRAPPER" --request-file <request.json> --pretty
```

Or inline JSON:

```bash
python3 "$FETCH_US_COMPANY_DATA_WRAPPER" --request-json '<json-object>' --pretty
```

Optional flags:
- `--identity "Name email@domain.com"`
- `--output-root <PATH>`
- `--base-dir <PATH>`

## Structured Request Contract (if used)
Top-level keys:
- `identity` (optional)
- `identity_required` (default `true`)
- `variables` (optional object)
- `steps` (required list)
- `outputs` (optional object/list)

Step operations:
- `call`
- `read`
- `value`

Value interpolation:
- `{"$ref": "step_id"}`
- `{"$path": "step_id.field"}`
- `{"$var": "name"}`
- `{"$env": "ENV_VAR", "default": "fallback"}`
- `{"$literal": <any>}`

Exports:
- formats: `json`, `yaml`, `csv`, `markdown`, `text`, `bytes`, `auto`
- common fields: `path`, `format`, `include_attachments`, `index`, `dataframe_kwargs`

## Related References
- `references/edgartools-data-catalog.md`
- `references/edgartools-wrapper.md`
- [edgartools docs](https://edgartools.readthedocs.io/en/latest/)
