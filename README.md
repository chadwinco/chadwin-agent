# Chadwin Codex Research Repo

## What This Project Does
This repository is an LLM-assisted equity research workflow focused on long-term value assessment.

For a given ticker, it:
1. Fetches local company data (SEC filings, financial statements, analyst estimates, and transcript content when available).
2. Produces a concise research report plus scenario-based valuation outputs.

The main goal is repeatable, evidence-backed analysis with clear assumptions and traceable artifacts.

## Quick Start (Humans)
Run from repo root (`/Users/chad/source/chadwin-codex`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If you plan to run US/EDGAR fetches, configure identity in `.env`:

```bash
EDGAR_IDENTITY="Your Name your.email@example.com"
```

## How Work Is Organized
The workflow is split into an orchestration skill, market-specific fetch skills, and an LLM report skill:
- Orchestration wrapper: `.agents/skills/research/SKILL.md`
- US data fetch/bootstrap: `.agents/skills/fetch-us-company-data/SKILL.md`
- Japan data fetch/bootstrap: `.agents/skills/fetch-japanese-company-data/SKILL.md`
- Research + valuation write-up: `.agents/skills/run-llm-workflow/SKILL.md`

Use them in this order:
0. (Optional but recommended) Run `$fetch-us-investment-ideas` to seed the central queue log at `idea-screens/company-ideas-log.jsonl`.
1. Run `$research` (or run fetch skills manually if tighter control is needed).
2. If using manual flow, run the country-appropriate fetch skill (`$fetch-us-company-data` or `$fetch-japanese-company-data`).
3. Run `$run-llm-workflow`.

If ticker/identifier is omitted when running a fetch or research skill, the workflow now selects from `idea-screens/company-ideas-log.jsonl` when a matching candidate exists.

## Repository Structure
- `companies/<TICKER>/data/`
  - Raw/processed local inputs used for analysis.
- `companies/<TICKER>/reports/<YYYY-MM-DD>/`
  - Point-in-time outputs for a run date.
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/`
  - Assumptions and computed valuation outputs.
- `docs/`
  - Process-level notes and logs.
- `.agents/skills/`
  - The authoritative workflow instructions and templates.

## Output Contract (Per Ticker/Date)
Expected artifacts for each completed research run:
- `companies/<TICKER>/reports/<YYYY-MM-DD>/report.md`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

## Current Valuation Approach
The active method is a three-stage DCF with:
- Competitive-advantage period
- Fade period
- Terminal period

Authoritative method details live in:
- `.agents/skills/run-llm-workflow/references/valuation-method.md`

## Agent Notes (Important)
- Treat local files under `companies/<TICKER>/data` as primary evidence.
- Keep as-of dates explicit and consistent across all generated outputs.
- Every factual claim in reports should cite a local file path.
- Prefer SEC filings for core financial/forecast claims; use third-party transcript files mainly for qualitative color.
- Do not duplicate workflow logic in ad hoc docs; update skill references when process changes are needed.

## Setup and Operational References
- Fetch outputs and data definitions:
  - `.agents/skills/fetch-us-company-data/references/data-outputs.md`
  - `.agents/skills/fetch-us-company-data/references/data-dictionary.md`
  - `.agents/skills/fetch-japanese-company-data/references/data-outputs.md`
  - `.agents/skills/fetch-japanese-company-data/references/data-dictionary.md`
- Skill-level Python setup:
  - `.agents/skills/fetch-us-company-data/references/python-setup.md`
  - `.agents/skills/fetch-japanese-company-data/references/python-setup.md`
  - `.agents/skills/fetch-us-investment-ideas/references/python-setup.md`
- Research workflow and quality gate:
  - `.agents/skills/run-llm-workflow/references/research-workflow.md`
  - `.agents/skills/run-llm-workflow/references/report-format.md`
- Manual validation scenarios:
  - `.agents/skills/research/references/workflow-validation-scenarios.md`
- Process learning history:
  - `docs/improvement-log.md`

## How to Evolve the System
When a repeatable issue appears:
1. Record it in `docs/improvement-log.md`.
2. Update the relevant skill reference (not just a single report output).
3. Validate with at least one end-to-end ticker run.

This keeps improvements durable for future agent runs.
