# Chadwin Codex Research

This repository is a skill-first, Codex-operated equity research system.

Deterministic code lives inside skills (`.agents/skills/*`) and is used as bounded helpers. The LLM agent remains responsible for workflow control, sanity checks, and final output quality.

Agent operating contract and workflow rules are defined in `AGENTS.md`.
Shared data primitives and extension rules are defined in `DATA_CONTRACT.md`.

## One-Time Setup
Setup should begin with the `chadwin-setup` skill:

```bash
sed -n '1,260p' .agents/skills/chadwin-setup/SKILL.md
```

This skill is the canonical setup entrypoint and includes:
- Python `.venv` creation and troubleshooting
- per-skill dependency installation guidance
- `.env` + `EDGAR_IDENTITY` setup
- `<DATA_ROOT>` bootstrap behavior and commands

If you only need the data-root bootstrap command directly:

```bash
.venv/bin/python .agents/skills/chadwin-setup/scripts/setup_chadwin_data_dirs.py
```

Validate shared data-contract compliance:

```bash
.venv/bin/python .agents/skills/chadwin-setup/scripts/validate_data_contract.py
```

## Discover and Use Skills
List available repo-local skills:

```bash
find .agents/skills -mindepth 1 -maxdepth 1 -type d | sort
```

For each skill you intend to run, read its workflow first:

```bash
sed -n '1,220p' .agents/skills/<skill-name>/SKILL.md
```

If an orchestrator skill is installed, use it for semi-autonomous runs. If not, compose manual runs from available lower-level skills (idea generation, data fetch, research/reporting, preferences).

## Required Outputs Per Completed Research Run
For `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/`, a run is complete only when these files exist:
- `report.md`
- `valuation/inputs.yaml`
- `valuation/outputs.json`

## Repository Layout
- `.agents/skills/`: skill definitions, scripts, references, and assets
- `<DATA_ROOT>/idea-screens/<SCREEN_RUN_ID>/screener-results.jsonl`: per-screen idea queue primitives
- `<DATA_ROOT>/user_preferences.json`: persistent preference profile
- `<DATA_ROOT>/improvement-log.md`: process improvement log
- `<DATA_ROOT>/companies/`: company package root
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/`: company evidence and reports
