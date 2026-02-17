# Source Quality and Targeted Search Discipline

Use this when local files cannot fully resolve a high-impact investment issue.

## 1. Source Priority
Use this source hierarchy:

1. Primary official sources (highest priority)
- SEC/EDGAR filings
- Regulator publications
- Court filings/legal dockets
- Official counterparty filings (major customers/suppliers)

SEC execution rule:
- For SEC retrieval, use the skill SEC helper scripts and configured identity. Do not use ad-hoc direct `sec.gov` HTTP calls.

2. High-quality secondary sources
- Industry bodies and audited industry datasets
- Credit rating agency reports/updates
- Established research/data providers with clear methods

3. Tertiary context sources (sparingly)
- Reputable financial press for event context
- Executive interviews only when cross-checked elsewhere

Avoid or heavily discount:
- Anonymous posts, promotional blogs, unsourced social claims
- AI summaries without primary citations
- Sources with unclear publication dates

## 2. Falsification-Driven Query Design
For each unresolved high-impact issue, define:
- `Question`: what would prove this assumption wrong?
- `Evidence needed`: what objective data would move?
- `Target domains`: where credible evidence is likely to exist

Use narrow, purpose-built queries. Avoid generic narrative searching.

## 3. Recency and Independence Rules
- Use only evidence dated on or before the run as-of date.
- For material external claims, seek at least two independent sources when feasible.
- If sources conflict, record both and explain resolution logic.
- Flag claims supported by only one source.

## 4. External Source Logging
When external sources materially affect assumptions, write:
- `<DATA_ROOT>/companies/<EXCHANGE_COUNTRY>/<TICKER>/reports/<REPORT_DATE_DIR>/third-party-sources.md`

Suggested table:

```markdown
| Issue | Claim Tested | Source | URL | Published | Accessed | Quality Tier | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |
```

## 5. Claim-Citation Rule
- Final report claims must cite local file paths.
- For external claims used in report conclusions, cite:
  - the local source log path (if created), and
  - the URL entry captured in that log.
