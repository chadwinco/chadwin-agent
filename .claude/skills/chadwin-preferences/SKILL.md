---
name: chadwin-preferences
description: Create or update free-form markdown preferences at `<DATA_ROOT>/user_preferences.md` through open conversation.
---

# Manage User Preferences

## Overview

Use this skill when a user wants to create or revise persistent preferences in their own words.

Preference file:
- `<DATA_ROOT>/user_preferences.md`

## Shared Contract Guardrails
- Update only `<DATA_ROOT>/user_preferences.md`; do not move or rename this file.
- Keep the content markdown/plain-text only (no JSON contract).
- Allow any preference content; do not force sections, key names, or taxonomy.
- No legacy migration behavior. Current primitive is markdown.

## Execution Mode

This skill is intentionally LLM-operated.
- Do not rely on deterministic parser scripts for this workflow.
- Drive updates through natural conversation and write markdown directly.

## Workflow

1. Read `<DATA_ROOT>/user_preferences.md` if it exists.
2. Ask open-ended follow-up questions only as needed to capture what the user wants changed.
3. Draft updated markdown that reflects the user's intent in their own language.
4. Confirm the draft with the user before final write when the requested edits are ambiguous.
5. Persist to `<DATA_ROOT>/user_preferences.md`.
6. Validate the shared data contract:

```bash
.venv/bin/python ".agents/skills/chadwin-setup/scripts/validate_data_contract.py"
```

7. Notify the user that the preference update is complete.

Interaction rule:
- Do not hard-steer the user into preset categories.
- When possible, preserve user wording and tone instead of re-encoding into rigid structures.
