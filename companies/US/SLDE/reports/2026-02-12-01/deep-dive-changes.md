# SLDE Deep-Dive Changes (2026-02-12 -> 2026-02-12-01)

## Assumption Changes
- Base `roe_stage1`: `30.0%` -> `28.0%`
- Base `terminal_roe`: `17.0%` -> `16.0%`
- Base `terminal_growth`: `3.0%` -> `2.8%`
- Base `cost_of_equity`: unchanged at `12.0%`
- Base `stage1_years`: unchanged at `6`

These changes reflect a stricter view on normalized profitability durability under catastrophe/reinsurance uncertainty while preserving the same balance-sheet and price anchors. (Sources: companies/US/SLDE/reports/2026-02-12/valuation/inputs.yaml, companies/US/SLDE/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md)

## Valuation Impact
| Scenario | Prior Value/Share | Revised Value/Share | Delta |
| --- | --- | --- | --- |
| Base | $23.78 | $20.66 | -$3.12 |
| Bull | $43.34 | $31.88 | -$11.46 |
| Bear | $7.11 | $5.76 | -$1.36 |

Base MoS moved from `+45.82%` to `+26.67%` and remains above the +25% hurdle after this falsification pass. (Source: companies/US/SLDE/reports/2026-02-12-01/valuation/outputs.json)
