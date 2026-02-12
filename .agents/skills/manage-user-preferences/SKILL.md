---
name: manage-user-preferences
description: Create or update `preferences/user_preferences.json` through an interactive conversation that captures market coverage, sector/industry preferences, strategy preferences, and report-content preferences.
---

# Manage User Preferences

## Overview

Use this skill when a user wants to create or update persistent preference settings for idea selection and report style.

Preference file:
- `preferences/user_preferences.json`

## Workflow

1. Read the existing preferences file if it exists.
2. Ask for Section 1 only: country markets of interest.
3. Rewrite Section 1 response into normalized JSON-friendly values.
4. Ask for Section 2 only: sector and industry include/exclude preferences.
5. Rewrite Section 2 response into normalized JSON-friendly values.
6. Ask for Section 3 only: preferred and excluded investment strategy styles.
7. Rewrite Section 3 response into normalized JSON-friendly values.
8. Ask for Section 4 only: report information preferences (`must_include`, `nice_to_have`, `exclude`).
9. Rewrite Section 4 response into normalized JSON-friendly values.
10. Confirm the final normalized summary with the user.
11. Persist the updated JSON in `preferences/user_preferences.json`.
12. Notify the user that the preference update is complete.

Important interaction rule:
- Do not ask all sections at once.
- Ask exactly one section at a time and wait for the user's answer before proceeding.

## Deterministic Helper

Use the helper script for deterministic write/normalize behavior:

```bash
python3 .agents/skills/manage-user-preferences/scripts/user_preferences.py interactive
```

Useful commands:

```bash
python3 .agents/skills/manage-user-preferences/scripts/user_preferences.py show
python3 .agents/skills/manage-user-preferences/scripts/user_preferences.py apply --payload-file /tmp/prefs.json
python3 .agents/skills/manage-user-preferences/scripts/user_preferences.py init
```

`apply` accepts a partial JSON payload and merges it into existing preferences before normalization.

## Output Contract

The saved JSON must include:
- `markets.included_countries`
- `sector_and_industry_preferences`
- `investment_strategy_preferences`
- `report_preferences`
- `updated_at_utc`

Use concise plain-language values in arrays (for example: `"US"`, `"Non-US"`, `"oil"`, `"biotech"`, `"value long"`).
