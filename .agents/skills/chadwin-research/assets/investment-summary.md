# Investment Summary Prompt

Goal: Produce a concise, decision-oriented summary for the current price.

Inputs:
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/outputs.json`
- Local filing and transcript evidence from `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/*.md`
- Current price from `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- Analyst consensus/target context from `analyst_consensus.csv` and `analyst_price_targets.csv` when available

Instructions:
- Lead with a clear verdict: `Attractive`, `Watch`, or `Avoid`.
- Include base value/share, bull/bear range, current price, and base margin of safety.
- Write one compact paragraph (roughly 120-180 words), not bullet fragments.
- In that paragraph, cover core thesis, biggest resolved issue, biggest remaining uncertainty, and why the current MOS is decision-relevant.
- Cite factual claims with ticker-root local paths (for example, `AMZN/data/...`).
