# Valuation Method (Scenario DCF)

Use a consistent five-year, two-stage DCF for base/bull/bear scenarios.

## Inputs Required
From local files:
- `revenue_0`: latest annual revenue
- `net_debt`: latest net debt (`totalDebt - cashAndCashEquivalents`, or `netDebt` if present)
- `diluted_shares`: latest `weightedAverageShsOutDil` (fallback `weightedAverageShsOut`)
- `current_price`: `company_profile.csv` `price`
- scenario assumptions:
  - `revenue_growth`
  - `fcf_margin`
  - `discount_rate`
  - `terminal_growth`

## Formulas
For `t = 1..N` where `N = 5`:
- `revenue_t = revenue_0 * (1 + g)^t`
- `fcf_t = revenue_t * fcf_margin`
- `pv_fcf_t = fcf_t / (1 + r)^t`

Terminal value:
- `terminal_fcf = fcf_N * (1 + tg)`
- `terminal_value = terminal_fcf / (r - tg)`
- `pv_terminal = terminal_value / (1 + r)^N`

Scenario outputs:
- `enterprise_value = sum(pv_fcf_t) + pv_terminal`
- `equity_value = enterprise_value - net_debt`
- `value_per_share = equity_value / diluted_shares`
- `margin_of_safety = (value_per_share / current_price) - 1`

## Guardrails
- `discount_rate` must be greater than `terminal_growth`.
- Use one unit system across all inputs (do not mix dollars and millions).
- If `net_debt` is negative, treat it as net cash (subtracting a negative increases equity value).

## Write `valuation/inputs.yaml`
Include all assumptions used:

```yaml
asof_date: YYYY-MM-DD
currency: USD
price: 123.45
forecast_years: 5
base_year:
  revenue: 0
  net_debt: 0
  diluted_shares: 0
scenarios:
  base:
    revenue_growth: 0.04
    fcf_margin: 0.12
    discount_rate: 0.10
    terminal_growth: 0.02
  bull:
    revenue_growth: 0.06
    fcf_margin: 0.14
    discount_rate: 0.09
    terminal_growth: 0.025
  bear:
    revenue_growth: 0.01
    fcf_margin: 0.09
    discount_rate: 0.11
    terminal_growth: 0.015
```

## Write `valuation/outputs.json`
Minimum schema:

```json
{
  "ticker": "TICKER",
  "asof_date": "YYYY-MM-DD",
  "currency": "USD",
  "price": 123.45,
  "method": "two-stage-dcf",
  "forecast_years": 5,
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
