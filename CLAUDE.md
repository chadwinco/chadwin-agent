# Chadwin Agent

This repository is an LLM-operated equity research system. In Claude sessions, the agent is the active operator and must execute setup and workflow commands directly when needed.

Startup behavior:
- If asked to begin setup, run `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"`.
- Use natural-language chat as the primary interface; do not require users to run shell commands directly.
- If SEC data is needed and `EDGAR_IDENTITY` is missing from repo `.env`, ask for `Full Name <email@example.com>` and write it as `EDGAR_IDENTITY`.

Skill locations:
- Bundled source-of-truth skills: `.agents/skills/`
- Claude project mirrors: `.claude/skills/`
- External installed skills: `~/.claude/skills` (and optionally `~/.codex/skills` for dual-runtime workflows)

Shared contract:
- Follow `AGENTS.md` for `<DATA_ROOT>` conventions, shared path primitives, and validation requirements.
- Run `.venv/bin/python ".agents/skills/chadwin-setup/scripts/validate_data_contract.py"` after setup and contract-affecting changes.
