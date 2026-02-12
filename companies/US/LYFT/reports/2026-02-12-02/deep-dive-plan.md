# LYFT Deep-Dive Plan

_As of 2026-02-12 | Baseline package: 2026-02-12-01 | Revised package: 2026-02-12-02_

## Objective
Explain the February 11-12, 2026 analyst re-rating wave and test whether those reasons break the prior deep-dive thesis.

## Prioritized Thesis-Breaker Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Falsification Question | Pass/Fail Threshold |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Near-term margin expansion continues smoothly in 2026 | 5 | 4 | 2 | Did Q1 guidance and post-print analyst work materially reduce confidence in margin trajectory? | Fail if guidance implies flat-to-weaker near-term margin vs prior expectations and analysts broadly reset targets lower. |
| 2 | Demand growth quality is durable without promo dependence | 4 | 3 | 3 | Are rides/gross bookings trends still strong enough after Q4 promotional intensity concerns? | Fail if ride growth or Q1 setup indicates material deceleration not offset by mix. |
| 3 | Competitive and AV pressure is manageable in core markets | 4 | 3 | 3 | Are analysts now discounting LYFT due to AV/competitive share risk more than previously modeled? | Fail if multiple independent sources cite AV/competition as a primary reason for lower targets and local filings support low-switching-cost risk. |
| 4 | International expansion will be value-accretive on a risk-adjusted basis | 3 | 3 | 4 | Is FreeNow/TBR expansion likely to improve economics soon enough to offset core risks? | Fail if evidence points to prolonged execution drag without clear margin contribution. |
| 5 | Event-risk cap is low (no hidden corporate-action overhang) | 3 | 2 | 1 | Is there signed/proposed take-private/M&A/tender-process risk that caps upside or changes downside? | Fail if PREM14A/DEFM14A or 8-K evidence shows active transaction process requiring event-risk overlays. |

## Evidence Collection Plan
1. Corporate-action sweep (required): run SEC historical pull for `8-K,PREM14A,DEFM14A` through 2026-02-12 and classify event-risk implications.
2. Local primary evidence pass:
- Q4/FY2025 8-K with attachments for disclosed Q1 guidance and one-time items.
- 2026 10-K risk disclosures on competition, switching costs, incentives, insurance, regulation.
- Earnings call transcript for promo intensity, AV-market commentary, and management stance on 2027 targets.
3. Targeted external pass (falsification-driven):
- StockAnalysis rating tape to quantify breadth of target resets.
- Reuters-syndicated and analyst-note coverage to isolate cited downgrade causes (margin guidance, demand quality, AV/competition, execution risk).
4. Assumption update rules:
- Change growth/margin/discount assumptions only if evidence directly maps to a valuation driver.
- Keep base-year anchors unchanged unless new accounting data invalidates them.

## Decision Rules
- If hypotheses 1 and 2 are both failed, reduce base-case growth and near-term FCF margin assumptions and raise discount rate.
- If hypothesis 3 is failed, reduce terminal margin and/or raise discount rate to reflect persistent competitive intensity.
- If hypothesis 4 is only partially supported, cap bull-case upside and keep expansion upside optional, not core.
- If hypothesis 5 passes, do not apply takeout cap overlays.

## Planned Outputs
- `companies/US/LYFT/reports/2026-02-12-02/report.md`
- `companies/US/LYFT/reports/2026-02-12-02/valuation/inputs.yaml`
- `companies/US/LYFT/reports/2026-02-12-02/valuation/outputs.json`
- `companies/US/LYFT/reports/2026-02-12-02/deep-dive-changes.md`
- `companies/US/LYFT/reports/2026-02-12-02/third-party-sources.md`
