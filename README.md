# Chadwin Codex Research Repo

This repository is a Codex-operated equity research system.

## Intended Usage (Codex Only)
Use this repo inside Codex, by asking the agent to run Skills.

- Humans should request outcomes in natural language or by naming a Skill.
- The agent executes scripts and shell commands as part of Skill workflows.
- Humans are not expected to run raw bash commands to operate the repo.

Agent operating rules and workflow contract are in:
- `chadwin-codex/AGENTS.md`

## One-Time Environment Setup (Human)
These steps prepare the local Python environment so Codex Skills can run successfully.

From repo root (`chadwin-codex`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If you will use US filing fetch workflows (`$research` on US tickers or `$fetch-us-company-data`), set EDGAR identity in `.env`:

```bash
EDGAR_IDENTITY="Your Name (your.email@example.com)"
```

This is setup/bootstrap only. Day-to-day usage should still be done by asking Codex to run Skills.

## How To Use It As A Human
Use one of these Skill-level requests in Codex:

- Default entrypoint: `$research`
- Advanced manual control: `$fetch-us-investment-ideas`
- Advanced manual control: `$fetch-us-company-data`
- Advanced manual control: `$run-llm-workflow`
- Preferences setup/update: `$manage-user-preferences`
- For non-US markets, use the installed market-specific fetch skill when available.

`$run-llm-workflow` now includes progressive falsification/deep-research behavior: it should keep investigating the highest-impact unresolved issues and stop only when key investment points are resolved to decision quality.

Most skills now read `preferences/user_preferences.json` by default (market guardrails plus sector/industry and report-style preferences where applicable).

Example requests you can give Codex:
- `Run $research for AAPL as-of 2026-02-11.`
- `Run $fetch-us-investment-ideas, then use $research with no ticker.`
- `Run $run-llm-workflow for HRMY as-of 2026-02-12 and focus on falsifying the key unresolved issues from the latest same-date baseline report package.`
- `Run $manage-user-preferences and ask me questions to build my profile.`

## Required Outputs Per Completed Run
For `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`, a run is complete only when these exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

`<REPORT_DATE_DIR>` naming convention:
- First run for an as-of date: `YYYY-MM-DD`
- Additional runs for the same as-of date: `YYYY-MM-DD-01`, then `YYYY-MM-DD-02`, etc.
- Exception: if `reports/YYYY-MM-DD/valuation/inputs.yaml` exists but `report.md` or `valuation/outputs.json` is missing, continue that incomplete package instead of creating a suffixed directory.

## What The Agent Uses Internally
Skills are the authoritative workflow definitions and use scripts as bounded helpers.
Any shell command execution is agent-facing and should happen inside a Skill workflow.

Primary Skill docs:
- `chadwin-codex/.agents/skills/research/SKILL.md`
- `chadwin-codex/.agents/skills/fetch-us-investment-ideas/SKILL.md`
- `chadwin-codex/.agents/skills/fetch-us-company-data/SKILL.md`
- `chadwin-codex/.agents/skills/run-llm-workflow/SKILL.md`
- `chadwin-codex/.agents/skills/manage-user-preferences/SKILL.md`

## Repository Layout
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/`: exchange-country roots for company packages
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/`: local evidence inputs
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`: report and valuation outputs
- `idea-screens/`: idea queue and generated idea files
- `preferences/user_preferences.json`: persistent user preference profile
- `improvement-log.md`: repo-level process improvement log
- `.agents/skills/`: Skill definitions, scripts, references, and assets
