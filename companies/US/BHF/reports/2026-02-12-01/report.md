# Brighthouse Financial, Inc. (BHF) Deep-Dive Revision

_As of 2026-02-12 (Baseline package: 2026-02-12)_

## Executive Delta
- Prior verdict: Attractive
- Revised verdict: Attractive
- Prior base value: $84.71/share
- Revised base value: $81.63/share
- Prior current price: $64.10
- Revised current price input: $64.10
- Base MOS change: -4.80 percentage points (32.15% to 27.35%)

- Fed policy-rate cuts through 2025 support a more conservative spread/ROE path than the baseline case implied. (Source: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md)
- Industry data shows record annuity demand but meaningful mix shifts as rates declined, increasing uncertainty around sustained profitability quality. (Source: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md)
- Company-specific capital posture is solid but tight (RBC at low end of target plus ongoing buybacks), which justifies a higher required return and modestly lower terminal ROE. (Sources: companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md, companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md)
- Peer filing checks reinforce that derivatives, policyholder behavior, and capital/regulatory constraints remain structural downside channels across life/annuity models. (Source: companies/US/BHF/data/filings/third_party/MET-10-K-latest.md)

## Thesis-Breaker Review
| Hypothesis | Baseline Assumption | New Evidence | Status (Holds/Weakened/Broken) | Value Impact |
| --- | --- | --- | --- | --- |
| Rate-cycle does not pressure normalized ROE materially | Mid-teens capital return not required to support valuation upside | Fed and industry data point to a lower-rate and mix-shifting environment, reducing confidence in spread durability. (Source: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md) | Weakened | Lowered base and bull values. (Source: companies/US/BHF/reports/2026-02-12-01/valuation/outputs.json) |
| Capital flexibility remains comfortably above stress needs | Buybacks/liquidity are fully compatible with stable capital resilience | RBC was at the low end of stated target, so capital buffer quality is acceptable but not abundant. (Source: companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md) | Weakened | Increased cost-of-equity and payout conservatism in revised base case. (Source: companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml) |
| Earnings quality is stable enough for baseline ROE path | Derivative and assumption noise is manageable | 10-Q and peer disclosures continue to show material sensitivity to market and actuarial factors. (Sources: companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md, companies/US/BHF/data/filings/third_party/MET-10-K-latest.md) | Weakened | Contributed to lower terminal ROE assumption. (Source: companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml) |
| Product franchise retains competitive relevance | Shield/annuity and distribution footprint can support scale | Record Shield and annuity sales still indicate real commercial strength. (Source: companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md) | Holds | Prevented thesis break despite tighter assumptions. (Source: companies/US/BHF/reports/2026-02-12-01/deep-dive-changes.md) |

## Revised Financial and Valuation View
| Scenario | Key Assumptions (Revised) | Value/Share (Revised) | Prior Value/Share | Delta |
| --- | --- | --- | --- | --- |
| Base | ROE 10.4%, payout 41%, COE 11.6%, terminal ROE 8.8%, terminal growth 2.0%, stage-1 6 years | $81.63 | $84.71 | -$3.08 |
| Bull | ROE 12.0%, payout 36%, COE 11.0%, terminal ROE 9.6%, terminal growth 2.3%, stage-1 7 years | $104.14 | $114.37 | -$10.23 |
| Bear | ROE 7.5%, payout 52%, COE 12.6%, terminal ROE 6.5%, terminal growth 1.3%, stage-1 5 years | $50.64 | $56.20 | -$5.56 |

Deep-dive changes were targeted rather than sweeping: we kept the model and base-year anchors intact, but tightened profitability and required-return assumptions where falsification evidence was strongest (rates, capital headroom, and volatility persistence). (Sources: companies/US/BHF/reports/2026-02-12/valuation/inputs.yaml, companies/US/BHF/reports/2026-02-12-01/valuation/inputs.yaml, companies/US/BHF/reports/2026-02-12-01/third-party-sources.md)

## Residual Risks and Monitoring Signals
- Rate-path risk: disconfirm if additional easing or lower long-end yields materially compress reinvestment economics. (Sources: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md, companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md)
- Capital adequacy risk: disconfirm if RBC falls below target range or liquidity weakens while buybacks continue. (Source: companies/US/BHF/data/filings/earnings-call-2026-01-23-news.alphastreet.com.md)
- Earnings-volatility risk: disconfirm if MRB/derivative and assumption-reset noise persists at levels that depress normalized ROE. (Sources: companies/US/BHF/data/filings/10-Q-2025-11-07-0001685040-25-000071.md, companies/US/BHF/data/filings/third_party/MET-10-K-latest.md)
- Sales-mix risk: disconfirm if favorable top-line annuity demand shifts to structurally lower-return products. (Source: companies/US/BHF/reports/2026-02-12-01/third-party-sources.md)

## Conclusion
After downside-focused falsification, BHF remains `Attractive`: revised base value is $81.63 versus a $64.10 price, implying 27.35% margin of safety. (Source: companies/US/BHF/reports/2026-02-12-01/valuation/outputs.json) The thesis still works, but with lower confidence than baseline and tighter dependence on capital discipline plus rate-sensitive earnings execution. (Sources: companies/US/BHF/reports/2026-02-12-01/deep-dive-changes.md, companies/US/BHF/reports/2026-02-12-01/deep-dive-plan.md)
