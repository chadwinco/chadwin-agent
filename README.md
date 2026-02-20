# Chadwin Codex Research

Chadwin Codex is an LLM-operated equity research app. It allows you to run rigorous stock research using natural language.

## How to Use

### 1. Ask the LLM to set things up
Open this repository in Codex desktop and in the chat, use a simple request like:

```text
Let's get started.
```

The agent should handle all setup actions from chat prompts; users are not expected to run shell commands directly.

If SEC/EDGAR data is needed and `EDGAR_IDENTITY` is not present in repo `.env`, the agent should ask for your SEC identity in the form `Full Name <email@example.com>` and add it.

```bash
EDGAR_IDENTITY="Full Name <email@example.com>"
```

### 2. Run research with the `Chadwin Research` skill

Example request:

```text
$chadwin-research Screen for consumer cyclical companies with high ROE. Run research on the top three most promising ideas from the screen.
```

The app uses a few core skills to run screeners and carry out deep research on individual companies:

- `chadwin-research`: Deep research skill for producing fundamental equity research. This is the default entry point for fetching new ideas and generating research.
- `fetch-us-investment-ideas`: Generates lists of US stock ideas based on flexible criteria. It can be invoked via the `$chadwin-research` skill, in order to fetch new ideas and carry out research on them in one request.
- `fetch-us-company-data`: Retrieves targeted SEC/EDGAR company data as part of the research process. This is heavily used by the `$chadwin-research` skill to fetch and store data needed for company research.
- `chadwin-preferences`: Bundled in this repo at `.agents/skills/chadwin-preferences`. Captures your market, strategy, and report-format preferences. Skills will respect these preferences, but they can also be overridden in chat.
- `chadwin-setup`: Bundled in this repo at `.agents/skills/chadwin-setup`. Installs/updates core external skills, bootstraps app `.venv`, and validates shared data primitives.

Detailed operator rules and setup command reference live in `AGENTS.md`.
