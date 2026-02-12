# TTD Deep-Dive Plan (Original)

- Ticker: `TTD`
- Exchange/Country: `US`
- Revised as-of date: `2026-02-12`
- Baseline report directory: `companies/US/TTD/reports/2026-02-08`
- Output directory: `companies/US/TTD/reports/2026-02-12`

## Prioritized Thesis-Breakers
| Hypothesis | Downside Impact (1-5) | Prob. Baseline Wrong (1-5) | Evidence Gap (1-5) | Severity Score |
| --- | --- | --- | --- | --- |
| Privacy/identity changes structurally reduce targeting efficacy and take-rate durability | 5 | 4 | 4 | 80 |
| Revenue growth is more cyclical than baseline assumes because client spend is non-committed and CTV demand can normalize | 5 | 3 | 3 | 45 |
| Platform cost intensity (hosting + SBC) compresses sustainable FCF margin versus baseline | 5 | 4 | 3 | 60 |
| Buybacks fail to fully offset dilution and consume optionality during volatility | 4 | 3 | 2 | 24 |
| Governance/execution shocks (CFO transition, governance scrutiny) warrant higher required return | 3 | 3 | 3 | 27 |

## Falsification Workplan
| Hypothesis | Falsification Question | Evidence Needed | Target Sources | Pass/Fail Threshold |
| --- | --- | --- | --- | --- |
| Privacy/identity pressure | Are independent ad platforms losing signal quality and monetization power due privacy/OS/browser/regulatory changes? | Confirmed disclosures on signal degradation, consent/opt-out friction, and monetization effects | Local: TTD 10-K/10-Q. External: META 10-K, GOOGL 10-K, PUBM 10-Q, source log | Fail if multiple independent filings indicate persistent signal constraints with explicit revenue/efficacy impact and no offsetting mitigation disclosure. |
| Demand durability / CTV reliance | Does baseline overstate durable growth given non-committed MSAs and evolving CTV demand? | Contract terms, revenue concentration mechanics, macro ad sensitivity, independent CTV demand evidence | Local: TTD 10-K/10-Q/historical 10-Ks. External: ROKU 10-Q, MAGNA, IAB | Fail if evidence shows weak spend visibility plus macro-sensitive ad budgets and no hard contractual floor. |
| Margin durability | Are TTD cash margins at risk from rising infrastructure and compensation intensity? | Platform ops/hosting trend, SBC burden vs OCF and revenue, evidence of competitive pricing pressure | Local: TTD 10-Q, annual financial statements, historical filings. External: peer filings for pricing pressure | Fail if cost intensity grows faster than revenue and structural expense drivers are recurring. |
| Capital allocation quality | Do repurchases protect per-share value or mainly offset SBC while reducing liquidity? | Buyback authorization/use, diluted share trend, SBC/OCF ratio | Local: TTD 10-K/10-Q, annual statements | Fail if diluted share count remains up while SBC stays high and buybacks reduce strategic cash optionality. |
| Governance/execution | Are governance events likely to raise operating/valuation risk? | CFO transition details, exchange reprimand/governance events, legal/governance references | Local: TTD 8-Ks and 10-K risk/legal sections | Fail if multiple governance events occur in short succession with unresolved leadership transition. |

## Planned Evidence Sequence
1. Reconcile baseline assumptions and identify which are most fragile under downside tests.
2. Run local evidence pass: contract structure, growth/margin history, cost drivers, liquidity and dilution.
3. Run targeted third-party pass: peer filings + high-quality industry bodies for independent triangulation.
4. Apply explicit assumption changes only where pass/fail thresholds fail.
5. Recompute valuation and document every assumption delta with source traceability.
