---
name: manage-user-preferences
description: Create or update `user_preferences.json` through an interactive conversation that captures market coverage, sector/industry preferences, strategy preferences, and report-content preferences.
---

# Manage User Preferences

## Overview

Use this skill when a user wants to create or update persistent preference settings for idea selection and report style.

Preference file:
- `user_preferences.json`

## Execution Mode

This skill is intentionally LLM-operated.
- Do not rely on deterministic parser scripts for this workflow.
- The agent should run a structured interview, normalize responses with judgment, then write JSON directly.

## Workflow

1. Read `user_preferences.json` if it exists; otherwise start from the output contract schema.
2. Ask Section 1 only: country markets of interest.
3. Normalize Section 1 into `markets.included_countries`.
4. Ask Section 2 only: sector and industry include/exclude preferences.
5. Normalize Section 2 into `sector_and_industry_preferences`.
6. Ask Section 3 only: preferred and excluded investment strategy styles.
7. Normalize Section 3 into `investment_strategy_preferences`.
8. Ask Section 4 only: report information preferences (`must_include`, `nice_to_have`, `exclude`).
9. Normalize Section 4 into `report_preferences`.
10. Confirm the final normalized summary with the user.
11. Persist the updated JSON in `user_preferences.json`.
12. Notify the user that the preference update is complete.

Interaction rule:
- Ask exactly one section at a time; do not ask all sections in one message.

Normalization rules:
- Markets:
  - Prefer `US`, `Non-US`, and `Global` for broad buckets.
  - Keep explicit country names when the user is specific (for example `Sweden`, `Japan`).
- Section keys:
  - `sector_and_industry_preferences`: `preferred_sectors`, `preferred_industries`, `excluded_sectors`, `excluded_industries`, `notes`
  - `investment_strategy_preferences`: `preferred_strategies`, `excluded_strategies`, `notes`
  - `report_preferences`: `must_include`, `nice_to_have`, `exclude`, `notes`
- For list fields:
  - Split comma/semicolon/newline phrasing into arrays.
  - Trim whitespace and de-duplicate case-insensitively.
- Keep `notes` concise plain text.

## Output Contract

The saved JSON must include:
- `markets.included_countries`
- `sector_and_industry_preferences`
- `investment_strategy_preferences`
- `report_preferences`
- `updated_at_utc`

Use concise plain-language values in arrays (for example: `"US"`, `"Non-US"`, `"oil"`, `"biotech"`, `"value long"`).
