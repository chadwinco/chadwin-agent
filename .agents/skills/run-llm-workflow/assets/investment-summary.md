# Investment Summary Prompt

Goal: Produce a concise, decision-oriented summary for the current price.

Inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/outputs.json`
- Local filing and transcript evidence from `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`
- Current price from `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- Analyst consensus/target context from `analyst_consensus.csv` and `analyst_price_targets.csv` when available

Instructions:
- Lead with a clear verdict: `Attractive`, `Watch`, or `Avoid`.
- Include base value/share, bull/bear range, current price, and base margin of safety.
- Add 2-4 bullets on the core thesis, biggest resolved issue, and biggest remaining uncertainty.
- Keep this section under 140 words.
- Cite local file paths for factual claims.
