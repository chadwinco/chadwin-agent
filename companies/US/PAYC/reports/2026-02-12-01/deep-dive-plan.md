# PAYC Deep-Dive Research Plan

_As of 2026-02-12 | Baseline package: 2026-02-12_

## Objective
Test whether PAYC's baseline long-duration growth/margin assumptions remain credible after explicitly stress-testing retention, seat-growth sensitivity, automation monetization, and litigation/regulatory downside. Baseline reference: `companies/US/PAYC/reports/2026-02-12/report.md` and `companies/US/PAYC/reports/2026-02-12/valuation/inputs.yaml`.

## Prioritized Falsification Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Priority Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Growth durability is overstated because labor-market softness and seat growth pressure can push recurring growth below high-single digits. | 5 | 3 | 3 | Largest valuation sensitivity driver is top-line compounding duration. |
| 2 | Margin durability is overstated because automation/AI investment intensity could keep FCF margins below prior assumptions. | 4 | 3 | 2 | High capex/R&D cadence can consume operating leverage. |
| 3 | Retention and competitive positioning may weaken if automation value is not translated into realized client ROI. | 4 | 3 | 2 | Retention trend is central to renewal and upsell economics. |
| 4 | Beti-related legal/regulatory overhang could impair multiples, focus, or economics. | 3 | 2 | 3 | Event risk is lower probability but potentially material to sentiment/cost. |
| 5 | Interest-on-funds tailwind could reverse in a lower-rate environment, reducing incremental earnings support. | 3 | 3 | 2 | Non-core but meaningful contributor to total revenue volatility. |

## Workplan
| Hypothesis | Falsification Question | Evidence Needed | Planned Sources | Pass/Fail Threshold | Status |
| --- | --- | --- | --- | --- | --- |
| Growth durability | Is demand/seat exposure soft enough to justify cutting stage-1 growth? | Latest recurring growth trend, management outlook, labor demand data | `companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md`; `companies/US/PAYC/data/filings/earnings-call-2026-02-11-fool.com.md`; `companies/US/PAYC/reports/2026-02-12-01/third-party-sources.md` | Fail if recurring growth trajectory supports <7% medium-term; pass if evidence supports sustained high-single-digit compounding | Completed |
| Margin durability | Are automation investments structurally pressuring cash conversion? | Capex/R&D trend, 2025 investment commentary, FCF context | `companies/US/PAYC/data/financial_statements/annual/cash_flow_statement.csv`; `companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md`; `companies/US/PAYC/data/filings/earnings-call-2026-02-11-fool.com.md` | Fail if capex + opex intensity implies normalized FCF margin <19%; pass otherwise | Completed |
| Retention/competition | Is retention/competitive pressure worsening enough to break baseline economics? | Retention trend, competitive risk language, usage/return commentary | `companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md`; `companies/US/PAYC/data/filings/earnings-call-2026-02-11-fool.com.md` | Fail if retention trend weakens and price pressure clearly accelerates; pass if retention is stable/improving with usage gains | Completed |
| Legal/regulatory | Has litigation/regulatory risk escalated enough to require a risk-premium step-change? | Current case status, funding/regulatory architecture notes | `companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md`; `companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md` | Fail if adverse legal/regulatory developments are concrete and near-term; pass if risk remains monitored but not thesis-breaking | Completed |
| Rate-tailwind fragility | Is interest-on-funds contribution too large/volatile for baseline assumptions? | Revenue mix and rate sensitivity disclosures | `companies/US/PAYC/data/filings/10-K-2025-02-20-0000950170-25-024136.md`; `companies/US/PAYC/data/filings/10-Q-2025-11-06-0001193125-25-269543.md` | Fail if non-core interest contribution is required for base-case success; pass if core recurring growth remains primary value driver | Completed |
