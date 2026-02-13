# Improvement Loop

Use this after each completed report to keep the skill improving.

## 1. Mandatory Post-Run Introspection (Every Run)
Review the full run path before closing the task:
- include command retries/failures, path mistakes, parser surprises, and assumption misunderstandings;
- identify the root cause (one-off operator miss vs workflow/documentation gap);
- decide whether a workflow/reference update would have prevented the issue.

## 2. Log Only Real Improvements
Append one row to `improvement-log.md` only when introspection results in a concrete, reusable workflow/process improvement:

`| Date | Area | Observation | Action |`

Focus on accuracy and misunderstanding prevention:
- weak or missing evidence
- unclear thesis
- valuation assumption drift
- noisy or overly long write-ups
- command/path mistakes caused by ambiguous instructions
- brittle parsing or formatting assumptions

Do not add no-change rows.

## 3. Patch the Workflow in the Same Run
When introspection finds a repeatable or workflow-caused issue, update one of:
- `references/research-workflow.md`
- `references/report-format.md`
- `references/valuation-method.md`
- `SKILL.md` (if routing/entrypoint guidance is unclear)
- relevant router/helper scripts (only when docs alone cannot prevent recurrence)

Keep changes concrete and minimal.

## 4. Preserve Decision Traceability
When assumptions change materially versus a prior run, explain why:
- in the report valuation section
- in the corresponding `improvement-log.md` row (when a real improvement entry is created)
