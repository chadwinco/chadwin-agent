# Research Checklist

## Scope and Data
- [ ] Ticker and as-of date are explicit.
- [ ] Required local files exist and load without errors.
- [ ] Latest filing/transcript evidence used is dated on or before the as-of date.

## Evidence Discipline
- [ ] No verbatim copying from filings or transcripts.
- [ ] Every factual claim cites local file paths.
- [ ] External sources are logged in `docs/source-log.md`.

## Thesis Quality
- [ ] Thesis explains why returns can persist and what can break the thesis.
- [ ] Competitive position is described with evidence.
- [ ] Capital allocation quality is assessed.

## Financial Quality
- [ ] Revenue trend is quantified (CAGR plus recent year-over-year change).
- [ ] EBIT and FCF margin trends are quantified.
- [ ] ROIC proxy and leverage are evaluated.

## Valuation Quality
- [ ] Base/bull/bear assumptions are explicit and defensible.
- [ ] Assumptions are written to `valuation/inputs.yaml`.
- [ ] Valuation outputs are written to `valuation/outputs.json`.
- [ ] Margin of safety reconciles with current price and value per share.

## Output Quality
- [ ] Report is concise (target: 500-900 words) and decision-oriented.
- [ ] Top 3-5 risks are prioritized by cash-flow impact.
- [ ] Conclusion states a clear action at current price.
- [ ] Improvement notes are added to `docs/improvement-log.md`.
