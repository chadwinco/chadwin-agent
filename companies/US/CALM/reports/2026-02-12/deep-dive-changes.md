# CALM Deep-Dive Change Log

_As of 2026-02-12 | Baseline package: 2026-02-07_

## Verdict Delta
- Prior verdict: **Watch**
- Revised verdict: **Watch**
- Interpretation change: prior thesis leaned on a meaningful valuation discount; revised work indicates CALM is closer to fair value after explicit stress on pricing-framework shifts and legal overhang.

## Assumption Delta (Baseline vs Revised)
| Scenario | Input | Baseline (2026-02-07) | Revised (2026-02-12) | Why Changed | Evidence |
| --- | --- | --- | --- | --- | --- |
| Base | Revenue growth (stage 1) | 1.0% | 0.25% | FY2026 YTD total sales declined 2.8% YoY while conventional sales remained the largest mix component; diversification is improving but not yet enough to support prior growth confidence. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/reports/2026-02-12/third-party-sources.md` (TP-1) |
| Base | FCF margin (stage 1) | 9.0% | 8.0% | Gross profit fell from $603.3M to $518.7M YoY and conventional pricing declined sharply; management also disclosed hybrid pricing can reduce profitability in high-price periods. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` |
| Base | Discount rate | 9.5% | 10.0% | New antitrust suits, DOJ CID/NY subpoena, and ongoing legacy antitrust exposure keep outcome range open and justify a risk premium. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md` |
| Base | Terminal growth | 2.5% | 2.25% | Pricing normalization evidence in USDA/BLS data supports a slightly more conservative long-run growth anchor. | `companies/US/CALM/reports/2026-02-12/third-party-sources.md` (TP-2, TP-3, TP-4) |
| Base | Terminal FCF margin | 7.0% | 6.25% | Through-cycle profitability uncertainty remains elevated due pricing-model transition and unresolved litigation/investigation outcomes. | `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`; `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` |
| Bull | Revenue growth (stage 1) | 3.0% | 2.25% | Trimmed to reflect lower near-term visibility despite prepared-foods expansion. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` |
| Bull | FCF margin (stage 1) | 12.0% | 10.5% | Still constructive on mix upgrade, but now constrained by contractual pricing changes and volatility in conventional economics. | `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`; `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` |
| Bear | Revenue growth (stage 1) | -1.0% | -2.0% | Added deeper downside to reflect legal overhang and potential slower demand/pricing recovery. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/reports/2026-02-12/third-party-sources.md` (TP-1, TP-2, TP-3) |
| Bear | FCF margin (stage 1) | 5.0% | 4.25% | Lowered for stress under weaker pricing and higher fixed-cost absorption risk. | `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md` |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| Base | $103.32 | $83.05 | -$20.27 | 25.2% | 0.6% | -24.6 pts |
| Bull | $184.19 | $141.72 | -$42.47 | 123.2% | 71.7% | -51.5 pts |
| Bear | $51.83 | $40.48 | -$11.35 | -37.2% | -51.0% | -13.8 pts |

(Source: `companies/US/CALM/reports/2026-02-07/valuation/outputs.json`; `companies/US/CALM/reports/2026-02-12/valuation/outputs.json`)

## Corporate-Action Sweep Delta
- No signed or proposed take-private/merger proxy filings were found in the required historical SEC sweep (`PREM14A`, `DEFM14A` both zero). (Source: `companies/US/CALM/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`)
- 8-K activity was dominated by recapitalization mechanics, secondary-offering/repurchase execution, and acquisition close disclosures; no event-risk valuation cap was applied. (Source: `companies/US/CALM/data/filings/historical/8-K-2025-03-27-0001562762-25-000058.md`; `companies/US/CALM/data/filings/historical/8-K-2025-04-17-0001213900-25-032989.md`; `companies/US/CALM/data/filings/historical/8-K-2025-06-02-0001562762-25-000156.md`)

## What Did Not Change (and Why)
- **Model type** remained `three-stage-dcf-fade` because CALM is still best valued on through-cycle cash generation, not book-value residual income. (Source: `companies/US/CALM/reports/2026-02-07/valuation/inputs.yaml`; `.agents/skills/run-llm-workflow/references/valuation-method.md`)
- **Capital-structure treatment** remained net-cash supportive since CALM reported substantial cash/investments and no funded revolver borrowings. (Source: `companies/US/CALM/data/filings/10-Q-2026-01-07-0001562762-26-000004.md`; `companies/US/CALM/data/filings/10-K-2025-07-22-0001562762-25-000170.md`)
- **Verdict label** stayed `Watch`, but with lower conviction and less valuation cushion at current price. (Source: `companies/US/CALM/reports/2026-02-07/report.md`; `companies/US/CALM/reports/2026-02-12/valuation/outputs.json`)
