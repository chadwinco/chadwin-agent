# Financial Quality Prompt

Goal: Quantify financial quality and cash generation durability.

Inputs:
- `companies/<TICKER>/data/financial_statements/annual/*.csv`.
- `docs/data-dictionary.md` for metric definitions.

Instructions:
- Quantify revenue trend (CAGR plus latest year-over-year).
- Quantify EBIT margin and FCF margin trends.
- Estimate ROIC proxy and comment on drivers.
- Evaluate leverage (net debt and net debt/EBITDA).
- Flag one metric that would most likely signal thesis deterioration.
- Cite local file paths for factual claims.
