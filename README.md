# Chadwin Codex Research

Chadwin Codex is an LLM-operated equity research app. It allows you to run rigorous stock research using natural language.

The app uses a bundled setup skill plus external core skills:

- `chadwin-setup`: setup control plane bundled in this repo at `.agents/skills/chadwin-setup` (installs/updates core external skills, bootstraps app `.venv`, and validates shared data primitives)
- `chadwin-research`: deep research skill for producing fundamental equity research
- `fetch-us-investment-ideas`: generates lists of US stock ideas based on flexible criteria
- `fetch-us-company-data`: retrieves targeted SEC/EDGAR company data as part of the research process
- `chadwin-preferences`: captures your market, strategy, and report-format preferences into a single reusable profile

## How to Use

### 1. Open in Codex
Open this repository in Codex desktop and work from the repo root.

### 2. Ask the LLM to set things up
In chat, use a simple request like:

```text
Let's get started.
```

The agent should:
- run `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"` from this repo root
- handle all setup actions from chat prompts; the human is not expected to run shell commands directly

If SEC/EDGAR data is needed and `EDGAR_IDENTITY` is not present in repo `.env`, the agent should ask for your name/email and add it.

```bash
EDGAR_IDENTITY="Full Name <email@example.com>"
```

### 3. Run research with the `Chadwin Research` skill

Example request:

```text
$chadwin-research Screen for consumer cyclical companies with high ROE. Run research on the top three most promising ideas from the screen
```

Detailed operator rules and setup command reference live in `AGENTS.md`.
