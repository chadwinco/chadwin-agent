# BHF Deep-Dive Changes

_As of 2026-02-12 | Baseline package: 2026-02-12 | Revised package: 2026-02-12-01_

## Verdict Delta
- Prior verdict: `Attractive`
- Revised verdict: `Attractive`
- Prior base value: $84.71/share
- Revised base value: $81.63/share
- Prior base MOS: 32.15%
- Revised base MOS: 27.35%

Deep-dive falsification reduced valuation headroom but did not break the thesis: rate-cycle and capital-sensitivity evidence supported tighter assumptions, yet base MoS still remains above +25%. (Sources: companies/US/BHF/reports/2026-02-12/valuation/outputs.json, companies/US/BHF/reports/2026-02-12-01/valuation/outputs.json, companies/US/BHF/reports/2026-02-12-01/third-party-sources.md)

## Assumption Delta
| Assumption (Base case) | Baseline | Revised | Change | Evidence / Rationale |
| --- | --- | --- | --- | --- |
| Stage-1 ROE | 10.5% | 10.4% | -10 bps | Trimmed for lower-rate backdrop and annuity mix pressure risk. (Sources: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md, companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md) |
| Payout ratio | 40% | 41% | +100 bps | Slightly higher payout reflects active return-of-capital posture with tighter capital balance. (Sources: companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md, companies/US/BHF/reports/2026-02-12-01/third-party-sources.md) |
| Cost of equity | 11.5% | 11.6% | +10 bps | Higher required return to reflect volatility and capital/rate sensitivity. (Sources: companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md, companies/US/BHF/data/filings/third_party/MET-10-K-latest.md) |
| Terminal ROE | 9.0% | 8.8% | -20 bps | Reduced for long-run spread and assumption-reset uncertainty. (Sources: companies/US/BHF/data/filings/10-K-2025-02-28-0001685040-25-000010.md, companies/US/BHF/reports/2026-02-12-01/third-party-sources.md) |
| Bull-case ROE | 12.5% | 12.0% | -50 bps | Lowered to avoid over-crediting peak sales momentum in a softer-rate regime. (Sources: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md, companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md) |
| Bear-case ROE | 8.0% | 7.5% | -50 bps | Deepened downside for prolonged pressure on spread returns and capital flexibility. (Sources: companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md, companies/US/BHF/data/filings/third_party/MET-10-K-latest.md) |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS |
| --- | --- | --- | --- | --- | --- |
| Base | $84.71 | $81.63 | -$3.08 (-3.6%) | 32.15% | 27.35% |
| Bull | $114.37 | $104.14 | -$10.23 (-8.9%) | 78.42% | 62.46% |
| Bear | $56.20 | $50.64 | -$5.56 (-9.9%) | -12.33% | -21.00% |

(Values from `valuation/outputs.json` in baseline and revised packages.)

## What Did Not Change and Why
- Valuation method remains `two-stage-residual-income` because BHF is capital- and balance-sheet-driven; FCF is less decision-useful for this business model. (Sources: companies/US/BHF/reports/2026-02-12/valuation/inputs.yaml, companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml)
- Base-year equity and share-count anchors were unchanged to isolate deep-dive impacts to thesis assumptions rather than data base changes. (Sources: companies/US/BHF/data/financial_statements/quarterly/balance_sheet.csv, companies/US/BHF/data/company_profile.csv)
- Final verdict stays `Attractive` because revised base MoS still clears the required +25% threshold after downside stress. (Source: companies/US/BHF/reports/2026-02-12-01/valuation/outputs.json)
