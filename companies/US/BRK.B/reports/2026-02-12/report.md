# Berkshire Hathaway Inc. (BRK.B) Investment Snapshot

_As of 2026-02-12_

## Investment Summary
- Verdict: Watch
- Base intrinsic value: $506.03/share
- Bull/Bear range: $328.99 to $606.84/share
- Current price: $504.53
- Margin of safety (base): +0.3%

Berkshire screens as roughly fairly valued on a residual-income basis at the current quote, with a base case that is close to spot and a wide outcome band driven by underwriting/event losses and equity-portfolio volatility. Conviction improved most from confirming balance-sheet scale and liquidity (including very large cash and U.S. Treasury Bill holdings) and from anchoring valuation on the latest local book-value/share base, while the main unresolved uncertainty is how durable excess returns remain through market and catastrophe cycles under new leadership execution. The base MOS is real but de minimis, so this is a monitor-first setup rather than a high-urgency entry. (Source: `companies/US/BRK.B/reports/2026-02-12/valuation/outputs.json`; `companies/US/BRK.B/data/company_profile.csv`; `companies/US/BRK.B/data/financial_statements/quarterly/balance_sheet.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`)

## Valuation Pillars (What Must Be True)
### Pillar 1: Excess returns on book value must stay above cost of equity
The model requires Berkshire to sustain ROE meaningfully above cost of equity for a long period. Local annuals support that as plausible but not guaranteed: FY2024 ROE was about 13.7% and the multi-year profile remains volatile because investment marks can swing earnings, including a loss year in 2022. Base assumptions therefore set stage-1 ROE at 13.5% against 9.5% cost of equity, with a terminal ROE fade to 10.5% instead of extrapolating recent high years. If ROE settles closer to cost of equity for an extended period, value per share compresses toward book-based outcomes quickly. (Source: `companies/US/BRK.B/data/financial_statements/annual/income_statement.csv`; `companies/US/BRK.B/data/financial_statements/annual/balance_sheet.csv`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`; `companies/US/BRK.B/reports/2026-02-12/valuation/outputs.json`)

### Pillar 2: Liquidity and capital-allocation flexibility must remain a structural advantage
Berkshire’s capital position remains a core support for downside containment and optionality: local quarterlies show large cash and U.S. Treasury Bill balances at 2025-09-30, and the repurchase framework retains a hard liquidity floor. At the same time, no repurchases were made in the first nine months of 2025, which implies management can choose to preserve optionality instead of forcing per-share accretion at any price. This pillar maps to payout assumptions (20% base/bull, 30% bear) and supports keeping intrinsic-value dispersion wide around capital-deployment execution. (Source: `companies/US/BRK.B/data/financial_statements/quarterly/balance_sheet.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`)

### Pillar 3: Equity portfolio concentration risk must stay manageable
Management explicitly flags that equity investments are concentrated, and the latest 10-Q notes the five largest positions represented 66% of equity-securities fair value at September 30, 2025. That concentration can amplify both upside and downside in reported earnings and book value, so valuation cannot assume smooth compounding. In the model, this is handled through a conservative base cost of equity and a bear case that narrows excess-return spread rather than assuming permanent outperformance from market marks. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`)

### Pillar 4: Insurance-event volatility and leadership transition must not impair capital discipline
Recent filings show catastrophe loss pressure (including Southern California wildfire losses) and governance transition milestones (Greg Abel as CEO from January 1, 2026 and planned CFO succession in 2026-2027). The operating thesis remains intact only if underwriting discipline and capital allocation remain consistent through this transition while catastrophe experience stays within modeled tolerance. This pillar drives the bear scenario’s higher cost of equity and lower ROE spread versus base. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`; `companies/US/BRK.B/data/filings/8-K-2025-12-11-0001193125-25-314935.md`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`)

## Market-Implied Expectations (Analyst Anchor)
| Signal | Current Read | Implication for Base Case |
| --- | --- | --- |
| Consensus stance / analyst count | Strong Buy, 1 analyst | Positive signal but low breadth, so confidence uplift is limited |
| Revenue outlook dispersion | FY2025 avg $386.2B (range $364.5B-$396.7B); FY2026 avg $385.1B (range $337.2B-$416.9B) | Supports moderate growth expectations with wide uncertainty |
| EPS and forward P/E path | EPS 21.92 (2025) to 22.13 (2026); forward P/E 23.00x to 22.78x | Implies near-term earnings normalization rather than accelerating EPS |
| Price target range and median | Low/median/high all $595 (average $595; +18% indicated upside) | Suggests upside to current price, but target distribution is not diversified |
| Recent ratings/target revisions | Six late-2025 updates, all maintains, targets moving within ~$591-$606 | Momentum is constructive but incremental, not a regime shift |

The base case intentionally sits below the single-analyst $595 target, because local filing evidence still points to meaningful volatility channels (equity marks, catastrophe severity, and transition execution) that are hard to treat as low-variance. (Source: `companies/US/BRK.B/data/analyst_consensus.csv`; `companies/US/BRK.B/data/analyst_revenue_estimates.csv`; `companies/US/BRK.B/data/analyst_eps_estimates.csv`; `companies/US/BRK.B/data/analyst_eps_forward_pe_estimates.csv`; `companies/US/BRK.B/data/analyst_price_targets.csv`; `companies/US/BRK.B/data/analyst_ratings_actions_12m.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`)

## Business and Competitive Position
Berkshire remains a diversified operating-and-investment conglomerate across insurance/reinsurance, utilities and energy, freight rail, manufacturing, services, and retailing. That structure provides multiple earnings engines and capital-recycling options that are difficult to replicate at comparable scale. (Source: `companies/US/BRK.B/data/filings/8-K-2025-12-11-0001193125-25-314935.md`)

The competitive advantage is not single-product growth; it is capital allocation under a decentralized operating model and balance-sheet depth that can absorb stress while preserving optionality. The main structural vulnerability is that a meaningful part of intrinsic value is still tied to concentrated listed-equity exposure and insurance-event variability, which can move book value and reported earnings materially in either direction over short windows. (Source: `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/financial_statements/quarterly/balance_sheet.csv`)

Leadership transition is now in execution mode (CEO transition effective January 1, 2026 with planned CFO succession), so valuation durability depends on continuity in underwriting and capital-deployment discipline rather than strategic reinvention. (Source: `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`; `companies/US/BRK.B/data/filings/8-K-2025-12-11-0001193125-25-314935.md`)

## Financial Quality
| Metric | Latest | 3-5Y Trend | Comment |
| --- | --- | --- | --- |
| Revenue growth | FY2024 revenue $371.4B | FY2019-FY2024 CAGR ~7.8% | Solid top-line expansion across a diversified base |
| Operating profitability (pre-tax proxy) | FY2024 pre-tax income $110.4B (~29.7% of revenue) | Highly variable across years due investment and catastrophe effects | Reported profitability is strong but inherently noisy |
| Cash generation | FY2024 operating cash flow $30.6B (~8.2% margin) | OCF was ~$37.2B-$49.2B in FY2021-FY2023 | 2024 cash conversion weakened versus recent run-rate |
| Returns proxy | FY2024 ROE ~13.7% | Roughly ~12.0% average over FY2019-FY2024, with a loss year in 2022 | Excess-return capacity exists but is cyclical |
| Leverage / capital adequacy | 2025-09-30 cash + T-bills ~$377.5B vs debt ~$45.6B; equity ~$700.4B | Equity base expanded from ~$428.6B (2019) to ~$700.4B (2025-09-30) | Balance sheet remains a major strategic buffer |

The most supportive metric is balance-sheet scale and liquidity; the earliest break signal would be a sustained compression in ROE toward cost of equity paired with weaker underwriting results and equity-portfolio drawdowns. (Source: `companies/US/BRK.B/data/financial_statements/annual/income_statement.csv`; `companies/US/BRK.B/data/financial_statements/annual/balance_sheet.csv`; `companies/US/BRK.B/data/financial_statements/annual/cash_flow_statement.csv`; `companies/US/BRK.B/data/financial_statements/quarterly/balance_sheet.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`)

## Key Issue Resolution and Falsification
This run tested whether Berkshire still merits a long-duration excess-return framing despite visible volatility channels. Evidence resolved the core balance-sheet and business-mix questions and bounded the key uncertainties (catastrophe severity, portfolio concentration, and leadership transition) with explicit scenario penalties in cost-of-equity and terminal-return assumptions. Recent 8-K filings in the local package show leadership and financing events rather than signed M&A/take-private actions, so no event-cap overlay was applied. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`; `companies/US/BRK.B/data/filings/8-K-2025-11-21-0001193125-25-290864.md`; `companies/US/BRK.B/data/filings/8-K-2025-12-11-0001193125-25-314935.md`; `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`)

| Issue | Why It Matters | Resolution Status (Resolved/Bounded/Open) | Evidence | Valuation Impact |
| --- | --- | --- | --- | --- |
| Durability of excess ROE | Primary driver of residual-income premium to book | Resolved | Annual ROE and equity growth profile | Sets base `roe_stage1` 13.5% and terminal fade to 10.5% |
| Equity portfolio concentration | Can swing earnings/book value materially | Bounded | Top-five holdings concentration and risk-factor disclosure | Keeps cost of equity conservative in base and higher in bear |
| Catastrophe / reserve volatility | Directly affects insurance earnings and capital confidence | Bounded | 2025 wildfire loss disclosures and underwriting-risk language | Narrows bear ROE spread and lowers terminal growth |
| Leadership transition execution | Capital allocation quality is central to long-term value | Bounded | CEO/CFO transition filings | Prevents aggressive upside extrapolation in base case |

## Valuation
| Scenario | Core Assumptions | Discount / Cost of Equity | Terminal Assumption | Value/Share | MOS vs Price |
| --- | --- | --- | --- | --- | --- |
| Base | ROE 13.5%; payout 20%; 10-year stage 1 | 9.5% | Terminal ROE 10.5%; terminal growth 3.0% | $506.03 | +0.3% |
| Bull | ROE 14.0%; payout 20%; 10-year stage 1 | 9.0% | Terminal ROE 10.8%; terminal growth 3.0% | $606.84 | +20.3% |
| Bear | ROE 11.0%; payout 30%; 8-year stage 1 | 10.5% | Terminal ROE 10.3%; terminal growth 2.3% | $328.99 | -34.8% |

Base assumptions are central rather than optimistic because they retain a meaningful spread of ROE over cost of equity but do not assume repurchases or market gains smooth out reported volatility. The base also stays below the single available analyst target to reflect concentration and catastrophe risk explicitly. (Source: `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`; `companies/US/BRK.B/reports/2026-02-12/valuation/outputs.json`; `companies/US/BRK.B/data/analyst_price_targets.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`)

Bull requires sustained low-double-digit ROE durability with limited catastrophe/securities shocks and continued capital-allocation discipline through leadership transition. Bear reflects weaker underwriting and equity-mark outcomes that compress excess returns close to cost-of-equity levels for long enough to erode the premium to book. (Source: `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`; `companies/US/BRK.B/reports/2026-02-12/valuation/inputs.yaml`)

## Key Risks and Disconfirming Signals
1. Catastrophe-loss severity exceeds modeled tolerance.
Mechanism: outsized event losses can pressure underwriting earnings, reserve confidence, and implied excess ROE. Disconfirming signal: multiple periods with catastrophe losses and reserve development materially above recent range. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`)
2. Concentrated equity holdings re-rate lower.
Mechanism: concentrated market declines can reduce book value and statutory surplus, compressing valuation multiples and underwriting flexibility. Disconfirming signal: sustained fair-value drawdowns in top holdings with associated capital-pressure commentary. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`)
3. Regulated infrastructure financing and policy risk at BHE/BNSF rises.
Mechanism: higher capital costs or regulatory constraints can lower subsidiary returns and group-level capital efficiency. Disconfirming signal: persistent covenant/funding stress, rate-case shortfalls, or adverse regulatory shifts in rail/utility operations. (Source: `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`)
4. Leadership transition disrupts capital-allocation consistency.
Mechanism: weaker investment or repurchase discipline can reduce long-duration compounding and narrow excess-return persistence. Disconfirming signal: clear deterioration in capital deployment quality relative to historical policy framing. (Source: `companies/US/BRK.B/data/filings/8-K-A-2026-01-06-0001193125-26-004727.md`; `companies/US/BRK.B/data/filings/8-K-2025-12-11-0001193125-25-314935.md`; `companies/US/BRK.B/data/filings/10-K-2025-02-24-0000950170-25-025210.md`)

## Conclusion
At $504.53, Berkshire looks close to fair value in the base case, with upside that is meaningful but not mispricing-level unless excess returns remain high and volatility stays contained. The key reason this is not an outright avoid call is balance-sheet depth and durable diversification across operating and investment engines. The key reason this is not an attractive call is that the current price already captures most of the central-case residual-income value, leaving limited base-case cushion. Positioning is best treated as watch/quality hold unless price weakness or stronger evidence on excess-return durability creates a larger margin of safety. (Source: `companies/US/BRK.B/data/company_profile.csv`; `companies/US/BRK.B/reports/2026-02-12/valuation/outputs.json`; `companies/US/BRK.B/data/financial_statements/quarterly/balance_sheet.csv`; `companies/US/BRK.B/data/filings/10-Q-2025-11-03-0001193125-25-261548.md`)

## Research Stop Gate
- Thesis confidence: 82%
- Highest-impact levers: 4
- Levers resolved: 4
- Open thesis-critical levers: 0
- Diminishing returns from additional research: Yes
- Research complete: Yes
- Next best research focus: None

Additional cycles are unlikely to change the directional call materially without new data because the main decision levers now have explicit scenario translation and the remaining uncertainty is mostly about monitoring volatility magnitude, not undiscovered business-model unknowns.
