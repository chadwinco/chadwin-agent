# Chadwin Codex Research

Chadwin Codex is a practical, LLM-operated equity research app.  
The goal is simple: open the repo in Codex, ask for research, and get structured outputs that are consistent and reusable.

What this app gives you:
- a stable control plane for installing and updating research skills
- a shared data contract so reports and valuation artifacts land in predictable paths
- an LLM-first workflow where the agent owns end-to-end execution quality

Detailed operator rules and setup command reference live in `AGENTS.md`.

## How to Use

### 1. Open in Codex
Open this repository in Codex desktop and work from the repo root.

### 2. Ask the LLM to set things up
In chat, use a simple request like:

```text
Let's get started.
```

The agent should run the setup workflow (`scripts/chadwin_setup.py`) and ensure skills + shared data primitives are ready before research work starts.

### 3. Run research with the `Chadwin Research` skill

Example request:

```text
$chadwin-research Screen for consumer cyclical companies with high ROE. Run research on the top three most promising ideas from the screen
```

## Default Skills (User Experience)

- `chadwin-setup`: makes initial setup reliable by creating required shared data primitives and validating the shared contract.
- `chadwin-research`: produces a concise investment report plus scenario valuation artifacts in canonical report folders.
- `fetch-us-investment-ideas`: generates lists of US stock ideas based on flexible criteria
- `fetch-us-company-data`: retrieves targeted SEC/EDGAR company data as part of the research process
- `chadwin-preferences`: captures your market, strategy, and report-format preferences into a single reusable profile.
