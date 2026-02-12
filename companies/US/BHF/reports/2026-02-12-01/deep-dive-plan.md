# BHF Deep-Dive Research Plan

_As of 2026-02-12 | Baseline package: 2026-02-12_

## Objective
Test whether BHF’s discount to book value is a real opportunity or a value trap driven by rate-cycle pressure, capital constraints, and earnings-quality volatility.

## Prioritized Falsification Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Priority Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Lower policy rates and product-mix shifts reduce spread economics and normalized ROE below baseline assumptions. | 5 | 4 | 2 | Most direct risk to residual-income upside. |
| 2 | Capital buffers are thinner than they appear (RBC near low end + ongoing buybacks), limiting resilience in stress periods. | 5 | 3 | 2 | Could force lower future distributions and weaker equity compounding. |
| 3 | Derivative/MRB and actuarial assumption resets keep GAAP and statutory outcomes structurally volatile. | 4 | 4 | 2 | Can impair confidence in normalized ROE and terminal assumptions. |
| 4 | Current annuity-sales strength is cyclical and cannot offset runoff and rate-sensitive pressure over a full cycle. | 4 | 3 | 3 | Needed to test demand durability versus pricing/capital costs. |
| 5 | Reinsurance and hedging execution for legacy blocks underdelivers, increasing tail-risk to capital adequacy. | 4 | 3 | 3 | Lower-probability but high-severity downside path. |

## Workplan
| Hypothesis | Falsification Question | Evidence Needed | Planned Sources | Pass/Fail Threshold | Status |
| --- | --- | --- | --- | --- | --- |
| Rate/mix pressure | Are current sales and spread economics robust in a lower-rate regime? | Official policy-rate path + independent annuity-sales mix data + company disclosures | `companies/US/BHF/reports/2026-02-12-01/third-party-sources.md`; `companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md`; `companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md` | Fail if evidence implies sustained ROE compression toward or below cost of equity | Completed |
| Capital headroom | Is BHF under-buffered after buybacks/reinsurance changes? | RBC/target range and liquidity disclosures vs return-of-capital pace | `companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md`; `companies/US/BHF/data/financial_statements/quarterly/balance_sheet.csv` | Fail if capital flexibility appears insufficient for moderate stress scenarios | Completed |
| Earnings-quality volatility | Are derivatives/MRB and assumption resets likely to keep outcomes unstable? | Volatility disclosures and actuarial-review impacts | `companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md`; `companies/US/BHF/data/financial_statements/quarterly/income_statement.csv` | Fail if recurring assumption/mark adjustments challenge normalized ROE assumptions | Completed |
| Industry comparability | Do peer disclosures support concerns on rates/capital/reinsurance complexity? | Peer primary filing disclosures on similar risk drivers | `companies/US/BHF/data/filings/third_party/MET-10-K-latest.md`; `companies/US/BHF/reports/2026-02-12-01/third-party-sources.md` | Fail if peer evidence suggests sector-wide pressure not captured in baseline | Completed |
| Reinsurance execution risk | Are recent portfolio actions reducing or adding fragility? | Company strategy disclosures and timing of reinsurance transitions | `companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md`; `companies/US/BHF/data/filings/10-K-2025-02-28-0001685040-25-000010.md` | Fail if transitions add complexity without clear capital/earnings benefit | Completed |
