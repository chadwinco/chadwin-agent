# Valuation Prompt

Goal: Explain scenario DCF outputs and the implied margin of safety.

Inputs:
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/inputs.yaml`
- `companies/<TICKER>/reports/<YYYY-MM-DD>/valuation/outputs.json`

Instructions:
- Present base, bull, and bear assumptions clearly.
- Reconcile each scenario value/share against current price.
- State margin of safety for each scenario.
- Explain what has to go right for bull case and what drives bear case.
- If results look extreme, sanity-check units, net debt sign, and share count.
- Cite local file paths for factual claims.
