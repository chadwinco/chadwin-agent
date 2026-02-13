# Moody's Corporation (MCO) Investment Snapshot

_As of 2026-02-13_

## Investment Summary
- Verdict: Watch
- Base intrinsic value: $446.99/share
- Bull/Bear range: $174.85 to $589.66/share
- Current price: $419.72
- Margin of safety (base): +6.5%

Moody’s still looks like a high-quality compounding franchise, but the current setup is a narrow-margin call rather than a clear dislocation. The core positives are resilient MA growth, strong MIS profitability, and sustained cash conversion, while the main uncertainty is how much issuance-linked cyclicality and competitive pressure can be absorbed without compressing long-duration valuation assumptions. My base case sits below the analyst average target and only modestly above price, so upside exists but is not yet wide enough for high-conviction sizing. (Source: `companies/US/MCO/data/financial_statements/annual/income_statement.csv`; `companies/US/MCO/data/financial_statements/annual/cash_flow_statement.csv`; `companies/US/MCO/data/financial_statements/quarterly/income_statement.csv`; `companies/US/MCO/data/analyst_price_targets.csv`; `companies/US/MCO/reports/2026-02-13/valuation/outputs.json`)

## Valuation Pillars (What Must Be True)
### Pillar 1: Ratings-cycle volatility must stay bounded by recurring and mix effects
MIS remains materially exposed to issuance activity, but recurring monitoring programs and related fees partially offset pure transaction swings. Recent results still show strong profitability despite uneven issuance conditions, which supports a positive but not fully de-risked growth/margin path in the model. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

### Pillar 2: MA recurring model and product breadth must keep delivering operating leverage
MA’s recurring-heavy profile and recent margin expansion are central to defending premium valuation multiples. The base case assumes MA remains a durable mid/high single-digit growth engine with steady margin improvement rather than a one-quarter peak. (Source: `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

### Pillar 3: Cost-efficiency execution must convert restructuring into durable savings
Management’s multi-year Strategic and Operational Efficiency Restructuring Program targets substantial annualized savings and is intended to complete by end-2026. The valuation assumes the program lifts sustained free-cash-flow conversion without sacrificing growth execution in MA and ratings quality in MIS. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

### Pillar 4: Contracted revenue durability must persist through portfolio changes
Deferred/remaining performance obligation disclosures indicate meaningful contracted revenue visibility in MA, while MIS has a smaller but still relevant monitoring-related deferred base. The announced MA Learning Solutions divestiture appears non-material, so the model remains focused on core MA/MIS economics. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`)

## Market-Implied Expectations (Analyst Anchor)
| Signal | Current Read | Implication for Base Case |
| --- | --- | --- |
| Consensus stance / analyst count | Buy, 17 analysts | Market still prices MCO as a quality compounder rather than a late-cycle value name |
| Revenue outlook dispersion | FY2025 avg $7.8B (range $7.5B-$8.2B); FY2026 avg $8.4B (range $8.0B-$8.9B) | Supports high-single-digit growth assumptions, but not a step-change growth regime |
| EPS and forward P/E path | EPS $14.87 (2025E) to $16.56 (2026E); forward P/E 28.23x to 25.35x | Implies growth with some multiple normalization, consistent with moderate rerating upside |
| Price target range and median | Low $507, median $552, high $660, average $558.44 | Street central tendency is above my base value, indicating my assumptions are more conservative than consensus |
| Recent ratings/target revisions | Several January upgrades/target raises, plus selective trims (for example $603 to $532 on 2026-02-09) | Momentum is positive but not one-way, supporting a balanced Watch stance |

My base case aligns with consensus on continued earnings/revenue growth but differs by using a more conservative long-run spread between growth durability and discount-rate risk than the median target implies. (Source: `companies/US/MCO/data/analyst_consensus.csv`; `companies/US/MCO/data/analyst_revenue_estimates.csv`; `companies/US/MCO/data/analyst_eps_estimates.csv`; `companies/US/MCO/data/analyst_eps_forward_pe_estimates.csv`; `companies/US/MCO/data/analyst_price_targets.csv`; `companies/US/MCO/data/analyst_ratings_actions_12m.csv`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

## Business and Competitive Position
Moody’s operates two reportable segments: MA (analytics/data/workflow) and MIS (ratings). MIS is structurally tied to issuance activity, while recurring monitoring fees and related programs help damp pure transaction cyclicality. This mix creates a high-quality but cycle-sensitive earnings profile rather than a pure subscription utility. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`)

Competition is broad across both segments: MA faces software/data/analytics providers across Decision Solutions, Research & Insights, and Data & Information, while MIS faces regulatory and market-share pressure across ratings categories. The durability argument is therefore less about monopoly conditions and more about brand, embedded workflows, and continued product execution in areas like private credit and AI-enabled offerings. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`)

## Financial Quality
| Metric | Latest | 3-5Y Trend | Comment |
| --- | --- | --- | --- |
| Revenue / premium / fee growth | Q3 2025 revenue $2.007B (+10.7% YoY) | 2019-2024 revenue CAGR about 8.0% | Growth has remained resilient despite issuance volatility |
| Operating profitability (EBIT or pre-tax margin) | 2024 operating margin 40.6%; Q3 2025 operating margin 45.7% | Expanded versus 2019-2023 levels | Margin profile supports premium valuation, but cyclicality remains |
| Cash generation (FCF or operating-cash proxy) | 2024 OCF $2.838B; capex $317M; FCF proxy $2.521B (35.6% margin) | Consistently strong conversion in recent years | Asset-light economics are a key valuation support |
| Returns metric (ROIC or ROE proxy) | 2024 net-income ROE proxy 55.2% | Elevated and supported by buybacks plus high margins | Very high ROE is favorable but partly equity-base driven |
| Leverage / capital adequacy | Net debt about $5.02B (2024) and $4.80B (Q3 2025) | Net debt broadly stable with high cash generation | Balance sheet is manageable but not trivial for a long-duration multiple |

The strongest support metric is sustained high cash conversion at scale. The first break signal would be a multi-quarter combination of weaker issuance-linked volume and lower MA growth that compresses operating margin and reduces FCF conversion. (Source: `companies/US/MCO/data/financial_statements/annual/income_statement.csv`; `companies/US/MCO/data/financial_statements/annual/balance_sheet.csv`; `companies/US/MCO/data/financial_statements/annual/cash_flow_statement.csv`; `companies/US/MCO/data/financial_statements/quarterly/income_statement.csv`; `companies/US/MCO/data/financial_statements/quarterly/balance_sheet.csv`)

## Key Issue Resolution and Falsification
This run tested whether MCO’s premium valuation can still be defended after anchoring to local statements, latest 10-Q disclosures, analyst expectations, and event-risk checks. Assumptions were tightened toward the analyst growth baseline but kept below consensus valuation central tendency to account for issuance and discount-rate sensitivity. (Source: `companies/US/MCO/data/analyst_price_targets.csv`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

| Issue | Why It Matters | Resolution Status (Resolved/Bounded/Open) | Evidence | Valuation Impact |
| --- | --- | --- | --- | --- |
| Is issuance exposure still manageable? | MIS transaction cyclicality can swing consolidated earnings | Bounded | 10-K dependence disclosure plus Q3 2025 MIS growth/margin evidence | Supports positive base growth with bear-case deceleration |
| Can MA sustain growth-plus-margin expansion? | MA durability underwrites long stage-1 period assumptions | Bounded | 10-Q segment growth/margin and Q2 2025 transcript operating commentary | Supports base 9.5% stage-1 growth and 34% stage-1 FCF margin |
| Will restructuring benefits convert to real economics? | Savings delivery is needed to defend margin durability | Bounded | Program target savings and completion timeline in 10-K/10-Q | Supports base/bull margin assumptions; execution miss is bear driver |
| Any control-transaction event risk overriding standalone valuation? | Signed transactions can cap upside or change downside framing | Resolved | Recent 8-Ks cover governance/compensation; no signed control transaction disclosed; MA Learning Solutions divestiture described as non-material | Standalone DCF remains appropriate |

(Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/data/filings/8-K-2025-12-19-0001059556-25-000197.md`; `companies/US/MCO/data/filings/8-K-2026-01-12-0001059556-26-000004.md`; `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`)

## Valuation
| Scenario | Core Assumptions | Discount / Cost of Equity | Terminal Assumption | Value/Share | MOS vs Price |
| --- | --- | --- | --- | --- | --- |
| Base | 9.5% stage-1 revenue growth; 34% stage-1 FCF margin; 11-year stage 1 + 5-year fade | 7.8% discount rate | 2.5% terminal growth; 29% terminal FCF margin | $446.99 | +6.5% |
| Bull | 10.5% stage-1 revenue growth; 35% stage-1 FCF margin; 11-year stage 1 + 5-year fade | 7.4% discount rate | 2.8% terminal growth; 30% terminal FCF margin | $589.66 | +40.5% |
| Bear | 6.0% stage-1 revenue growth; 29% stage-1 FCF margin; 8-year stage 1 + 5-year fade | 9.2% discount rate | 2.0% terminal growth; 25% terminal FCF margin | $174.85 | -58.3% |

The base case assumes Moody’s can keep high-single-digit growth and strong cash conversion while sustaining some benefit from efficiency execution, but it does not assume the full optimism embedded in analyst average targets. This is why base value remains above spot but below the median/average sell-side target range. (Source: `companies/US/MCO/data/analyst_price_targets.csv`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`; `companies/US/MCO/reports/2026-02-13/valuation/outputs.json`)

The bull case requires durable private-credit and MA platform tailwinds with limited competitive/macro friction. The bear case reflects simultaneous issuance softness, margin pressure, and a higher required return, which materially compresses long-duration DCF value. (Source: `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`; `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`; `companies/US/MCO/reports/2026-02-13/valuation/outputs.json`)

## Key Risks and Disconfirming Signals
1. Issuance-cycle shock in global credit markets reduces MIS transaction revenue and weakens consolidated operating leverage. Disconfirming signal: sustained recurring-fee growth offsetting transaction weakness over multiple quarters. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`)
2. Competitive and pricing pressure across data/analytics and credit opinions, including GenAI-enabled substitutes, compresses growth or margin. Disconfirming signal: continued MA recurring growth and stable/improving MA operating margin with no material retention deterioration. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/earnings-call-2025-07-23-fool.com.md`)
3. Regulatory/legal actions in ratings markets increase compliance costs or reduce franchise economics. Disconfirming signal: no material new adverse regulatory findings and sustained MIS margin stability. (Source: `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`)
4. Restructuring and portfolio-change execution risk (including MA Learning Solutions divestiture timing) disrupts margin trajectory. Disconfirming signal: program savings realization with stable organic growth and limited transition friction. (Source: `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`; `companies/US/MCO/data/filings/10-K-2025-02-14-0001059556-25-000025.md`)
5. Valuation duration risk from rate sensitivity: small discount-rate increases can materially lower DCF value. Disconfirming signal: persistent earnings growth with market-rate stability that supports current required-return assumptions. (Source: `companies/US/MCO/reports/2026-02-13/valuation/inputs.yaml`; `companies/US/MCO/reports/2026-02-13/valuation/outputs.json`)

## Conclusion
At $419.72, MCO screens slightly above fair value in this run, but only with a modest base margin of safety. The business quality is high and operational momentum remains good, yet the current valuation still requires continued strong execution and a supportive funding/issuance backdrop. The call is `Watch` until either price offers a wider entry buffer or new evidence increases confidence that current elevated cash-conversion and growth durability can persist through a full cycle. (Source: `companies/US/MCO/data/company_profile.csv`; `companies/US/MCO/reports/2026-02-13/valuation/outputs.json`; `companies/US/MCO/data/filings/10-Q-2025-10-23-0001628280-25-046118.md`)

## Research Stop Gate
- Thesis confidence: 82%
- Highest-impact levers: 4
- Levers resolved: 4
- Open thesis-critical levers: 0
- Diminishing returns from additional research: Yes
- Research complete: Yes
- Next best research focus: None

Current high-impact levers are resolved or bounded with direct valuation sensitivity, and additional work is more likely to tighten scenario width than change the current Watch decision at this price.
