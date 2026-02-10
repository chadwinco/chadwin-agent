# Business and Competitive Position Prompt

Goal: Explain how the company makes money, why returns may persist, and what could weaken the model.

Inputs:
- `companies/<TICKER>/data/filings/10-K-*.md` or `20-F-*.md`
- Latest `10-Q-*.md` and earnings call transcript, if available
- `companies/<TICKER>/data/company_profile.csv`

Instructions:
- Write 1-2 short paragraphs.
- Describe revenue drivers (products, customers, geographies, segments).
- Identify structural advantages and explicit weak points.
- Avoid generic moat language; tie every claim to concrete evidence.
- Cite local file paths for factual claims.
