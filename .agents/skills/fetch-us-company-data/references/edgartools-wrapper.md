# edgartools Wrapper Reference

This document defines how to execute `scripts/edgartools_wrapper.py`.

Design goal:
- natural-language requests between skills by default,
- deterministic wrapper requests when reproducibility is needed,
- full edgartools fetch surface available to callers.

## Capability Scope
Use `references/edgartools-data-catalog.md` for the complete list of data this skill can fetch.

`edgartools` exposes broad capabilities: company filings, current filing feeds, filing data objects (for example Form 4 / 13F), company/entity facts with query filters, XBRL statements, and attachment/exhibit content.

Relevant docs:
- [Getting started](https://edgartools.readthedocs.io/en/latest/getting-started/)
- [Filings API](https://edgartools.readthedocs.io/en/latest/api/filings/)
- [Company API](https://edgartools.readthedocs.io/en/latest/api/company/)
- [Entity Facts API](https://edgartools.readthedocs.io/en/latest/api/entity-facts-reference/)
- [Data Objects (includes filing-type parsing and mappings)](https://edgartools.readthedocs.io/en/latest/data-objects/)
- [Insider Filings (Forms 3/4/5)](https://edgartools.readthedocs.io/en/latest/insider-filings/)

## Natural-Language Mode (Default)
Other skills do not need to send structured JSON.

They can send plain instructions such as:
- "Fetch latest 10-K and subsequent 10-Q filings for AAPL, include attachments."
- "Pull last 6 months of Form 4 filings and export transactions to CSV."

This skill should translate that objective into wrapper steps and execute them.

## Structured Mode (Optional)
Use this when caller explicitly wants deterministic replay or a saved request artifact.

## CLI

```bash
python3 .agents/skills/fetch-us-company-data/scripts/edgartools_wrapper.py \
  --request-file <request.json|request.yaml> \
  [--identity "Name email@domain.com"] \
  [--output-root <PATH>] \
  [--base-dir <PATH>] \
  [--pretty]
```

Exactly one of `--request-file` or `--request-json` is required.

## Request Schema

Top-level fields:
- `identity` (string, optional): EDGAR identity override.
- `identity_required` (bool, optional, default `true`): whether to require identity setup before running steps.
- `variables` (object, optional): reusable values.
- `steps` (array, required): ordered operations.
- `outputs` (object or array, optional): final exports by reference.

### Step schema
Each step must include exactly one operation key:
- `call`: invoke callable at a path.
- `read`: resolve and return object at a path.
- `value`: literal or interpolated value.

Optional step fields:
- `id` (string): reference name for this step result.
- `args` (array): call arguments.
- `kwargs` (object): call keyword arguments.
- `save` (object or array): export this step result immediately.

### Reference resolution
Paths support:
- dot access: `company.get_filings`
- index access: `filings[0]`
- key access: `my_dict["field"]`

Built-in root references:
- `edgar`: edgartools module.
- `helpers`: wrapper helpers.
- `py`: safe Python utilities.

### Interpolation tokens
Allowed inside `value`, `args`, and `kwargs`:
- `{"$ref": "step_id"}` direct prior reference.
- `{"$path": "step_id.subfield"}` nested path reference.
- `{"$var": "name"}` variable reference.
- `{"$env": "ENV_VAR", "default": "fallback"}` environment lookup.
- `{"$literal": ...}` pass literal object.

## Exports

`save`/`outputs` fields:
- `path` (required)
- `format` (optional: `auto`, `json`, `yaml`, `csv`, `markdown`, `text`, `bytes`)
- `include_attachments` (optional, markdown only)
- `index` (optional, csv only)
- `dataframe_kwargs` (optional, csv conversion only)

When `format` is `auto`, format is inferred from file extension when possible.

## Helpers

`helpers` namespace includes:
- `take(iterable, count)` -> list
- `first(iterable, default=None)` -> item/default
- `filing_markdown(filing, include_attachments=False, attachment_form=None)` -> markdown

`py` namespace includes:
- `list`, `len`, `sorted`, `dict`, `set`, `tuple`, `sum`, `min`, `max`, `str`, `int`, `float`, `bool`

## Form 4 Recipe

Direct example of pulling insider transaction data.

```json
{
  "steps": [
    {"id": "current_form4", "call": "edgar.get_current_filings", "kwargs": {"form": "4", "page_size": 40}},
    {"id": "filing", "read": "current_form4[0]"},
    {"id": "form4", "call": "filing.obj"},
    {
      "id": "transactions",
      "call": "form4.to_dataframe",
      "kwargs": {"detailed": true, "include_metadata": true},
      "save": [
        {"path": "tmp/form4-transactions.csv", "format": "csv"},
        {"path": "tmp/form4-transactions.json", "format": "json"}
      ]
    }
  ]
}
```

## Notes for Downstream Skills
- Keep requests minimal and explicit; fetch only what the current reasoning loop needs.
- Prefer stable exported artifacts (CSV/JSON/Markdown) for evidence traceability.
- For iterative research, compose multiple focused wrapper calls instead of one large pull.
