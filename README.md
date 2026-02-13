# Chadwin Codex Research

This repository is a Codex-operated equity research system. It is intended to be used inside OpenAI Codex by requesting outcomes in natural language using the included skills.

Agent operating rules and workflow contract are in `AGENTS.md`

## One-Time Setup
These steps prepare the local Python environment so Codex Skills can run successfully.

From repo root:

If `python3 -m venv .venv` fails with `No module named venv`, install Python's `venv` support first:

```bash
# macOS (Homebrew; `venv` is included with Python)
brew install python

# Debian/Ubuntu (`venv` is a separate package)
sudo apt update && sudo apt install -y python3-venv

# Fedora/RHEL/CentOS (`venv` is included with python3)
sudo dnf install -y python3

# Arch Linux (`venv` is included with python)
sudo pacman -S python
```

Then create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If macOS still uses the wrong interpreter after `brew install python`, run Homebrew Python explicitly:
- Apple Silicon: `/opt/homebrew/bin/python3 -m venv .venv`
- Intel: `/usr/local/bin/python3 -m venv .venv`

You should also configure your identity in `.env` to comply with the rules of the SEC EDGAR API, which is used to fetch financial information:

```bash
EDGAR_IDENTITY="Your Name (your.email@example.com)"
```

## How To Use Chadwin Codex

The `$chadwin-research` skill is the default entry point. This can accept flexible input that will handle generating investment ideas, fetching required data, and running a flexible LLM research workflow.

The core LLM research skill uses a progressive falsification/deep-research behavior: it should keep investigating the highest-impact unresolved issues and stop only when key investment points are resolved to decision quality.

For example:
- `$chadwin-research Find 10 potentially undervalued small-cap consumer defensive companies. Run research on all ten, giving a summary of the full results at the end`

More fine-grained control is available by using specific skills that are part of the overall `$chadwin-research skill`. 

For example:
- `Run $run-llm-workflow for HRMY as-of 2026-02-12 and focus on falsifying the key unresolved issues from the latest report`

- Additional skills: 
  - `$fetch-us-investment-ideas`: Generates a list of companies to research and writes them to the `idea-screens` directory
  - `$fetch-us-company-data`: Fetches comprehensive company information from the SEC and reputable third-party websites and writes it to a company folder in `companies`
  - `$run-llm-workflow`: Runs the LLM-driven workflow, which results in a valuation and written report inside the company folder in `companies`
  - `$manage-user-preferences`: Helper skill to update user preferences. These can also be manually updates at `user_preferences.json`

- Support for non-US markets will be available soon.

## Required Outputs Per Completed Run
For `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`, a run is complete only when these exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

## What The Agent Uses Internally
Skills are the authoritative workflow definitions and use scripts as bounded helpers.
Any shell command execution is agent-facing and should happen inside a Skill workflow.

Primary Skill docs:
- `.agents/skills/chadwin-research/SKILL.md`
- `.agents/skills/fetch-us-investment-ideas/SKILL.md`
- `.agents/skills/fetch-us-company-data/SKILL.md`
- `.agents/skills/run-llm-workflow/SKILL.md`
- `.agents/skills/manage-user-preferences/SKILL.md`

## Repository Layout
- `idea-screens/`: idea queue and generated idea files
- `user_preferences.json`: persistent user preference profile
- `improvement-log.md`: repo-level process improvement log
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/`: country-code roots for company packages (`<EXCHANGE_COUNTRY>` must be uppercase ISO 3166-1 alpha-2, for example `US`, `JP`, `GB`)
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/`: local evidence inputs
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`: report and valuation outputs
