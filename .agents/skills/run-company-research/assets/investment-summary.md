# Investment Summary Prompt

Goal: Produce a concise, decision-oriented summary for the current price.

Inputs:
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`
- Local filing and transcript evidence from `companies/<TICKER>/data/filings/*.md`
- Current price from `companies/<TICKER>/data/company_profile.csv`

Instructions:
- Lead with a clear verdict: `Attractive`, `Watch`, or `Avoid`.
- Include base value/share, bull/bear range, current price, and base margin of safety.
- Add 2-4 bullets on the core thesis and the biggest uncertainty.
- Keep this section under 140 words.
- Cite local file paths for factual claims.
