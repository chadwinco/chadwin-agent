# Valuation Method (Scenario-Based, Business-Model Aware)

Use one of two methods depending on business economics:

1. `three-stage-dcf-fade`
   - Use for non-financial companies where free cash flow is decision-useful.
2. `two-stage-residual-income`
   - Use for insurers, banks, and other financials where book value, ROE, and capital constraints are more informative than FCF.

## Model Selection Rules
- Prefer `three-stage-dcf-fade` when revenue and FCF margins are stable enough to forecast.
- Prefer `two-stage-residual-income` when:
  - balance-sheet leverage is structural to the business model;
  - statutory/regulatory capital constraints drive value; and
  - reported operating cash flow is noisy as a valuation anchor.

## Analyst Anchor Rules (Required When Files Exist)
Use local analyst files to anchor what the market currently expects:
- `analyst_revenue_estimates.csv`
- `analyst_eps_estimates.csv`
- `analyst_eps_forward_pe_estimates.csv`
- `analyst_price_targets.csv`
- `analyst_consensus.csv`
- `analyst_ratings_actions_12m.csv`

How to use them:
- Anchor near-term growth/profitability ranges to analyst central tendency and dispersion.
- Use ratings/target actions to detect expectation momentum shifts.
- Use forward P/E and target range as a valuation-sentiment cross-check against your scenario outputs.
- If your base case differs materially from consensus, keep it only with explicit evidence and written rationale in the report/inputs notes.

---

## Model A: Three-Stage DCF with Competitive-Advantage Fade

### Model Structure
1. Stage 1 (competitive-advantage period): explicit growth and FCF margin for `stage1_years`.
2. Stage 2 (fade): linearly converge growth and margin to terminal levels over `fade_years`.
3. Terminal stage: steady-state perpetuity.

### Inputs Required
From local files:
- `revenue_0`: latest reliable annual revenue
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

### Formulas
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

### Guardrails
- `discount_rate` must be greater than `terminal_growth`.
- Use one unit system across all inputs (do not mix dollars and millions).
- If `net_debt` is negative, treat it as net cash (subtracting a negative increases equity value).
- Do not default `stage1_years` to 5 for durable businesses; typically use 8-15 years when evidence supports persistence.

---

## Model B: Two-Stage Residual Income (Financials / Insurers)

Residual income values equity directly from current book value plus discounted future excess returns.

### Inputs Required
From local files:
- `common_equity_0`: latest common equity (or stockholders' equity if common-equity split is unavailable)
- `shares_outstanding`: current diluted/common share count proxy used for per-share conversion
- `current_price`: `company_profile.csv` `price`

Per scenario:
- `roe_stage1`
- `payout_ratio`
- `cost_of_equity`
- `terminal_roe`
- `terminal_growth`
- `stage1_years`

### Formulas
At `t = 1..stage1_years`:
- `net_income_t = roe_stage1 * book_value_(t-1)`
- `dividends_t = payout_ratio * net_income_t`
- `book_value_t = book_value_(t-1) + net_income_t - dividends_t`
- `residual_income_t = (roe_stage1 - cost_of_equity) * book_value_(t-1)`
- `pv_residual_income_t = residual_income_t / (1 + cost_of_equity)^t`

Terminal residual income:
- `residual_income_(n+1) = (terminal_roe - cost_of_equity) * book_value_n`
- `continuing_value_n = residual_income_(n+1) / (cost_of_equity - terminal_growth)`
- `pv_continuing_value = continuing_value_n / (1 + cost_of_equity)^n`

Scenario outputs:
- `equity_value = common_equity_0 + sum(pv_residual_income) + pv_continuing_value`
- `value_per_share = equity_value / shares_outstanding`
- `margin_of_safety = (value_per_share / current_price) - 1`

### Guardrails
- `cost_of_equity` must be greater than `terminal_growth`.
- `payout_ratio` should be in `[0, 1]`.
- Keep `roe_stage1`, `terminal_roe`, and `cost_of_equity` in decimal form (for example `0.10` for 10%).
- Use a share-count denominator consistent with the price source date.
- Enterprise value is not the primary decision metric for this model.

---

## Write `valuation/inputs.yaml`

For DCF:

```yaml
asof_date: YYYY-MM-DD
currency: USD
price: 123.45
model:
  type: three-stage-dcf-fade
base_year:
  period_end: YYYY-MM-DD
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
```

For residual income:

```yaml
asof_date: YYYY-MM-DD
currency: USD
price: 123.45
model:
  type: two-stage-residual-income
base_year:
  period_end: YYYY-MM-DD
  common_equity: 0
  shares_outstanding: 0
scenarios:
  base:
    roe_stage1: 0.10
    payout_ratio: 0.30
    cost_of_equity: 0.115
    terminal_roe: 0.095
    terminal_growth: 0.02
    stage1_years: 5
```

## Write `valuation/outputs.json`

Minimum schema:

```json
{
  "ticker": "TICKER",
  "asof_date": "YYYY-MM-DD",
  "currency": "USD",
  "price": 123.45,
  "method": "three-stage-dcf-fade or two-stage-residual-income",
  "scenarios": {
    "base": {
      "equity_value": 0,
      "value_per_share": 0,
      "margin_of_safety": 0
    },
    "bull": {},
    "bear": {}
  }
}
```

For DCF runs, include `enterprise_value` in each scenario.

## Sanity Checks
- Base value should usually be between bull and bear.
- Recalculate one scenario manually to check arithmetic.
- Compare base assumptions to analyst-implied expectations; explain any intentional non-consensus stance.
- If outputs look nonsensical, verify:
  - units
  - share count denominator
  - price date alignment
  - model choice versus business economics
