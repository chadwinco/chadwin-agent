# LYFT Deep-Dive Changes

_As of 2026-02-12 | Baseline package: 2026-02-12 | Revised package: 2026-02-12-01_

## Verdict Delta
- Prior verdict: `Attractive`
- Revised verdict: `Attractive`
- Prior base value: $18.46/share
- Revised base value: $17.53/share
- Prior base MOS: 31.95%
- Revised base MOS: 25.31%

Deep-dive falsification reduced upside but did not break the thesis: competition and cost volatility warranted lower growth/margin durability assumptions, yet valuation remains above the +25% MOS threshold. (Sources: companies/US/LYFT/reports/2026-02-12/valuation/outputs.json, companies/US/LYFT/reports/2026-02-12-01/valuation/outputs.json)

## Assumption Delta
| Assumption (Base case) | Baseline | Revised | Change | Evidence / Rationale |
| --- | --- | --- | --- | --- |
| Stage-1 revenue growth | 7.2% | 6.9% | -30 bps | Trimmed for slower macro labor momentum and competition-related demand uncertainty. (Sources: companies/US/LYFT/reports/2026-02-12-01/third-party-sources.md, companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md) |
| Stage-1 FCF margin | 7.8% | 7.5% | -30 bps | Cut to reflect sustained insurance/incentive pressure and reserve volatility risk. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/data/financial_statements/annual/income_statement.csv) |
| Terminal FCF margin | 5.8% | 5.7% | -10 bps | Slightly lower long-run cash conversion due structural competition and regulatory overhead risk. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/data/filings/third_party/UBER-10-K-latest.md) |
| Bull-case growth | 9.0% | 8.5% | -50 bps | Reduced to avoid over-anchoring on high-growth narrative during early global integration phase. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/data/filings/earnings-call-2026-02-10-fool.com.md) |
| Bear-case growth | 4.5% | 4.0% | -50 bps | Deepened downside scenario for competitive and macro stress. (Sources: companies/US/LYFT/reports/2026-02-12-01/third-party-sources.md, companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md) |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS |
| --- | --- | --- | --- | --- | --- |
| Base | $18.46 | $17.53 | -$0.93 (-5.0%) | 31.95% | 25.31% |
| Bull | $33.13 | $28.88 | -$4.25 (-12.8%) | 136.80% | 106.42% |
| Bear | $9.32 | $8.18 | -$1.14 (-12.2%) | -33.36% | -41.53% |

(Values from `valuation/outputs.json` in both packages.)

## What Did Not Change and Why
- Valuation model remains `three-stage-dcf-fade`; LYFT is still best assessed via normalized long-duration cash-generation scenarios rather than residual-income framing. (Sources: companies/US/LYFT/reports/2026-02-12/valuation/inputs.yaml, companies/US/LYFT/reports/2026-02-12-01/valuation/inputs.yaml)
- Base-year anchors (revenue, net cash, diluted shares, current price input) were unchanged to keep the deep-dive signal isolated to hypothesis-driven assumption changes. (Sources: companies/US/LYFT/data/financial_statements/annual/income_statement.csv, companies/US/LYFT/data/financial_statements/annual/balance_sheet.csv, companies/US/LYFT/data/company_profile.csv)
- Final verdict stays `Attractive` because revised base MOS still clears the mandated +25% hurdle after downside testing. (Source: companies/US/LYFT/reports/2026-02-12-01/valuation/outputs.json)
