# Valuation Method (Scenario DCF with Competitive-Advantage Fade)

Use a three-stage DCF for base/bull/bear scenarios so durable businesses are not forced into a "five years then inflation" shape.

## Model Structure
1. Stage 1 (competitive-advantage period): explicit growth and FCF margin for `stage1_years`.
2. Stage 2 (fade): linearly converge growth and margin to terminal levels over `fade_years`.
3. Terminal stage: steady-state perpetuity.

## Inputs Required
From local files:
- `revenue_0`: latest reliable annual revenue (if a more recent annual figure is only in a filing, cite it explicitly in `notes`)
- `net_debt`: latest net debt (`totalDebt - cashAndCashEquivalents`, or `netDebt` if present)
- `diluted_shares`: latest `weightedAverageShsOutDil` (fallback `weightedAverageShsOut`)
- `current_price`: `company_profile.csv` `price`

Per scenario:
- `revenue_growth_stage1`
- `fcf_margin_stage1`
- `discount_rate`
- `terminal_growth`
- `fcf_margin_terminal`
- `stage1_years`
- `fade_years`

## Formulas
For Stage 1 (`t = 1..stage1_years`):
- `revenue_t = revenue_(t-1) * (1 + g_stage1)`
- `fcf_t = revenue_t * margin_stage1`
- `pv_fcf_t = fcf_t / (1 + r)^t`

For Fade stage (`j = 1..fade_years`):
- `g_j = g_stage1 + (terminal_growth - g_stage1) * j / (fade_years + 1)`
- `m_j = margin_stage1 + (margin_terminal - margin_stage1) * j / (fade_years + 1)`
- `revenue_(t+j) = revenue_(t+j-1) * (1 + g_j)`
- `fcf_(t+j) = revenue_(t+j) * m_j`
- `pv_fcf_(t+j) = fcf_(t+j) / (1 + r)^(t+j)`

Terminal value at end of fade:
- `terminal_fcf = fcf_last * (1 + terminal_growth)`
- `terminal_value = terminal_fcf / (r - terminal_growth)`
- `pv_terminal = terminal_value / (1 + r)^last_year`

Scenario outputs:
- `enterprise_value = sum(pv_fcf) + pv_terminal`
- `equity_value = enterprise_value - net_debt`
- `value_per_share = equity_value / diluted_shares`
- `margin_of_safety = (value_per_share / current_price) - 1`

## Guardrails
- `discount_rate` must be greater than `terminal_growth`.
- Use one unit system across all inputs (do not mix dollars and millions).
- If `net_debt` is negative, treat it as net cash (subtracting a negative increases equity value).
- Do not default `stage1_years` to 5 for durable businesses; typically use 8-15 years when evidence supports persistence.
- `terminal_growth` should represent stable long-run growth and be explicitly justified (not auto-set to inflation).

## Write `valuation/inputs.yaml`
Include all assumptions used:

```yaml
asof_date: YYYY-MM-DD
currency: USD
price: 123.45
model:
  type: three-stage-dcf-fade
base_year:
  year: YYYY-MM-DD
  revenue: 0
  net_debt: 0
  diluted_shares: 0
scenarios:
  base:
    revenue_growth_stage1: 0.10
    fcf_margin_stage1: 0.20
    discount_rate: 0.09
    terminal_growth: 0.03
    fcf_margin_terminal: 0.16
    stage1_years: 10
    fade_years: 5
  bull:
    revenue_growth_stage1: 0.13
    fcf_margin_stage1: 0.24
    discount_rate: 0.08
    terminal_growth: 0.035
    fcf_margin_terminal: 0.19
    stage1_years: 12
    fade_years: 5
  bear:
    revenue_growth_stage1: 0.06
    fcf_margin_stage1: 0.14
    discount_rate: 0.10
    terminal_growth: 0.02
    fcf_margin_terminal: 0.12
    stage1_years: 8
    fade_years: 5
```

## Write `valuation/outputs.json`
Minimum schema:

```json
{
  "ticker": "TICKER",
  "asof_date": "YYYY-MM-DD",
  "currency": "USD",
  "price": 123.45,
  "method": "three-stage-dcf-fade",
  "scenarios": {
    "base": {
      "enterprise_value": 0,
      "equity_value": 0,
      "value_per_share": 0,
      "margin_of_safety": 0
    },
    "bull": {},
    "bear": {}
  }
}
```

## Sanity Checks
- Base value should usually be between bull and bear.
- If results look nonsensical, verify:
  - units
  - net debt sign
  - share count denominator
  - stage-1 duration versus competitive evidence
  - implied terminal economics (growth and margin) versus business maturity
