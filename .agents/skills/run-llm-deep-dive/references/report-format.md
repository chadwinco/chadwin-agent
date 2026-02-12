# Deep-Dive Report Format

Use this structure for:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md`

The goal is to communicate what changed after deeper, downside-focused research.

```markdown
# {Company Name} ({TICKER}) Deep-Dive Revision

_As of {YYYY-MM-DD} (Baseline package: {BASELINE_REPORT_DIR})_

## Executive Delta
- Prior verdict: Attractive | Watch | Avoid
- Revised verdict: Attractive | Watch | Avoid
- Prior base value: ${...}/share
- Revised base value: ${...}/share
- Prior current price: ${...}
- Revised current price input: ${...}
- Base MOS change: ...%

2-4 bullets on the most decision-changing evidence from this deep dive.

## Thesis-Breaker Review
| Hypothesis | Baseline Assumption | New Evidence | Status (Holds/Weakened/Broken) | Value Impact |
| --- | --- | --- | --- | --- |
| | | | | |

## Revised Financial and Valuation View
| Scenario | Key Assumptions (Revised) | Value/Share (Revised) | Prior Value/Share | Delta |
| --- | --- | --- | --- | --- |
| Base | | | | |
| Bull | | | | |
| Bear | | | | |

One short paragraph explaining why revised assumptions changed (or stayed unchanged).

## Residual Risks and Monitoring Signals
List 3-5 risks that remain open after this deep dive.
For each, include one disconfirming signal to track.

## Conclusion
2-3 sentences with a clear action at current price and confidence level after deep research.
```

## Companion Delta File
Also write:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/deep-dive-changes.md`

That file should include assumption-by-assumption change traceability with explicit citations.
