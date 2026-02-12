# CALM Deep-Dive Research Plan

_As of 2026-02-12 | Baseline package: 2026-02-07_

## Objective
Test whether CALM's baseline margin-of-safety remains valid once customer pricing-framework changes, litigation overhang, and post-acquisition mix quality are stressed against current evidence.

## Prioritized Falsification Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Priority Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Customer pressure is structurally shifting conventional-egg pricing away from pure market upside capture. | 5 | 4 | 3 | Highest P&L sensitivity because conventional eggs remain the largest revenue bucket. |
| 2 | Diversification into specialty/prepared foods is not yet large enough to offset conventional price compression. | 4 | 4 | 2 | Revenue mix improved, but consolidated gross profit still fell materially YoY. |
| 3 | Legal/regulatory overhang (civil suits + antitrust investigations) is underpriced in discount-rate assumptions. | 4 | 3 | 4 | Potential outcomes remain unbounded in disclosures; baseline used no explicit risk premium. |
| 4 | Balance-sheet resilience is weaker than reported once acquisition spending and buybacks are included. | 3 | 2 | 1 | Needed to test downside funding fragility before adding a risk premium. |
| 5 | Corporate-action event risk (take-private/M&A cap) invalidates standalone valuation framing. | 3 | 2 | 2 | Mandatory deep-dive sweep requirement. |

## Workplan
| Hypothesis | Falsification Question | Evidence Needed | Planned Sources | Pass/Fail Threshold | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Are contract structures shifting toward lower upside capture for CALM in high-price regimes? | Explicit company disclosures on market-based vs hybrid/cost-plus pricing and profitability impact. | `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`; `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` | Fail if management discloses growing hybrid exposure plus lower profitability in high-price periods; cut stage-1 FCF margin. | Completed (Failed baseline assumption) |
| 2 | Is mix-shift enough to stabilize earnings through conventional price normalization? | Product-mix and gross-profit YoY bridge with current-period segment data. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/financial_statements/quarterly/income_statement.csv` | Fail if conventional remains >50% of sales and prepared+egg products <15% while gross profit declines YoY; reduce growth/margins. | Completed (Failed baseline assumption) |
| 3 | Do current legal disclosures justify adding an explicit valuation risk premium? | Case counts, potential liabilities, accrual levels, and investigation status. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md` | Fail if losses are not reasonably estimable and material outcomes exceed accrued amounts; raise discount rates/widen bear case. | Completed (Failed baseline assumption) |
| 4 | Is CALM exposed to near-term funding stress under downside assumptions? | Cash/investments, debt usage, covenants, and liquidity headroom. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`; `companies/US/CALM/data/financial_statements/quarterly/balance_sheet.csv` | Pass if cash+investments >$800M and no funded debt, with revolver capacity intact; keep net debt assumption unchanged. | Completed (Passed baseline assumption) |
| 5 | Is there signed/proposed transaction evidence that caps upside or changes downside (deal break risk)? | Historical SEC sweep for M&A/take-private proxy forms and related 8-K disclosures. | `companies/US/CALM/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`; `companies/US/CALM/data/filings/historical/8-K-2025-06-02-0001562762-25-000156.md`; `companies/US/CALM/data/filings/historical/8-K-2025-04-17-0001213900-25-032989.md` | Pass if no PREM14A/DEFM14A and no signed change-of-control event; keep standalone valuation (no event-risk cap). | Completed (Passed baseline assumption) |

## Corporate-Action Sweep Result (Required)
- SEC helper run completed for `8-K, PREM14A, DEFM14A` through `2026-02-12`; fetched 12 `8-K` filings and zero `PREM14A`/`DEFM14A`. (Source: `companies/US/CALM/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`)
- Observed events were governance recapitalization actions, share repurchase/secondary-offering mechanics, and acquisition close disclosures, not a signed take-private or merger process requiring event-risk valuation caps. (Source: `companies/US/CALM/data/filings/historical/8-K-2025-03-27-0001562762-25-000058.md`; `companies/US/CALM/data/filings/historical/8-K-2025-04-17-0001213900-25-032989.md`; `companies/US/CALM/data/filings/historical/8-K-2025-06-02-0001562762-25-000156.md`)
