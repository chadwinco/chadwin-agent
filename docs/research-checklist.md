# Research Checklist

## Data Integrity
- [ ] Required CSVs exist and load without errors.
- [ ] Fiscal years align across income, balance sheet, and cash flow.
- [ ] No missing or obviously incorrect values in key fields.

## Evidence Discipline
- [ ] No verbatim copying from filings or transcripts.
- [ ] All factual claims cite local file paths (or external sources in `docs/source-log.md`).
- [ ] Claims are supported by the latest available filings or transcripts.

## Financial Quality
- [ ] Revenue growth trend is quantified (CAGR + year-over-year).
- [ ] EBIT margin trend is described with data.
- [ ] FCF margin and cash conversion are analyzed.
- [ ] ROIC is calculated and compared to cost of capital.
- [ ] Leverage and liquidity are evaluated (net debt, net debt/EBITDA).

## Business Quality
- [ ] Competitive position described with evidence.
- [ ] Unit economics or operational drivers are identified.
- [ ] Capital allocation history is documented.

## Growth & Risks
- [ ] Growth drivers separated into organic, pricing, mix, and M&A.
- [ ] Top 3–5 risks prioritized by impact on cash generation.

## Valuation
- [ ] Base/bull/bear assumptions are explicit and defensible.
- [ ] DCF output reconciles to current price.
- [ ] Margin of safety is calculated and discussed.

## Output
- [ ] Executive summary is concise and decision-oriented.
- [ ] Assumptions summary is included and matches `assumptions.yaml`.
- [ ] Sources are logged in `docs/source-log.md` when external data is used.
- [ ] Improvement notes added to `docs/improvement-log.md`.
