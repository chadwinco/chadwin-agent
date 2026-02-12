# Cal-Maine Foods, Inc. (CALM) Deep-Dive Revision

_As of 2026-02-12 (Baseline package: 2026-02-07)_

## Executive Delta
- Prior verdict: Watch
- Revised verdict: Watch
- Prior base value: $103.32/share
- Revised base value: $83.05/share
- Prior current price: $82.53
- Revised current price input: $82.53
- Base MOS change: -24.6 percentage points (from +25.2% to +0.6%)

(Source: `companies/US/CALM/reports/2026-02-07/valuation/outputs.json`; `companies/US/CALM/reports/2026-02-12/valuation/outputs.json`; `companies/US/CALM/reports/2026-02-07/report.md`)

- The baseline upside was materially reduced because FY2026 YTD gross profit and net average shell-egg pricing (especially conventional) weakened versus prior year despite acquisition-driven mix expansion. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`)
- CALM disclosed that a higher proportion of conventional sales moved to hybrid pricing frameworks in response to customer demand; management explicitly notes this can lower profitability when egg prices are high versus pure market-based pricing. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`)
- Legal overhang increased: eight new federal suits, DOJ CID and NY subpoena remain open, and legacy antitrust matters still carry uncertain outcomes, warranting a higher discount rate than baseline. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`)
- Mandatory SEC corporate-action sweep found no PREM14A/DEFM14A filings and no signed change-of-control process; standalone valuation remains appropriate without deal-cap overlays. (Source: `companies/US/CALM/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`)

## Thesis-Breaker Review
| Hypothesis | Baseline Assumption | New Evidence | Status (Holds/Weakened/Broken) | Value Impact |
| --- | --- | --- | --- | --- |
| Conventional pricing upside remains largely market-linked | Market-based frameworks preserve upside in high-price periods | Customer pressure changed terms; CALM disclosed increased hybrid pricing exposure and lower profitability in high-price periods under hybrid arrangements. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`) | Weakened | Reduced stage-1 FCF margins across scenarios |
| Diversification is already sufficient to damp commodity-cycle earnings swings | Specialty/prepared foods materially offset conventional cyclicality | FY2026 YTD mix still had conventional at 51.4% of revenue; prepared foods + egg products only 13.4%, while gross profit declined YoY. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`) | Weakened | Reduced stage-1 growth and terminal margin assumptions |
| Legal and regulatory noise is manageable within baseline discount rate | Existing accruals and disclosures are enough | Eight new suits plus federal/state investigations with unestimable outcomes; legacy cases continue, including joint-and-several exposure context. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`) | Weakened | +50 bps discount-rate uplift in base; wider downside in bear case |
| Balance-sheet downside is limited | Net cash and liquidity can absorb stress | $369.5M cash and $769.5M investments at Nov-2025 with no funded revolver borrowings support liquidity resilience. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`) | Holds | No change to net-debt assumption |
| Event-driven cap risk (take-private/M&A) | No near-term transaction cap needed | Historical SEC sweep returned 12 8-Ks, 0 PREM14A, 0 DEFM14A through 2026-02-12. (Source: `companies/US/CALM/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`) | Holds | No event-risk cap applied |

## Revised Financial and Valuation View
| Scenario | Key Assumptions (Revised) | Value/Share (Revised) | Prior Value/Share | Delta |
| --- | --- | --- | --- | --- |
| Base | Rev CAGR 0.25%; stage-1 FCF margin 8.0%; discount rate 10.0%; terminal growth 2.25%; terminal FCF margin 6.25% | $83.05 | $103.32 | -$20.27 |
| Bull | Rev CAGR 2.25%; stage-1 FCF margin 10.5%; discount rate 9.0%; terminal growth 2.75%; terminal FCF margin 8.25% | $141.72 | $184.19 | -$42.47 |
| Bear | Rev CAGR -2.0%; stage-1 FCF margin 4.25%; discount rate 11.0%; terminal growth 1.75%; terminal FCF margin 3.5% | $40.48 | $51.83 | -$11.35 |

The revised assumptions explicitly reflect evidence that CALM is shifting toward more stability-oriented pricing structures, but at the cost of peak-cycle upside capture, while legal uncertainty remains elevated. External market data also indicates ongoing egg-price volatility (sharp 2025 swings and later normalization), which supports a more conservative through-cycle base case. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/reports/2026-02-12/third-party-sources.md` (TP-1, TP-2, TP-3, TP-4); `companies/US/CALM/reports/2026-02-12/valuation/outputs.json`; `companies/US/CALM/reports/2026-02-07/valuation/outputs.json`)

## Residual Risks and Monitoring Signals
1. Antitrust/legal escalation risk remains open.
Disconfirming signal to monitor: DOJ/NY investigations close without charges and current private suits resolve near or below existing accrual expectations. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`)
2. Conventional pricing capture may remain structurally lower under hybrid frameworks.
Disconfirming signal to monitor: CALM demonstrates sustained margin stability with hybrid contracts while maintaining acceptable peak-period upside economics. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`)
3. Cage-free investment returns may underperform if demand and contracted commitments lag capacity additions.
Disconfirming signal to monitor: long-duration customer commitments rise alongside improved cage-free utilization and realized pricing. (Source: `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`)
4. HPAI-driven supply shocks remain unpredictable and can move economics sharply in either direction.
Disconfirming signal to monitor: sustained low depopulation cadence through migration seasons and reduced wholesale-price whipsaw. (Source: `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`; `companies/US/CALM/reports/2026-02-12/third-party-sources.md` (TP-1, TP-2, TP-3))

## Conclusion
The deep-dive does not break the CALM thesis, but it does compress the valuation cushion: revised base value is effectively at the current price input, not meaningfully above it. Given weaker confidence in peak-cycle margin capture and unresolved legal overhang, the correct posture remains **Watch** until either legal uncertainty clears or price offers a wider discount to revised base value. (Source: `companies/US/CALM/reports/2026-02-12/valuation/outputs.json`; `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`)
