# EdgarTools Data Catalog (Wrapper Scope)

As of 2026-02-18, this is the complete data surface this skill treats as fetchable.

Contract rule: if the installed `edgar` module can fetch it, this skill can fetch it via `scripts/edgartools_wrapper.py` using `call`/`read` steps.

Primary docs:
- https://edgartools.readthedocs.io/en/latest/api/filings/
- https://edgartools.readthedocs.io/en/latest/api/filing/
- https://edgartools.readthedocs.io/en/latest/api/company/
- https://edgartools.readthedocs.io/en/latest/api/entity-facts-reference/
- https://edgartools.readthedocs.io/en/latest/data-objects/
- https://edgartools.readthedocs.io/en/latest/insider-filings/
- https://edgartools.readthedocs.io/en/latest/guides/current-filings/

## 1) Global Filing Discovery (All Form Types)

Fetchable data:
- Historical SEC filing index and filing metadata across all forms using `get_filings(...)`.
- Real-time filing stream using `get_current_filings(...)`.
- Filing lookup by accession (`get_by_accession_number(...)`) and search (`find(...)`).

Filtering dimensions (docs + API):
- form(s)
- filing date/date range
- year/quarter
- amendments include/exclude
- accession number
- ticker/CIK (via filtering on collections)

Collection operations available on `Filings`/`CurrentFilings`:
- `latest`, `head`, `tail`, `sample`, `filter`
- pagination with `next` / `previous`
- export helpers (for example `to_pandas`) where provided by edgartools

## 2) Single Filing Content, Metadata, and Attachments

Fetchable data from a `Filing`:
- Core metadata: form, filing date, accession number, company/entity identifiers, SEC links.
- Body formats: `html()`, `text()`, `markdown()`, `xml()`.
- Filing attachments/exhibits via `filing.attachments`.
- Structured sections/search APIs where provided by filing type.
- XBRL handle for XBRL-capable filings via `filing.xbrl()`.

This skill also exposes attachment-aware markdown extraction via `helpers.filing_markdown(...)`.

## 3) Structured Filing Data Objects (`filing.obj()`)

From filing data object docs and filing-type guides, the following form families have structured parsing support.

Core objects (explicitly documented):
- `10-K` -> `TenK`
- `10-Q` -> `TenQ`
- `8-K` -> `EightK`
- `20-F` -> `TwentyF`
- `13F-HR` -> `ThirteenF`
- `3`, `4`, `5` -> Ownership objects (`Form3` / `Form4` / `Form5`)
- `SC 13D`, `SC 13G` -> `Schedule13D`
- `DEF 14A` -> `ProxyStatement`
- `144` -> `Form144`
- `D` -> `FormD`
- `C`, `C-U`, `C-AR`, `C-TR` -> `FormC`
- `MA-I` -> `MunicipalAdvisorForm`
- `10-D` -> `TenD`
- `N-PX` -> fund voting report object (guide uses `filing.obj()`)
- `NPORT-P` -> `FundReport`
- `N-MFP2` -> `MoneyMarketFundReport`
- `N-CEN` -> structured census object (fund census guide)

Additional filing-type guides in current docs include:
- 13F holdings
- Ownership (Forms 3/4/5)
- Schedule 13D/G
- Form 144
- 8-K
- 10-K
- 10-Q
- 20-F
- 6-K
- DEF 14A
- Form D
- Form C
- N-PORT
- N-MFP
- N-CEN
- N-PX
- ABS-EE
- 10-D
- MA-I

For forms without a dedicated data object, filings are still fetchable as raw filing content + attachments.

## 4) Company / Entity Data

From `Company` / entity APIs, fetchable data includes:
- Company/entity profile identifiers (ticker, CIK, names, SIC/industry when available).
- Company filing history (`company.get_filings(...)`, `company.latest(...)`).
- Company financial statement accessors (`get_financials`, `get_quarterly_financials`, statement helpers where supported).
- Company facts endpoint (`company.get_facts()`).

## 5) Entity Facts (XBRL Fact Store)

From Entity Facts API:
- Raw fact collection for a company/entity.
- Query builder filtering by:
  - concept / label / text
  - fiscal year / fiscal period
  - period length
  - date range / as-of
  - form type
  - statement type
  - quality/confidence dimensions (where available)
- Query outputs to tabular forms (`to_dataframe` and related helpers).

## 6) XBRL Data

Fetchable XBRL data:
- Single-filing XBRL via `filing.xbrl()`.
- Multi-filing stitched XBRL views via `XBRLS.from_filings(...)`.
- Statement-level outputs (income, balance sheet, cash flow, and related statement families supported by filing).
- Statement/fact exports to DataFrame.

## 7) Ownership / Insider Trading Data (Form 3/4/5)

From Ownership docs:
- Insider identity and issuer metadata.
- Non-derivative and derivative transactions.
- Holdings and transaction summaries.
- DataFrame exports from ownership objects (for example detailed Form 4 transaction tables).

## 8) Fund and Specialized Regulatory Data

Via filing-type guides and object parsing support, fetchable categories include:
- Investment manager holdings (`13F-HR`)
- Beneficial ownership (`SC 13D/G`)
- Proxy voting (`N-PX`)
- Fund portfolio reporting (`N-PORT`)
- Money market fund reporting (`N-MFP`)
- Fund census reporting (`N-CEN`)
- Asset-backed securities distribution (`10-D`) and ABS asset-level feeds (`ABS-EE`)
- Municipal advisor registration (`MA-I`)

## 9) Local Data / Bulk Download Surface

From local data docs, edgartools also supports downloading local datasets (for example submissions/facts/attachments/reference data) when configured. If this is required, it is still in scope for this skill because wrapper calls can invoke those APIs.

## Practical Interpretation for This Skill

"All data available" means:
- Any form type EDGAR filing metadata/content.
- Any attachments/exhibits from those filings.
- Any structured object returned by `filing.obj()` in installed edgartools.
- Any company/entity/facts/XBRL data exposed by installed edgartools APIs.

When docs and installed package differ, installed package behavior is authoritative at runtime.
