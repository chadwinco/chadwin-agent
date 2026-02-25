---
name: chadwin-activity-log
description: Append high-level, timestamped activity entries to `<DATA_ROOT>/activity-log.md` for major user-visible actions.
---

# Write Activity Log Entries

## Overview
Use this skill to append one concise markdown log entry for major activity.

Log file:
- `<DATA_ROOT>/activity-log.md`

Major activity examples:
- completing a `chadwin-research` run,
- running `fetch-us-company-data` for a user request,
- running `fetch-us-investment-ideas`,
- meaningful non-skill chats that changed preferences, plans, or outputs.

## Shared Contract Guardrails
- Write only to `<DATA_ROOT>/activity-log.md`.
- Append-only behavior: never delete, reorder, or rewrite prior entries.
- Keep entries concise and high-level; do not dump long reasoning traces.
- Include an explicit timestamp on every entry.
- Keep content markdown/plain text (no JSON contract).

## Execution Mode
This skill is intentionally LLM-operated.
- Write entries directly in markdown.
- Do not use deterministic summarizer scripts.

## Entry Format
Append entries using this shape:

```markdown
## 2026-02-25T19:40:00Z | <activity-type>
- <1-3 sentence high-level outcome>
```

Formatting rules:
- Use UTC ISO-8601 with trailing `Z` for timestamps.
- `activity-type` examples: `chadwin-research`, `fetch-us-company-data`, `fetch-us-investment-ideas`, `preferences-update`, `chat`.
- Write exactly one summary bullet under each timestamp header.

## Workflow
1. Read `<DATA_ROOT>/activity-log.md` if it exists.
2. Draft a concise, high-level summary of the completed activity.
3. Append exactly one new timestamped markdown entry.
4. Confirm prior log content remains unchanged.
5. Validate the shared data contract:

```bash
.venv/bin/python ".agents/skills/chadwin-setup/scripts/validate_data_contract.py"
```
