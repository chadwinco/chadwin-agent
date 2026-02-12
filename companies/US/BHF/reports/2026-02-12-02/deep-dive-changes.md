# BHF Deep-Dive Changes

_As of 2026-02-12 | Baseline package: 2026-02-12-01 | Revised package: 2026-02-12-02_

## Verdict Delta
- Prior verdict: `Attractive`
- Revised verdict: `Watch`
- Prior base value: $81.63/share
- Revised base value: $64.18/share
- Prior base MOS: 27.35%
- Revised base MOS: 0.12%

The central thesis shifted from standalone value capture to event-risk balance after incorporating the signed $70 merger cap, pending close conditions, and lower break-case reference ranges. (Sources: companies/US/BHF/data/filings/historical/8-K-2025-11-06-0001685040-25-000065.md, companies/US/BHF/data/filings/historical/DEFM14A-2026-01-07-0001140361-26-000522.md, companies/US/BHF/reports/2026-02-12-02/valuation/outputs.json)

## Assumption Delta
| Assumption (Base case) | Baseline | Revised | Change | Evidence / Rationale |
| --- | --- | --- | --- | --- |
| Stage-1 ROE | 10.4% | 9.0% | -140 bps | Standalone economics were de-emphasized after merger-cap and break-risk reassessment; advisor standalone ranges did not support prior ROE persistence. (Sources: companies/US/BHF/data/filings/historical/DEFM14A-2026-01-07-0001140361-26-000522.md, companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml) |
| Payout ratio | 41% | 53% | +1200 bps | Higher effective payout reflects lower confidence in reinvestment compounding in a capped-upside, event-driven setup. (Sources: companies/US/BHF/data/filings/historical/8-K-2025-11-06-0001685040-25-000065.md, companies/US/BHF/reports/2026-02-12-02/deep-dive-plan.md) |
| Cost of equity | 11.6% | 12.6% | +100 bps | Added regulatory/closing uncertainty and break-case volatility premium. (Sources: companies/US/BHF/data/filings/historical/DEFM14A-2026-01-07-0001140361-26-000522.md, companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md) |
| Terminal ROE | 8.8% | 7.8% | -100 bps | Lower long-run return assumption aligns with advisor-implied standalone valuation context and persistent earnings sensitivity. (Sources: companies/US/BHF/data/filings/historical/DEFM14A-2026-01-07-0001140361-26-000522.md, companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md) |
| Terminal growth | 2.0% | 1.4% | -60 bps | Reduced perpetuity growth to avoid overstating post-deal-failure compounding potential. (Sources: companies/US/BHF/reports/2026-02-12-02/deep-dive-plan.md, companies/US/BHF/reports/2026-02-12-02/third-party-sources.md) |
| Stage-1 years | 6 | 5 | -1 year | Shorter explicit period reflects reduced forecasting confidence under transaction overhang and unresolved approvals. (Source: companies/US/BHF/data/filings/historical/DEFM14A-2026-01-07-0001140361-26-000522.md) |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS |
| --- | --- | --- | --- | --- | --- |
| Base | $81.63 | $64.18 | -$17.45 (-21.4%) | 27.35% | 0.12% |
| Bull | $104.14 | $70.09 | -$34.05 (-32.7%) | 62.46% | 9.34% |
| Bear | $50.64 | $47.24 | -$3.40 (-6.7%) | -21.00% | -26.31% |

(Values from `valuation/outputs.json` in baseline and revised packages.)

## What Did Not Change and Why
- Valuation framework remains `two-stage-residual-income` because BHF remains an insurer where book value and excess returns are more decision-useful than FCF. (Sources: companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/BHF/reports/2026-02-12-02/valuation/inputs.yaml)
- Base-year common equity anchor remains $6.428B (2025-09-30) to isolate thesis updates from accounting-base drift. (Source: companies/US/BHF/data/financial_statements/quarterly/balance_sheet.csv)
- Price input remains $64.10 for direct comparability versus the prior run; only thesis and share-count anchoring were revised. (Sources: companies/US/BHF/data/company_profile.csv, companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/BHF/reports/2026-02-12-02/valuation/inputs.yaml)
