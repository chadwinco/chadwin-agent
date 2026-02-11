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
2. Run an interactive conversation with the user to capture:
- country markets of interest
- sector and industry include/exclude preferences
- preferred investment strategy style(s) and excluded styles
- report information preferences (must include, nice to have, exclude)
3. Confirm the final normalized summary with the user.
4. Persist the updated JSON in `preferences/user_preferences.json`.

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

Use concise plain-language values in arrays (for example: `"US"`, `"Japan"`, `"oil"`, `"biotech"`, `"value long"`).
