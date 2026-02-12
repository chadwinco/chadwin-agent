# Valuation Prompt

Goal: Explain scenario DCF outputs and the implied margin of safety.

Inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/inputs.yaml`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/valuation/outputs.json`
- Analyst anchor files when available:
  - `analyst_revenue_estimates.csv`
  - `analyst_eps_estimates.csv`
  - `analyst_eps_forward_pe_estimates.csv`
  - `analyst_price_targets.csv`

Instructions:
- Present base, bull, and bear assumptions clearly.
- Start with a short paragraph that explains how the top valuation pillars translated into scenario inputs.
- Use the three-stage structure (competitive-advantage period, fade period, terminal period).
- Reconcile each scenario value/share against current price.
- State margin of safety for each scenario.
- Explain what has to go right for bull case and what drives bear case.
- Explain why `stage1_years` and terminal assumptions are appropriate for the company.
- Explicitly state where base assumptions align/diverge from analyst expectations and why.
- Avoid writing this section as a pure number list; explain the causal chain from evidence to model output.
- If results look extreme, sanity-check units, net debt sign, and share count.
- Cite local file paths for factual claims.
