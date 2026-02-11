# Chadwin Codex Research Repo

This repository is a Codex-operated equity research system.

## Intended Usage (Codex Only)
Use this repo inside Codex, by asking the agent to run Skills.

- Humans should request outcomes in natural language or by naming a Skill.
- The agent executes scripts and shell commands as part of Skill workflows.
- Humans are not expected to run raw bash commands to operate the repo.

Agent operating rules and workflow contract are in:
- `/Users/chad/source/chadwin-codex/AGENTS.md`

## One-Time Environment Setup (Human)
These steps prepare the local Python environment so Codex Skills can run successfully.

From repo root (`/Users/chad/source/chadwin-codex`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If you will use US filing fetch workflows (`$research` on US tickers or `$fetch-us-company-data`), set EDGAR identity in `.env`:

```bash
EDGAR_IDENTITY="Your Name your.email@example.com"
```

This is setup/bootstrap only. Day-to-day usage should still be done by asking Codex to run Skills.

## How To Use It As A Human
Use one of these Skill-level requests in Codex:

- Default entrypoint: `$research`
- Advanced manual control: `$fetch-us-investment-ideas`
- Advanced manual control: `$fetch-us-company-data`
- Advanced manual control: `$fetch-japanese-company-data`
- Advanced manual control: `$run-llm-workflow`

Example requests you can give Codex:
- `Run $research for AAPL as-of 2026-02-11.`
- `Run $fetch-us-investment-ideas, then use $research with no ticker.`
- `Run $fetch-japanese-company-data for 79740 as-of 2026-02-11, then run $run-llm-workflow.`

## Required Outputs Per Completed Run
For `companies/<TICKER>/reports/<YYYY-MM-DD>/`, a run is complete only when these exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

## What The Agent Uses Internally
Skills are the authoritative workflow definitions and use scripts as bounded helpers.
Any shell command execution is agent-facing and should happen inside a Skill workflow.

Primary Skill docs:
- `/Users/chad/source/chadwin-codex/.agents/skills/research/SKILL.md`
- `/Users/chad/source/chadwin-codex/.agents/skills/fetch-us-investment-ideas/SKILL.md`
- `/Users/chad/source/chadwin-codex/.agents/skills/fetch-us-company-data/SKILL.md`
- `/Users/chad/source/chadwin-codex/.agents/skills/fetch-japanese-company-data/SKILL.md`
- `/Users/chad/source/chadwin-codex/.agents/skills/run-llm-workflow/SKILL.md`

## Repository Layout
- `companies/<TICKER>/data/`: local evidence inputs
- `companies/<TICKER>/reports/<YYYY-MM-DD>/`: report and valuation outputs
- `idea-screens/`: idea queue and generated idea files
- `docs/`: supporting docs and improvement log
- `.agents/skills/`: Skill definitions, scripts, references, and assets

## References
- `/Users/chad/source/chadwin-codex/docs/python-setup.md`
- `/Users/chad/source/chadwin-codex/docs/improvement-log.md`
