# LYFT Deep-Dive Changes

_As of 2026-02-12 | Baseline package: 2026-02-12-01 | Revised package: 2026-02-12-02_

## Verdict Delta
- Prior verdict: `Attractive`
- Revised verdict: `Watch`
- Prior base value: $17.53/share
- Revised base value: $15.50/share
- Prior base MOS: 25.31%
- Revised base MOS: 10.77%

This rerun revises the thesis to `Watch` because the post-earnings analyst re-rating wave was broad and centered on near-term profitability quality, not only short-term price volatility. The new base case no longer clears the +25% MOS hurdle after incorporating the downgrade drivers. (Sources: companies/US/LYFT/reports/2026-02-12-01/valuation/outputs.json, companies/US/LYFT/reports/2026-02-12-02/valuation/outputs.json, companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md)

## Assumption Delta
| Assumption (Base case) | Prior (2026-02-12-01) | Revised (2026-02-12-02) | Change | Evidence / Rationale |
| --- | --- | --- | --- | --- |
| Stage-1 revenue growth | 6.9% | 6.4% | -50 bps | Cut to reflect demand-quality skepticism in post-print analyst notes and softer read-through from rides momentum vs expectations. (Sources: companies/US/LYFT/data/filings/earnings-call-2026-02-10-fool.com.md, companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md) |
| Stage-1 FCF margin | 7.5% | 7.1% | -40 bps | Q1 adjusted EBITDA setup and commentary point to slower near-term margin expansion than previously assumed. (Sources: companies/US/LYFT/data/filings/historical/8-K-2026-02-10-with-attachments.md, companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md) |
| Discount rate | 10.8% | 11.0% | +20 bps | Raised for elevated execution/competition risk signaled by broad target resets and AV/market-share concerns. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md) |
| Terminal growth | 2.4% | 2.3% | -10 bps | Trimmed to reflect slower confidence in durable above-market growth conversion amid intensified competition. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md) |
| Terminal FCF margin | 5.7% | 5.3% | -40 bps | Lowered for persistent low-switching-cost competition and ongoing incentive/insurance variability risk. (Sources: companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md, companies/US/LYFT/data/financial_statements/annual/cash_flow_statement.csv) |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS |
| --- | --- | --- | --- | --- | --- |
| Base | $17.53 | $15.50 | -$2.03 (-11.6%) | 25.31% | 10.77% |
| Bull | $28.88 | $24.72 | -$4.16 (-14.4%) | 106.42% | 76.72% |
| Bear | $8.18 | $6.55 | -$1.63 (-19.9%) | -41.53% | -53.18% |

(Values from `valuation/outputs.json` in both report packages.)

## Corporate-Action Sweep Result
- Required 8-K/PREM14A/DEFM14A sweep found recent 8-K activity but no PREM14A/DEFM14A filings and no signed take-private/tender-process signal requiring event-cap overlays in this run. (Source: companies/US/LYFT/data/filings/historical/historical-filings-fetch-report-2026-02-12.json)

## What Did Not Change and Why
- Model type remains `three-stage-dcf-fade`; LYFT valuation still depends on long-duration cash-generation durability, not balance-sheet residual-income framing. (Sources: companies/US/LYFT/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/LYFT/reports/2026-02-12-02/valuation/inputs.yaml)
- Base-year anchors (revenue, net debt, diluted shares, price input) were unchanged to isolate the effect of rerating-driven assumption changes. (Sources: companies/US/LYFT/data/financial_statements/annual/income_statement.csv, companies/US/LYFT/data/financial_statements/annual/balance_sheet.csv, companies/US/LYFT/data/company_profile.csv)
- We did not model an immediate structural break in gross bookings because company guidance still calls for 17%-20% Q1 gross bookings growth and record rider/ride trends in 2025. (Sources: companies/US/LYFT/data/filings/historical/8-K-2026-02-10-with-attachments.md, companies/US/LYFT/data/filings/earnings-call-2026-02-10-fool.com.md)
