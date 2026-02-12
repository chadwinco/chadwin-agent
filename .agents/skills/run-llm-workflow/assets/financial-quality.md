# Financial Quality Prompt

Goal: Quantify financial quality and cash generation durability.

Inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/financial_statements/annual/*.csv`.
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/data/analyst_revenue_estimates.csv` and `analyst_eps_estimates.csv` when available.
- Use the data dictionary from the fetch skill that generated the local company data (for example, `.agents/skills/fetch-us-company-data/references/data-dictionary.md`) for metric definitions.

Instructions:
- Quantify revenue trend (CAGR plus latest year-over-year).
- Quantify EBIT margin and FCF margin trends.
- Estimate ROIC proxy and comment on drivers.
- Evaluate leverage (net debt and net debt/EBITDA).
- Compare historical trend direction versus analyst forward expectations; flag the largest mismatch.
- Flag one metric that would most likely signal thesis deterioration.
- Cite local file paths for factual claims.
