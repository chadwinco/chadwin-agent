# PAYC Deep-Dive Changes

_As of 2026-02-12 | Baseline package: 2026-02-12 | Revised package: 2026-02-12-01_

## Verdict Delta
- Prior verdict: `Attractive`
- Revised verdict: `Attractive`
- Prior base value: $152.38/share
- Revised base value: $148.57/share
- Prior base MOS: 28.37%
- Revised base MOS: 25.16%

The deep-dive reduced valuation but did not break the thesis. The main downward adjustments were to growth and margin durability assumptions after testing labor sensitivity and investment intensity. (Sources: companies/US/PAYC/reports/2026-02-12/valuation/outputs.json, companies/US/PAYC/reports/2026-02-12-01/valuation/outputs.json)

## Assumption Delta
| Assumption (Base case) | Baseline | Revised | Change | Evidence / Rationale |
| --- | --- | --- | --- | --- |
| Stage-1 revenue growth | 8.2% | 8.1% | -10 bps | 2025 run-rate remains healthy but guidance and labor indicators support a modest haircut to durability expectations. (Sources: companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md, companies/US/PAYC/data/filings/earnings-call-2026-02-11-fool.com.md, companies/US/PAYC/reports/2026-02-12-01/third-party-sources.md) |
| Stage-1 FCF margin | 20.2% | 20.0% | -20 bps | Ongoing automation and infrastructure investment warrants a slightly more conservative cash-conversion path. (Sources: companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md, companies/US/PAYC/data/filings/earnings-call-2026-02-11-fool.com.md) |
| Terminal FCF margin | 17.0% | 16.5% | -50 bps | Competitive pricing pressure and continued product investment can limit long-run steady-state margin versus baseline. (Source: companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md) |
| Bear-case growth | 5.0% | 4.0% | -100 bps | Added deeper downside for macro/labor weakness and seat-volume pressure. (Sources: companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md, companies/US/PAYC/reports/2026-02-12-01/third-party-sources.md) |
| Bear-case discount rate | 11.0% | 11.5% | +50 bps | Reflects higher downside risk premium under adverse demand/competition outcomes. (Sources: companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md, companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md) |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS |
| --- | --- | --- | --- | --- | --- |
| Base | $152.38 | $148.57 | -$3.81 (-2.5%) | 28.37% | 25.16% |
| Bull | $265.09 | $240.90 | -$24.19 (-9.1%) | 123.31% | 102.93% |
| Bear | $80.54 | $66.06 | -$14.48 (-18.0%) | -32.16% | -44.35% |

(Values from `valuation/outputs.json` in both report packages.)

## What Did Not Change and Why
- Model choice stayed `three-stage-dcf-fade` because PAYC remains a non-financial SaaS business where FCF is a meaningful decision anchor. (Sources: companies/US/PAYC/reports/2026-02-12/valuation/inputs.yaml, companies/US/PAYC/reports/2026-02-12-01/valuation/inputs.yaml)
- Base-year anchors (revenue, net cash, diluted shares, and price snapshot) were preserved to isolate falsification-driven assumption changes rather than introducing mixed-period noise. (Sources: companies/US/PAYC/data/financial_statements/annual/income_statement.csv, companies/US/PAYC/data/financial_statements/annual/balance_sheet.csv, companies/US/PAYC/data/company_profile.csv)
- Verdict remained `Attractive` because the revised base case still clears the +25% MOS hurdle after stress tests. (Source: companies/US/PAYC/reports/2026-02-12-01/valuation/outputs.json)
