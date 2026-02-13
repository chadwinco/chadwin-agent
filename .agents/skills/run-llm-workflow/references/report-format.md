# Report Format

Use this structure for `.chadwin-data/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/report.md`.
Keep it concise, decision-oriented, and narrative-first.

Default house style (when report preferences are empty):
- Write tight prose that explains the investment argument, not a checklist of facts.
- Keep bullets limited to decision metrics and risk monitor items.
- For each major section, explicitly connect `claim -> evidence -> valuation implication`.
- Spend depth on 3-5 valuation pillars; avoid broad low-impact fact dumps.
- Do not repeat basic company facts unless they change scenario assumptions or confidence.

If `.chadwin-data/user_preferences.json` exists, prioritize `report_preferences.must_include`, then `nice_to_have`, and avoid items listed in `report_preferences.exclude` unless required for analytical integrity.

```markdown
# {Company Name} ({TICKER}) Investment Snapshot

_As of {YYYY-MM-DD}_

## Investment Summary
- Verdict: Attractive | Watch | Avoid
- Base intrinsic value: ${...}/share
- Bull/Bear range: ${...} to ${...}/share
- Current price: ${...}
- Margin of safety (base): ...%

One tight paragraph that states:
- the core thesis in plain language,
- what changed conviction most in this run,
- the biggest remaining uncertainty,
- and why the base MOS is or is not decision-credible.

## Valuation Pillars (What Must Be True)
Write 3-5 short subsections with headings like:
### Pillar 1: {short name}

Each pillar subsection must:
- state what must be true for intrinsic value to hold,
- summarize the best supporting and disconfirming evidence,
- map directly to model inputs (growth, margin, discount/cost of equity, terminal/fade),
- explain directional impact on value/share or MOS if the pillar weakens.

Use prose, not bullet fragments, for pillar analysis.

## Market-Implied Expectations (Analyst Anchor)
| Signal | Current Read | Implication for Base Case |
| --- | --- | --- |
| Consensus stance / analyst count | | |
| Revenue outlook dispersion | | |
| EPS and forward P/E path | | |
| Price target range and median | | |
| Recent ratings/target revisions | | |

One short paragraph: where your base case aligns with consensus and where it intentionally differs, with explicit rationale.

## Business and Competitive Position
2-3 short paragraphs on how the company makes money, why returns may persist, and where the model is vulnerable.
Close with one sentence that links business-position evidence to valuation durability (or fragility).

## Financial Quality
| Metric | Latest | 3-5Y Trend | Comment |
| --- | --- | --- | --- |
| Revenue / premium / fee growth | | | |
| Operating profitability (EBIT or pre-tax margin) | | | |
| Cash generation (FCF or operating-cash proxy) | | | |
| Returns metric (ROIC or ROE proxy) | | | |
| Leverage / capital adequacy | | | |

After the table, add one short paragraph explaining which metric most supports the thesis and which metric is the first likely break signal.

## Key Issue Resolution and Falsification
Start with one short paragraph on how the highest-impact issues were tested this run and which assumptions changed (or did not).

| Issue | Why It Matters | Resolution Status (Resolved/Bounded/Open) | Evidence | Valuation Impact |
| --- | --- | --- | --- | --- |
| | | | | |

## Valuation
| Scenario | Core Assumptions | Discount / Cost of Equity | Terminal Assumption | Value/Share | MOS vs Price |
| --- | --- | --- | --- | --- | --- |
| Base | | | | | |
| Bull | | | | | |
| Bear | | | | | |

Add 2 short paragraphs:
- Paragraph 1: how pillar evidence translated into base assumptions (why these are central, not optimistic).
- Paragraph 2: what must happen for bull case and what drives bear case.

If using DCF, call out growth/margin durability and fade.
If using residual income, call out ROE sustainability versus cost of equity and capital constraints.

## Key Risks and Disconfirming Signals
List top 3-5 risks by impact on cash generation.
For each risk, write 1-2 sentences:
- mechanism of damage to intrinsic value,
- concrete disconfirming signal that would invalidate or materially weaken the thesis.

## Conclusion
3-4 sentences with a clear call at the current price:
- whether the current MOS is sufficient for action,
- what evidence would most likely change the call,
- whether any thesis-critical uncertainty remains open.

## Research Stop Gate
- Thesis confidence: 0-100%
- Highest-impact levers: <count>
- Levers resolved: <count>
- Open thesis-critical levers: <count>
- Diminishing returns from additional research: Yes | No
- Research complete: Yes | No
- Next best research focus: <lever or "None">

One short paragraph on why additional research is (or is not) likely to change the decision materially.
Keep this paragraph as plain prose (not `Key: Value` format) so follow-up routing parsers only read the bullet fields above.
```
