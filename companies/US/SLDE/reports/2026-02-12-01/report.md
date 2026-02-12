# Slide Insurance Holdings, Inc. (SLDE) Deep-Dive Revision

_As of 2026-02-12 (Baseline package: 2026-02-12)_

## Executive Delta
- Prior verdict: Attractive
- Revised verdict: Attractive
- Prior base value: $23.78/share
- Revised base value: $20.66/share
- Prior current price: $16.31/share
- Revised current price input: $16.31/share
- Base MOS change: -19.15 percentage points (45.82% to 26.67%)

- This pass tightened profitability durability assumptions after explicit stress on catastrophe and concentration risk, reducing intrinsic value while still preserving a >25% cushion. (Sources: companies/US/SLDE/reports/2026-02-12-01/deep-dive-changes.md, companies/US/SLDE/reports/2026-02-12-01/valuation/outputs.json)
- Core operating evidence remains strong: 9M 2025 combined ratio at 58.3%, ROE at 39.2%, and net premiums earned growth to $753.0M from $567.8M. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md)
- External expectation anchors remain supportive, with 5-analyst `Buy` consensus and average target $22.8. (Sources: companies/US/SLDE/data/analyst_consensus.csv, companies/US/SLDE/data/analyst_price_targets.csv)

## Thesis-Breaker Review
| Hypothesis | Baseline Assumption | New Evidence | Status (Holds/Weakened/Broken) | Value Impact |
| --- | --- | --- | --- | --- |
| Underwriting outperformance can persist | Base valuation can sustain high excess returns over cost of equity | Filing confirms strong recent ratios, but also notes no named-storm losses in 9M 2025 and inherent reserve uncertainty. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md) | Weakened | Lowered stage-1 and terminal ROE in revised base case. |
| Reinsurance framework prevents thesis break in stress years | Coverage depth and counterparty quality meaningfully cap downside | Company discloses broad catastrophe layering but also explicit counterparty and availability/pricing risk. (Sources: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md, companies/US/SLDE/data/filings/S-1-A-2025-06-09-0001193125-25-137410.md) | Holds (bounded) | Preserved Attractive verdict, but with materially lower value than baseline. |
| Growth durability remains sufficient for compounding | Citizens/renewal funnel remains viable and profitable | 9M 2025 policy renewal rate was 88.5% and policies in force increased to 351,707, but growth remains concentrated in the same core market. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md) | Holds | Supports base case above hurdle, but not prior value level. |
| Concentration does not dominate economics | Florida exposure is manageable with capital and reinsurance | Florida remains 99% of direct written premium in the latest quarter, keeping event/regulatory concentration high. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md) | Weakened | Justifies wide downside spread and position-sizing caution. |

## Revised Financial and Valuation View
| Scenario | Key Assumptions (Revised) | Value/Share (Revised) | Prior Value/Share | Delta |
| --- | --- | --- | --- | --- |
| Base | ROE 28.0%, payout 30%, COE 12.0%, terminal ROE 16.0%, terminal growth 2.8%, stage-1 6 years | $20.66 | $23.78 | -$3.12 |
| Bull | ROE 31.0%, payout 28%, COE 11.5%, terminal ROE 18.0%, terminal growth 3.0%, stage-1 7 years | $31.88 | $43.34 | -$11.46 |
| Bear | ROE 15.0%, payout 40%, COE 13.5%, terminal ROE 9.0%, terminal growth 2.0%, stage-1 5 years | $5.76 | $7.11 | -$1.36 |

Revisions are intentionally concentrated in profitability durability rather than balance-sheet anchors. Even after stress, the revised base value remains below analyst average target but above current price by a mid-20s percentage margin. (Sources: companies/US/SLDE/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/SLDE/reports/2026-02-12-01/valuation/outputs.json, companies/US/SLDE/data/analyst_price_targets.csv)

## Residual Risks and Monitoring Signals
- Catastrophe-season adverse development: monitor reserve and loss-ratio trajectory through named-storm periods. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md)
- Reinsurance renewal risk: monitor ceded premium burden and counterparty quality at treaty resets. (Sources: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md, companies/US/SLDE/data/filings/S-1-A-2025-06-09-0001193125-25-137410.md)
- Concentration/regulatory risk in Florida: monitor policy-growth quality, pricing actions, and capital restrictions. (Source: companies/US/SLDE/data/filings/10-Q-2025-11-06-0001193125-25-267339.md)

## Conclusion
After downside-focused falsification, SLDE remains `Attractive`: revised base value is $20.66 versus a $16.31 price, implying 26.67% margin of safety. (Source: companies/US/SLDE/reports/2026-02-12-01/valuation/outputs.json) The idea clears the +25% hurdle, but only with explicit acceptance of concentrated catastrophe/reinsurance risk that can compress valuation quickly under an adverse season. (Sources: companies/US/SLDE/reports/2026-02-12-01/deep-dive-plan.md, companies/US/SLDE/reports/2026-02-12-01/deep-dive-changes.md)
