# Business and Competitive Position Prompt

Goal: Explain how the company makes money, why returns may persist, and what could weaken the model.

Inputs:
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/filings/10-K-*.md` or `20-F-*.md`
- Latest `10-Q-*.md` and earnings call transcript, if available
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/company_profile.csv`
- `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_ratings_actions_12m.csv` (optional expectation-shift context)

Instructions:
- Write 2-3 short, tightly argued paragraphs.
- Describe revenue drivers (products, customers, geographies, segments).
- Identify structural advantages and explicit weak points.
- Highlight one area where market expectations look ahead/behind fundamentals if evidence supports it.
- End with one sentence linking business evidence to valuation durability (or fragility).
- Avoid generic moat language; tie every claim to concrete evidence.
- Cite local file paths for factual claims.
