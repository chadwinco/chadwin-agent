---
name: run-llm-workflow
description: Produce a concise, LLM-written investment summary and scenario valuation from `companies/TICKER/data`. Use after running the market-appropriate fetch skill (`$fetch-us-company-data` or `$fetch-japanese-company-data`) when creating or refreshing `companies/TICKER/reports/YYYY-MM-DD/report.md` and valuation files. This skill is intentionally non-scripted and should be executed as an LLM workflow, not a one-command analysis script.
---

# Run LLM Workflow

## Overview
This is an LLM-first research workflow. The target output is intentionally simple:
1. A short investment summary for a company.
2. A transparent base/bull/bear valuation.

Do not use a deterministic end-to-end analysis script for this skill.

## Execution Mode (Required)
- Execute this skill by reasoning through the workflow and writing outputs.
- Do not look for or invent a single `scripts/*.py` command that completes the report.
- Helper commands are fine for extraction or arithmetic, but they do not replace the LLM workflow.
- The task is complete only when all required output files are written and the quality gate passes.

## Quick Start
1. Resolve ticker and confirm as-of date with the user.
2. Ensure `companies/<TICKER>/data` is populated. If not, run the appropriate fetch skill first (`$fetch-us-company-data` or `$fetch-japanese-company-data`).
3. Create the output directory from the repo root:

```bash
mkdir -p companies/<TICKER>/reports/<YYYY-MM-DD>/valuation
```
4. Work through `references/research-workflow.md` as an LLM task (no one-shot script).
5. After report completion and quality gate pass, remove the researched ticker from `idea-screens/company-ideas-log.jsonl`.

## Queue Helpers
Use the queue CLI owned by the `$research` skill from repo root:

```bash
python3 .agents/skills/research/scripts/company_idea_queue.py pick --task run-llm-workflow
python3 .agents/skills/research/scripts/company_idea_queue.py remove --ticker <TICKER>
```

- If ticker is omitted, the `pick` command above is the default selection source.
- The `remove` command should run only after required outputs are finalized and Step 6 quality gates pass.

## Required Outputs
- `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

## Workflow
1. Work through the end-to-end process in `references/research-workflow.md` manually as an LLM workflow.
2. Build valuation assumptions and outputs using `references/valuation-method.md`.
3. Draft the report using `references/report-format.md`.
4. Check all quality gates in `references/research-workflow.md` (Step 6) before finalizing.
5. Remove the completed ticker from `idea-screens/company-ideas-log.jsonl`.
6. Record learnings using `references/improvement-loop.md`.

## Constraints
- Keep the report concise and decision-oriented.
- Paraphrase source text; no verbatim copying from filings or transcripts.
- Every factual claim needs a local file citation.

## Troubleshooting
- If you are looking for a one-command analyzer (for example, `scripts/analyze_company.py`), stop and return to the LLM workflow in `references/research-workflow.md`.
- If no ticker was supplied and queue selection fails, run the queue helper (`pick --task run-llm-workflow`) and confirm the log has candidates.
- If required data is missing, run the appropriate fetch skill for that ticker/date (`$fetch-us-company-data` or `$fetch-japanese-company-data`).
- If valuation looks inconsistent, re-check units and net debt sign in `references/valuation-method.md`.
- If the write-up is weak, rerun the Step 6 quality gate in `references/research-workflow.md` and fix every unchecked item.

## Related References
- `references/research-workflow.md`
- `references/report-format.md`
- `references/valuation-method.md`
- `references/improvement-loop.md`
