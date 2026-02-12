# TTD Deep-Dive Changes

- Ticker: `TTD`
- Revised as-of date: `2026-02-12`
- Baseline package: `companies/US/TTD/reports/2026-02-08`
- Revised output package: `companies/US/TTD/reports/2026-02-12`

## Verdict Delta
| Item | Baseline (2026-02-08) | Revised (2026-02-12) | Delta |
| --- | --- | --- | --- |
| Verdict | Attractive | Watch | Downgraded after downside-falsification pass |
| Base value/share | $33.48 | $24.96 | -$8.52 |
| Base MOS vs $27.04 | +23.8% | -7.7% | -31.5 pts |

## Assumption Delta (Evidence-Backed)
| Scenario | Input | Baseline | Revised | Why Changed | Evidence |
| --- | --- | --- | --- | --- | --- |
| Base | `revenue_growth_stage1` | 10.0% | 8.5% | Client spend is explicitly non-committed/terminable and CTV-led demand is acknowledged as evolving and macro-sensitive; external data indicates growth remains positive but decelerating/cyclical. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-K-2025-02-21-0001671933-25-000029.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/historical/10-K-2023-02-15-0001671933-23-000007.md; /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/third-party-sources.md |
| Base | `fcf_margin_stage1` | 23.0% | 21.5% | Platform operations and hosting costs rose faster than revenue in 2025 YTD and SBC burden remains structurally high versus OCF. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-Q-2025-11-06-0001671933-25-000144.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/financial_statements/annual/cash_flow_statement.csv |
| Base | `discount_rate` | 9.5% | 10.0% | Added execution/governance risk premium due CFO transition plus governance-related exchange reprimand history and persistent regulatory complexity. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/8-K-2026-01-26-0001193125-26-021804.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/8-K-2025-12-15-0001671933-25-000148.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-K-2025-02-21-0001671933-25-000029.md |
| Base | `terminal_growth` | 3.0% | 2.5% | Long-run growth moderated due mature programmatic dynamics, concentration pressure, and pricing/take-rate caution in filings. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-K-2025-02-21-0001671933-25-000029.md; /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/third-party-sources.md |
| Base | `fcf_margin_terminal` | 18.0% | 16.5% | Margin durability haircut reflects recurring infra/people investment intensity and competitive/pricing pressure signals. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-Q-2025-11-06-0001671933-25-000144.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/third_party/PUBM-10Q-latest.md |
| Bull | Growth/margin/rate set | 12.0% / 25.0% / 9.0% | 11.0% / 24.5% / 9.3% | Bull still assumes strong execution, but deep-dive evidence supports a modest risk premium and slightly lower sustained growth confidence. | /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/third-party-sources.md; /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/10-K-2025-02-21-0001671933-25-000029.md |
| Bear | Growth/margin/rate set | 6.0% / 19.0% / 10.5% | 4.5% / 17.0% / 11.0% | Bear reflects stronger downside in a macro + privacy + pricing stress path. | /Users/chad/source/chadwin-codex/companies/US/TTD/data/filings/historical/10-K-2023-02-15-0001671933-23-000007.md; /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/third-party-sources.md |

## Valuation Output Delta
| Scenario | Prior Value/Share | Revised Value/Share | Delta | Prior MOS | Revised MOS | MOS Delta |
| --- | --- | --- | --- | --- | --- | --- |
| Base | $33.48 | $24.96 | -$8.52 | +23.8% | -7.7% | -31.5 pts |
| Bull | $46.42 | $38.66 | -$7.76 | +71.7% | +43.0% | -28.7 pts |
| Bear | $17.78 | $14.01 | -$3.77 | -34.3% | -48.2% | -13.9 pts |

## What Did Not Change and Why
- Valuation framework remained `three-stage-dcf-fade` because TTD remains an operating business where revenue/FCF dynamics are decision-useful.
- Base-year anchors (`revenue`, `net_debt` as net cash proxy, diluted share base) were not changed because no post-FY2024 annual restatement exists in the local data package.
- Current price input remained `$27.04` to stay aligned with the latest local company profile snapshot used by this repo workflow.

Sources:
- /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-08/valuation/inputs.yaml
- /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-08/valuation/outputs.json
- /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/valuation/inputs.yaml
- /Users/chad/source/chadwin-codex/companies/US/TTD/reports/2026-02-12/valuation/outputs.json
- /Users/chad/source/chadwin-codex/companies/US/TTD/data/company_profile.csv
