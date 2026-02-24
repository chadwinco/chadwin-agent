# Chadwin Agent

Chadwin Agent is a stock market research app designed to be run in Codex and Claude Code.

## 1. Get the agent setup
Clone the repo, open in Codex or Claude Code, and prompt it to get things setup:

```text
Let's get started
```

During setup, the agent will ask for your name and email address in order to call the SEC EDGAR API, which requires the name and email address of the person making the requests. This information is kept on your machine and only used for these API calls.

## 2. Run research
Research is done with the `Chadwin Research` skill. It's extremely flexible and designed to handle simple requests like:

```text
Do deep research on ASML including fair value estimates.
```

Or more complex requests like this:

```text
Screen for consumer cyclical companies with high ROIC. Run deep research on the top three most promising ideas from the screen.
```

The `Chadwin Research` skill makes use of helper skills to carry out specific parts of the research:

- `fetch-us-investment-ideas`: Generates lists of US stock ideas based on flexible criteria.
- `fetch-us-company-data`: Retrieves SEC filings, analyst forecasts, and general company information.

These skills can be accessed directly, but it's usually more powerful to use the `Chadwin Research` skill, which will invoke these skills when needed.

## 3. Personalize the agent
You can set preferences, whether it's certain industries to be excluded from screeners, preferences on what topics the reports cover, and more.

Simply use the `chadwin-preferences` skill with a message about your preferences. The agent will remember these preferences for all future research.

## 4. Keeping things up-to-date
In general, the agent will keep itself up-to-date by fetching the latest version from GitHub at the start of a session. You can also force this by making a request like:

```text
Update the app
```
