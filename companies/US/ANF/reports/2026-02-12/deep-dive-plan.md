# ANF Deep-Dive Research Plan

_As of 2026-02-12 | Baseline report date: 2026-02-12_

## Objective
Test whether ANF's positive baseline thesis can fail under a tariff + mix + regional execution stress case severe enough to erase most of the valuation gap.

## Prioritized Falsification Hypotheses
| Priority | Hypothesis | Downside Impact (1-5) | Probability Baseline Is Wrong (1-5) | Evidence Gap (1-5) | Priority Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Tariff and input-cost pressure persists through 2026, compressing normalized margins below baseline assumptions. | 5 | 4 | 2 | Q3 and YTD margin pressure already visible; key driver of valuation downside. |
| 2 | Growth quality is over-dependent on Hollister while Abercrombie remains weak, lowering consolidated growth durability. | 4 | 4 | 2 | Brand divergence widened in FY2025 YTD. |
| 3 | APAC expansion remains subscale with worsening losses, reducing international growth contribution and raising restructuring risk. | 4 | 3 | 3 | APAC losses worsened year to date; need through-cycle check with older filings. |
| 4 | Capital returns remain aggressive while cash generation is pressured by inventory/product costs, reducing downside buffer. | 3 | 3 | 2 | Buybacks remain large despite lower cash balance and tariff uncertainty. |

## Workplan
| Hypothesis | Falsification Question | Evidence Needed | Planned Sources | Pass/Fail Threshold | Status |
| --- | --- | --- | --- | --- | --- |
| Tariff margin pressure | Is recent margin compression mostly temporary, or does it require lower long-run FCF margins? | Quantified tariff bps, COGS deleverage, management 2026 mitigation cadence | `companies/US/ANF/data/filings/10-Q-2025-12-05-0001018840-25-000048.md`; `companies/US/ANF/data/filings/earnings-call-2026-01-22-news.alphastreet.com.md`; `companies/US/ANF/reports/2026-02-12/third-party-sources.md` | Fail baseline if tariff/cost pressure is >100 bps beyond FY2025 and no full offset is evidenced | Completed |
| Brand mix durability | Can consolidated growth hold if Hollister cools before Abercrombie re-accelerates? | Brand-level and comp trends, AUR/volume mix commentary | `companies/US/ANF/data/filings/10-Q-2025-12-05-0001018840-25-000048.md`; `companies/US/ANF/data/filings/earnings-call-2026-01-22-news.alphastreet.com.md`; `companies/US/ANF/reports/2026-02-12/third-party-sources.md` | Fail baseline if one-brand concentration remains and Abercrombie remains negative into next planning window | Completed |
| APAC economics | Is APAC likely to be value-accretive in the medium term? | Segment sales/operating loss trend across recent and historical filings | `companies/US/ANF/data/filings/10-Q-2025-12-05-0001018840-25-000048.md`; `companies/US/ANF/data/filings/historical/historical-filings-fetch-report-2026-02-12.json`; `companies/US/ANF/data/filings/historical/10-Q-2025-09-05-0001018840-25-000045.md` | Fail baseline if APAC loss rate worsens while management still needs growth investment | Completed |
| Capital allocation resilience | Does buyback pace reduce balance-sheet optionality under downside scenarios? | Cash/liquidity trajectory, buyback pace, operating cash flow pressure factors | `companies/US/ANF/data/filings/10-Q-2025-12-05-0001018840-25-000048.md`; `companies/US/ANF/data/filings/earnings-call-2026-01-22-news.alphastreet.com.md` | Fail baseline if net cash cushion trends down materially while margin risk remains elevated | Completed |
