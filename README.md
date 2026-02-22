# Chadwin Agent

Chadwin Agent is an LLM-operated equity research app for Codex and Claude Code. It allows rigorous stock research through natural language prompts.

## How to Use

### 1. Ask the LLM to set things up
Open this repository in Codex desktop or Claude Code and use a simple request like:

```text
Let's get started.
```

The agent should handle setup actions from chat prompts; users are not expected to run shell commands directly.

If SEC/EDGAR data is needed and `EDGAR_IDENTITY` is not present in repo `.env`, the agent should ask for your SEC identity in the form `Full Name <email@example.com>` and add it.

```bash
EDGAR_IDENTITY="Full Name <email@example.com>"
```

### Keeping the app and skills up to date

Setup keeps both the app workspace and skills current automatically whenever setup runs.

Automatic behavior:
- App repo self-update:
  - If the workspace is a git clone of `chadwin-agent`, setup fetches and fast-forwards the default branch when safe.
  - If the workspace was downloaded as an archive (no `.git`), setup initializes git metadata, connects to the official GitHub remote, and aligns to the default branch.
- Core external skills update: setup syncs required core skills to the refs in `.agents/skills/chadwin-setup/assets/skills.lock.json` (default floating `main`).
- Bundled skill mirror sync: setup syncs `.agents/skills/*` into `.claude/skills/*`.

Manual invocation:

```bash
python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py"
```

Useful manual options:
- Check drift only (no mutation): `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --check`
- Plan only (dry run): `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --dry-run`
- Skip app self-update if needed: `python3 ".agents/skills/chadwin-setup/scripts/chadwin_setup.py" --skip-self-update`

### 2. Run research with the `Chadwin Research` skill

Example requests:

```text
$chadwin-research Screen for consumer cyclical companies with high ROE. Run research on the top three most promising ideas from the screen.
```

```text
Invoke the chadwin-research skill to screen consumer cyclical companies with high ROE, then run deep research on the top three ideas.
```

The app uses a few core skills to run screeners and carry out deep research on individual companies:

- `chadwin-research`: Deep research skill for producing fundamental equity research. This is the default entry point for fetching new ideas and generating research.
- `fetch-us-investment-ideas`: Generates lists of US stock ideas based on flexible criteria. It can be invoked from `chadwin-research` in one request.
- `fetch-us-company-data`: Retrieves targeted SEC/EDGAR company data for research workflows.
- `chadwin-preferences`: Bundled in this repo at `.agents/skills/chadwin-preferences` and mirrored at `.claude/skills/chadwin-preferences`.
- `chadwin-setup`: Bundled in this repo at `.agents/skills/chadwin-setup` and mirrored at `.claude/skills/chadwin-setup`.

Detailed operator rules and setup command reference live in `AGENTS.md`.
