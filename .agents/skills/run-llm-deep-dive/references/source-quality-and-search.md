# Source Quality and Search Discipline

This deep-dive skill is evidence quality constrained. Search breadth does not replace source quality.

## 1. Source Priority

Use this order when evaluating third-party sources:

1. Primary official sources (highest priority)
- SEC/EDGAR filings
- Regulator publications
- Court filings / legal dockets
- Official company counterparties (major customer/supplier filings)

2. High-quality secondary sources
- Industry bodies and audited industry datasets
- Credit rating agency reports/updates
- Established research/data providers with clear methodology

3. Tertiary context sources (use sparingly)
- Reputable financial press for event context
- Executive interviews only when cross-checked elsewhere

Avoid or heavily discount:
- Anonymous posts, promotional blogs, unsourced social media claims
- AI-generated summaries without primary citations
- Sources with unclear publication dates

## 2. Falsification-Driven Query Design

For each top hypothesis, define:
- `Question`: what would prove this assumption wrong?
- `Evidence needed`: which objective datapoints should move?
- `Target domains`: where high-quality evidence is likely to exist

Example patterns:
- `"company name" + "customer concentration" + "10-K"`
- `"industry metric" + "2024 OR 2025" + "association report"`
- `"company name" + "covenant" + "credit agreement"`
- `"company name" + "litigation" + "complaint OR settlement"`

Use narrow, purpose-built queries. Avoid generic "is this company good?" style prompts.

## 3. Recency and Independence Rules

- Use only evidence dated on or before revised as-of date.
- For any material external claim, seek at least two independent sources when feasible.
- If sources conflict, record both and explain resolution logic.
- Explicitly flag claims with single-source support.

## 4. External Source Log (Required)

Write:
- `companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<YYYY-MM-DD>/third-party-sources.md`

Minimum table:

```markdown
| Hypothesis | Claim Tested | Source | URL | Published | Accessed | Quality Tier | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |
```

## 5. Claim-Citation Rule

- Final report claims must cite local file paths.
- For external claims, cite:
  - local source log path (`third-party-sources.md`)
  - and the specific URL entry in that file

This keeps the final package auditable.
