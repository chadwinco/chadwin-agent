# Valuation Prompt

Goal: Explain scenario DCF outputs and the implied margin of safety.

Inputs:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

Instructions:
- Present base, bull, and bear assumptions clearly.
- Use the three-stage structure (competitive-advantage period, fade period, terminal period).
- Reconcile each scenario value/share against current price.
- State margin of safety for each scenario.
- Explain what has to go right for bull case and what drives bear case.
- Explain why `stage1_years` and terminal assumptions are appropriate for the company.
- If results look extreme, sanity-check units, net debt sign, and share count.
- Cite local file paths for factual claims.
