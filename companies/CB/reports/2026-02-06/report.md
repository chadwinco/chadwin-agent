# Chubb Ltd (CB) Research Report

_As of 2026-02-06_

## Executive Summary
- Chubb is a global P&C, A&H, reinsurance, and life insurer with operations across 50+ countries and a diversified segment mix that reduces reliance on any single line or geography. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- FY2024 revenue was $55.8b and the last four years show strong cash generation: ~27% average FCF margin and ~20% average EBIT margin. (Source: companies/CB/data/income_statement_annual.csv; companies/CB/data/cash_flow_statement_annual.csv)
- Balance sheet leverage is moderate for an insurer: net debt about $11.8b and net debt/EBITDA around 1.3x on a four-year average. (Source: companies/CB/data/balance_sheet_annual.csv; companies/CB/data/income_statement_annual.csv)
- The strategic arc is global diversification and specialty scale, highlighted by the Cigna Asia A&H/life acquisition and majority control of Huatai in China. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- Valuation screens unattractive: base-case value $207.68 vs. current price $331.89 implies a -59.8% margin of safety; bull case $320.07 still implies a small negative MOS. (Source: companies/CB/model/outputs.json)
- The most material downside risks remain catastrophe volatility, reserve adequacy for long-tail lines, and pricing pressure in P&C cycles. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

## Business Overview
Chubb Ltd is a Swiss-incorporated global insurer headquartered in Zurich with a broad portfolio across commercial and personal P&C, accident & health, reinsurance, and life insurance. The company reports total assets around $246.5b and equity of $68.4b, with a workforce of roughly 43,000 employees. (Source: companies/CB/data/balance_sheet_annual.csv; companies/CB/data/company_profile.csv)

The business is organized into six segments: North America Commercial P&C, North America Personal P&C, North America Agricultural, Overseas General, Global Reinsurance, and Life Insurance. Its distribution relies heavily on brokers and agents, serving large multinational accounts, mid-market and small businesses, and affluent personal lines customers, alongside life and A&H offerings in select international markets. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

## Competitive Position
Chubb’s moat is built on scale, underwriting expertise, and breadth. Global reach and a diverse product set allow it to serve complex commercial accounts and specialty niches while spreading catastrophe and line-of-business risk. Strong financial strength ratings and claims capability are critical in winning large accounts, and Chubb’s size and balance sheet support those advantages. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md; companies/CB/data/balance_sheet_annual.csv)

That said, P&C insurance is structurally competitive and price-driven. Alternative capital and large peers can pressure pricing, and differentiation relies on underwriting discipline more than durable switching costs. Chubb’s historical margin and cash flow profile suggests it has executed well, but the durability of excess returns is tied to cycle timing and catastrophe experience. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md; companies/CB/data/income_statement_annual.csv; companies/CB/data/cash_flow_statement_annual.csv)

## Financial Quality
Revenue has grown at roughly 11% per year on a 2020–2024 CAGR, reflecting both organic growth and acquisitions. EBIT margin averaged ~19.7% over the last four years, with FCF margin averaging ~26.9% and reaching ~29.0% in FY2024, indicating strong cash conversion. (Source: companies/CB/data/income_statement_annual.csv; companies/CB/data/cash_flow_statement_annual.csv)

Using an approximate ROIC calculation (NOPAT / invested capital), Chubb averaged ~11% over the last four years, modestly above the 10% discount rate used in the base case. Net debt/EBITDA averaged ~1.3x, leaving capacity to absorb catastrophe volatility without excessive balance-sheet strain. (Source: companies/CB/data/income_statement_annual.csv; companies/CB/data/balance_sheet_annual.csv; companies/CB/model/assumptions.yaml)

## Capital Allocation
Chubb’s cash generation supports dividends, selective M&A, and balance-sheet flexibility. The current dividend is $3.88 per share, and net debt has stayed in a relatively tight band (~$10–13b) over the last several years, signaling disciplined leverage rather than aggressive balance-sheet expansion. (Source: companies/CB/data/company_profile.csv; companies/CB/data/balance_sheet_annual.csv)

Strategic acquisitions have been the primary reinvestment lever, with Cigna’s Asia A&H/life business in 2022 and a majority stake in Huatai in 2023 expanding the company’s footprint in Asia and adding scale in life and P&C. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

## Growth Opportunities
Chubb’s organic growth levers are underwriting discipline, pricing power in specialty and commercial lines, and continued penetration in high-net-worth personal lines. The breadth of distribution and product capability gives it room to cross-sell and expand wallet share, especially with broker-led commercial clients. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

International expansion is the more structural driver. Huatai adds meaningful exposure to China across life, P&C, and asset management, while the Cigna Asia acquisition broadened A&H and life offerings in select markets. These moves increase diversification and address long-term growth markets beyond the mature U.S. P&C base. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

Analyst revenue forecasts show a conservative near-term view: 2026–2027 average revenue estimates of ~$51.4b and ~$53.8b are below FY2024’s $55.8b. Upside therefore likely requires sustained pricing strength or stronger international contribution than the consensus path. (Source: companies/CB/data/analyst_estimates.csv; companies/CB/data/income_statement_annual.csv)

## Key Risks
- Catastrophe exposure (natural, cyber, geopolitical) can create large and volatile losses, and climate trends may increase frequency or severity beyond modeled expectations. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- Reserve adequacy risk remains meaningful for long-tail lines; adverse loss development can reduce earnings and erode confidence in underwriting quality. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- Competitive pricing cycles and alternative capital can compress premiums and margins, especially if capital floods the reinsurance and specialty markets. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- Multi-jurisdiction regulatory capital constraints and integration execution for Huatai and Cigna Asia could reduce flexibility or delay synergy realization. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

## Valuation
The base case assumes slightly declining revenue (-1.2% CAGR) and a 15% FCF margin with a 10% discount rate; bull case assumes modest growth (0.5%) and 17% FCF margin with a 9% discount rate; bear case assumes -4.0% growth and a 12% margin with an 11% discount rate. (Source: companies/CB/model/assumptions.yaml)

Implied values are $207.68 (base), $320.07 (bull), and $114.59 (bear) per share versus the current price $331.89. (Source: companies/CB/model/outputs.json)

## Assumptions Summary
| Scenario | Revenue Growth | FCF Margin | Discount Rate | Terminal Growth |
| --- | --- | --- | --- | --- |
| Base | -1.2% | 15.0% | 10.0% | 2.0% |
| Bull | 0.5% | 17.0% | 9.0% | 2.5% |
| Bear | -4.0% | 12.0% | 11.0% | 1.5% |

## Margin of Safety
The base-case margin of safety is -59.8% and the bull case is -3.7%. For upside, Chubb needs an extended period of favorable pricing and underwriting discipline, plus sustained benefits from international scale. The downside scenario would be driven by a severe catastrophe cycle, reserve strengthening, or a sharp turn in P&C pricing. (Source: companies/CB/model/outputs.json; companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)

## Conclusion
At today’s price, Chubb looks overvalued relative to the intrinsic value range implied by conservative assumptions. The business quality is strong, but the current valuation leaves little room for underwriting volatility or macro shocks.

Next research steps:
- Review segment-level combined ratios and reserve development to validate underwriting quality durability. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
- Compare Chubb’s margins and valuation to key peers to see whether the premium is justified. (Source: companies/CB/data/income_statement_annual.csv; companies/CB/model/outputs.json)
- Assess the long-term contribution and capital constraints from Huatai and Asia expansion. (Source: companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md)
