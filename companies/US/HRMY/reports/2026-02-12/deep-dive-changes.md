# Deep-Dive Changes vs Baseline

_Ticker: HRMY | Revised as-of: 2026-02-12 | Baseline: 2026-02-11_

## Verdict Delta
- Baseline verdict: Attractive
- Revised verdict: Watch
- Why it changed: The deep dive reduced confidence in HRMY's long-run durability despite still-strong near-term demand. The largest valuation changes came from (1) stronger-than-assumed competitive momentum in sleep-wake peers, (2) evidence that royalty burden is structurally rising with scale, and (3) persistent concentration/pipeline timing risk that limits diversification confidence. (sources: chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md, chadwin-codex/companies/US/HRMY/data/filings/historical/10-Q-2024-10-29-0001558370-24-013803.md, chadwin-codex/companies/US/HRMY/data/filings/10-K-2025-02-25-0001558370-25-001441.md, chadwin-codex/companies/US/HRMY/reports/2026-02-12/third-party-sources.md)

## Assumption Deltas
| Assumption | Baseline | Revised | Why Changed | Sources |
| --- | --- | --- | --- | --- |
| Stage-1 revenue growth (base) | 6.0% | 4.8% | Near-term guidance remains strong, but deep-dive evidence supports lower medium-term durability due single-product concentration and strong peer growth in overlapping indications. | `chadwin-codex/companies/US/HRMY/reports/2026-02-12/third-party-sources.md`, `chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md` |
| Stage-1 FCF margin (base) | 22.0% | 19.2% | Cost-of-sales ratio rose in 2024 and 2025 as higher royalty tiers were triggered; legal/professional and R&D intensity also increased. | `chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md`, `chadwin-codex/companies/US/HRMY/data/filings/historical/10-Q-2024-10-29-0001558370-24-013803.md` |
| Discount rate (base) | 10.5% | 10.9% | Added risk premium for concentration (single product / concentrated channel / single API source) and unresolved litigation/pipeline uncertainty. | `chadwin-codex/companies/US/HRMY/data/filings/10-K-2025-02-25-0001558370-25-001441.md`, `chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md` |
| Terminal growth (base) | 2.2% | 2.0% | Terminal confidence reduced due eventual patent/litigation overhang and higher probability of category-share pressure in narcolepsy/IH. | `chadwin-codex/companies/US/HRMY/data/filings/10-K-2025-02-25-0001558370-25-001441.md`, `chadwin-codex/companies/US/HRMY/reports/2026-02-12/third-party-sources.md` |
| Terminal FCF margin (base) | 18.0% | 15.8% | Deep dive increased confidence that royalty and competitive pressures can keep steady-state economics below baseline normalization. | `chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md`, `chadwin-codex/companies/US/HRMY/data/filings/historical/10-Q-2024-10-29-0001558370-24-013803.md`, `chadwin-codex/companies/US/HRMY/reports/2026-02-12/third-party-sources.md` |

## Valuation Output Deltas
| Scenario | Baseline Value/Share | Revised Value/Share | Delta | MOS Delta |
| --- | --- | --- | --- | --- |
| Base | $48.33 | $38.59 | -$9.74 | -25.7 pts |
| Bull | $82.84 | $59.71 | -$23.13 | -61.0 pts |
| Bear | $31.34 | $24.66 | -$6.68 | -17.6 pts |

## No-Change Items
- Balance-sheet downside buffer remains meaningful: HRMY still carries substantial net cash and low near-term refinancing stress, so the deep dive did not require a distressed-capital structure treatment. (sources: chadwin-codex/companies/US/HRMY/data/filings/10-Q-2025-11-04-0001104659-25-105962.md, chadwin-codex/companies/US/HRMY/data/financial_statements/quarterly/balance_sheet.csv)
- Model structure stayed a three-stage DCF because business economics are still better represented via long-run cash generation than a balance-sheet residual-income framework. (sources: chadwin-codex/companies/US/HRMY/reports/2026-02-12/valuation/inputs.yaml, chadwin-codex/.agents/skills/run-llm-workflow/references/valuation-method.md)
