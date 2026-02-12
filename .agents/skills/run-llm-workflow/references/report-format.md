# Report Format

Use this structure for `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md`. Keep it concise and decision-oriented.
If `preferences/user_preferences.json` exists, prioritize `report_preferences.must_include`, then `nice_to_have`, and avoid items listed in `report_preferences.exclude` unless required for analytical integrity.

```markdown
# {Company Name} ({TICKER}) Investment Snapshot

_As of {YYYY-MM-DD}_

## Investment Summary
- Verdict: Attractive | Watch | Avoid
- Base intrinsic value: ${...}/share
- Bull/Bear range: ${...} to ${...}/share
- Current price: ${...}
- Margin of safety (base): ...%

2-4 bullets on the core thesis and biggest uncertainty.

## Business and Competitive Position
1-2 short paragraphs on how the company makes money, why returns can persist, and where the model is vulnerable.

## Financial Quality
| Metric | Latest | 3-5Y Trend | Comment |
| --- | --- | --- | --- |
| Revenue / premium / fee growth | | | |
| Operating profitability (EBIT or pre-tax margin) | | | |
| Cash generation (FCF or operating-cash proxy) | | | |
| Returns metric (ROIC or ROE proxy) | | | |
| Leverage / capital adequacy | | | |

## Valuation
| Scenario | Core Assumptions | Discount / Cost of Equity | Terminal Assumption | Value/Share | MOS vs Price |
| --- | --- | --- | --- | --- | --- |
| Base | | | | | |
| Bull | | | | | |
| Bear | | | | | |

One short paragraph on what must happen for bull case and what drives bear case. If using DCF, call out growth/margin durability and fade. If using residual income, call out ROE sustainability versus cost of equity and capital constraints.

## Key Risks and Disconfirming Signals
List top 3-5 risks by impact on cash generation.
Include one sentence for each risk on what evidence would invalidate the thesis.

## Conclusion
2-3 sentences with a clear call at the current price.
```
