# LYFT Deep-Dive Research Plan

_As of 2026-02-12 | Baseline package: 2026-02-12_

## Objective
Stress-test whether LYFT’s valuation upside survives stricter assumptions on competitive pricing, insurance cost pressure, and macro demand sensitivity while validating whether international/product expansion can offset those risks.

## Prioritized Falsification Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Priority Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Competitive intensity (especially with Uber and emerging AV ecosystems) will force lower pricing and higher incentives, compressing margins. | 5 | 4 | 2 | Most direct threat to long-term cash margins. |
| 2 | Insurance and legal/regulatory reserve volatility will structurally reduce revenue quality and cash conversion. | 5 | 3 | 2 | Cost-of-revenue and reserve mechanics are large earnings swing factors. |
| 3 | U.S. labor-demand moderation will reduce ride-demand growth and seat expansion assumptions. | 4 | 3 | 3 | Macro sensitivity can break high-single-digit growth assumptions. |
| 4 | International expansion (FreeNow/TBR) may dilute returns if integration and marketplace health underdeliver. | 4 | 3 | 3 | Expansion is a key growth lever but still early-stage. |
| 5 | Driver-classification and operating-regulation exposure could force higher structural costs. | 4 | 2 | 2 | Tail-risk with potentially large operating-model consequences. |

## Workplan
| Hypothesis | Falsification Question | Evidence Needed | Planned Sources | Pass/Fail Threshold | Status |
| --- | --- | --- | --- | --- | --- |
| Competition / incentives | Are industry economics deteriorating due low switching costs and incentive competition? | Peer disclosure on pricing/incentive behavior + LYFT risk language | `companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md`; `companies/US/LYFT/data/filings/third_party/UBER-10-K-latest.md`; `companies/US/LYFT/reports/2026-02-12-01/third-party-sources.md` | Fail if evidence implies persistent fare cuts/incentive escalation with no offset; pass if LYFT can retain volume and moderate incentive burden | Completed |
| Insurance / reserve risk | Is margin profile vulnerable to sustained insurance-cost inflation and reserve adjustments? | Cost-of-revenue bridge, reserve mechanics, management commentary | `companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md`; `companies/US/LYFT/data/financial_statements/annual/income_statement.csv` | Fail if insurance trend implies structural margin step-down below revised base margins | Completed |
| Macro demand | Does current labor data support trimming growth durability assumptions? | Official labor-demand trend and near-term payroll context | `companies/US/LYFT/reports/2026-02-12-01/third-party-sources.md` | Fail if macro data signals material demand deceleration; pass if only modest moderation | Completed |
| Expansion integration | Are FreeNow/TBR scale claims sufficient to sustain growth without value destruction? | Acquisition/market-expansion disclosures and performance indicators | `companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md`; `companies/US/LYFT/data/filings/earnings-call-2026-02-10-fool.com.md` | Fail if integration evidence weak or margin-dilutive; pass if scale and execution remain on track | Completed |
| Regulatory/worker model | Is there near-term evidence of model-breaking regulation/litigation outcomes? | Active legal disclosures, known jurisdiction risks | `companies/US/LYFT/data/filings/10-K-2026-02-11-0001628280-26-006960.md` | Fail if concrete adverse rulings force immediate model reset | Completed |
