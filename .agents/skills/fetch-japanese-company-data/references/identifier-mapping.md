# Identifier Mapping (Japan)

## Accepted Formats
- 4-digit TSE code (example: `7974`)
- 5-digit JP code ending with `0` (example: `79740`)
- Yahoo symbol (`7974.T`)
- Seeded ISIN values

## Seeded Company Map
- Nintendo:
  - Canonical repo ticker: `79740`
  - TSE code: `7974`
  - Yahoo symbol: `7974.T`
  - ISIN: `JP3756600007`

## Extending The Map
Update `_SEEDED_COMPANIES` in `src/japan_fetch.py` when adding ISIN-first workflows or fixed canonical ticker aliases.
