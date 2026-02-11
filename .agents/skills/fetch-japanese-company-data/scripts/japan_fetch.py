from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from loaders import _require_pandas


_ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
_JP_CODE_RE = re.compile(r"^(\d{4})(?:0)?$")
_YAHOO_JP_RE = re.compile(r"^(\d{4})\.T$", re.IGNORECASE)


@dataclass(frozen=True)
class ResolvedJapaneseCompany:
    input_identifier: str
    canonical_ticker: str
    local_code: str
    yahoo_symbol: str
    isin: Optional[str] = None
    company_name: Optional[str] = None


@dataclass(frozen=True)
class JapanFetchResult:
    resolved: ResolvedJapaneseCompany
    profile_path: Path
    income_statement_path: Path
    balance_sheet_path: Path
    cash_flow_path: Path
    source_metadata_path: Path


@dataclass(frozen=True)
class StatementSpec:
    concept: str
    label: str
    aliases: tuple[str, ...]
    default_zero: bool = False


_SEEDED_COMPANIES = [
    {
        "canonical_ticker": "79740",
        "local_code": "7974",
        "yahoo_symbol": "7974.T",
        "isin": "JP3756600007",
        "company_name": "Nintendo Co., Ltd.",
        "aliases": [
            "7974",
            "79740",
            "7974.T",
            "JP3756600007",
            "NINTENDO",
            "NINTENDO CO LTD",
        ],
    },
    {
        "canonical_ticker": "99830",
        "local_code": "9983",
        "yahoo_symbol": "9983.T",
        "company_name": "Fast Retailing Co., Ltd.",
        "aliases": [
            "9983",
            "99830",
            "9983.T",
            "FAST RETAILING",
            "FAST RETAILING CO LTD",
        ],
    },
]


_PROFILE_COLUMNS = [
    "symbol",
    "companyName",
    "currency",
    "price",
    "marketCap",
    "beta",
    "lastDividend",
    "range",
    "change",
    "changePercentage",
    "volume",
    "cik",
    "isin",
    "cusip",
    "exchange",
    "exchangeFullName",
    "industry",
    "sector",
    "country",
    "fullTimeEmployees",
    "ceo",
    "website",
    "phone",
    "address",
    "city",
    "state",
    "zip",
    "isEtf",
    "isAdr",
    "isActivelyTrading",
]


_INCOME_SPECS = [
    StatementSpec(
        concept="us-gaap_Revenues",
        label="Total Revenue",
        aliases=("Total Revenue", "Revenue"),
    ),
    StatementSpec(
        concept="us-gaap_GrossProfit",
        label="Gross Profit",
        aliases=("Gross Profit",),
    ),
    StatementSpec(
        concept="us-gaap_OperatingIncomeLoss",
        label="Operating Income",
        aliases=("Operating Income", "EBIT"),
    ),
    StatementSpec(
        concept="us-gaap_IncomeLossBeforeIncomeTaxes",
        label="Income Before Tax",
        aliases=("Pretax Income", "Income Before Tax"),
    ),
    StatementSpec(
        concept="us-gaap_IncomeTaxExpenseBenefit",
        label="Income Tax Expense",
        aliases=("Tax Provision", "Income Tax Expense"),
    ),
    StatementSpec(
        concept="us-gaap_NetIncomeLoss",
        label="Net Income",
        aliases=(
            "Net Income Common Stockholders",
            "Net Income",
            "Net Income From Continuing Operation Net Minority Interest",
        ),
    ),
    StatementSpec(
        concept="us-gaap_WeightedAverageNumberOfSharesOutstandingBasic",
        label="Weighted Average Shares Basic",
        aliases=("Basic Average Shares", "Weighted Average Shares Basic"),
    ),
    StatementSpec(
        concept="us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding",
        label="Weighted Average Shares Diluted",
        aliases=("Diluted Average Shares", "Weighted Average Shares Diluted"),
    ),
]


_BALANCE_SPECS = [
    StatementSpec(
        concept="us-gaap_CashAndCashEquivalentsAtCarryingValue",
        label="Cash and Cash Equivalents",
        aliases=("Cash And Cash Equivalents", "Cash And Short Term Investments"),
    ),
    StatementSpec(
        concept="us-gaap_Assets",
        label="Total Assets",
        aliases=("Total Assets",),
    ),
    StatementSpec(
        concept="us-gaap_StockholdersEquity",
        label="Total Equity",
        aliases=("Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"),
    ),
    StatementSpec(
        concept="us-gaap_Debt",
        label="Total Debt",
        aliases=(
            "Total Debt",
            "Current Debt And Capital Lease Obligation",
            "Long Term Debt And Capital Lease Obligation",
            "Long Term Debt",
            "Current Debt",
        ),
        default_zero=True,
    ),
]


_CASH_SPECS = [
    StatementSpec(
        concept="us-gaap_NetCashProvidedByUsedInOperatingActivities",
        label="Net Cash Provided by Operating Activities",
        aliases=("Operating Cash Flow", "Cash Flow From Continuing Operating Activities"),
    ),
    StatementSpec(
        concept="us-gaap_PaymentsToAcquirePropertyPlantAndEquipment",
        label="Capital Expenditures",
        aliases=("Capital Expenditure", "Capital Expenditure Reported"),
    ),
    StatementSpec(
        concept="us-gaap_DepreciationDepletionAndAmortization",
        label="Depreciation and Amortization",
        aliases=("Depreciation And Amortization",),
    ),
]


def _require_yfinance():
    try:
        import yfinance as yf  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "yfinance is required for fetch-japanese-company-data. "
            "Install with `python3 -m pip install -r requirements.txt`."
        ) from exc
    return yf


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _is_isin(value: str) -> bool:
    return bool(_ISIN_RE.match(str(value or "").strip().upper()))


def _infer_local_code(identifier: str) -> Optional[str]:
    text = str(identifier or "").strip().upper()
    code_match = _JP_CODE_RE.match(text)
    if code_match:
        return code_match.group(1)
    yahoo_match = _YAHOO_JP_RE.match(text)
    if yahoo_match:
        return yahoo_match.group(1)
    return None


def resolve_japanese_identifier(identifier: str, isin: Optional[str] = None) -> ResolvedJapaneseCompany:
    raw_identifier = str(identifier or "").strip().upper()
    if not raw_identifier:
        raise ValueError("Ticker/identifier is required.")

    supplied_identifiers = [raw_identifier]
    if isin:
        supplied_identifiers.append(str(isin).strip().upper())

    normalized_inputs = {_normalize_identifier(item) for item in supplied_identifiers if item}

    for entry in _SEEDED_COMPANIES:
        aliases = set(entry.get("aliases", []))
        aliases.add(entry["local_code"])
        aliases.add(entry["canonical_ticker"])
        aliases.add(entry["yahoo_symbol"])
        if entry.get("isin"):
            aliases.add(entry["isin"])

        normalized_aliases = {_normalize_identifier(item) for item in aliases if item}
        if normalized_inputs & normalized_aliases:
            return ResolvedJapaneseCompany(
                input_identifier=raw_identifier,
                canonical_ticker=entry["canonical_ticker"],
                local_code=entry["local_code"],
                yahoo_symbol=entry["yahoo_symbol"],
                isin=entry.get("isin"),
                company_name=entry.get("company_name"),
            )

    if _is_isin(raw_identifier):
        raise ValueError(
            "ISIN provided without a seeded mapping. "
            "Use a TSE code (for example `7974` or `79740`) or add the ISIN mapping first."
        )

    local_code = _infer_local_code(raw_identifier)
    if not local_code:
        raise ValueError(
            "Unsupported Japanese identifier format. "
            "Use a 4-digit TSE code, 5-digit JP code ending in 0, .T Yahoo symbol, or a seeded ISIN."
        )

    canonical = f"{local_code}0"
    if raw_identifier.isdigit() and len(raw_identifier) == 5:
        canonical = raw_identifier

    return ResolvedJapaneseCompany(
        input_identifier=raw_identifier,
        canonical_ticker=canonical,
        local_code=local_code,
        yahoo_symbol=f"{local_code}.T",
        isin=isin.strip().upper() if isin else None,
        company_name=None,
    )


def _safe_number(value):
    if value is None:
        return ""
    try:
        numeric = float(value)
    except Exception:
        return ""
    if numeric != numeric:
        return ""
    return numeric


def _profile_template() -> dict:
    return {column: "" for column in _PROFILE_COLUMNS}


def _range_text(low, high) -> str:
    low_value = _safe_number(low)
    high_value = _safe_number(high)
    if low_value == "" or high_value == "":
        return ""
    return f"{low_value}-{high_value}"


def _coalesce(mapping: dict, keys: Iterable[str]):
    for key in keys:
        value = mapping.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _build_profile_row(resolved: ResolvedJapaneseCompany, info: dict) -> dict:
    row = _profile_template()

    price = _coalesce(info, ["currentPrice", "regularMarketPrice", "previousClose"])
    change = _coalesce(info, ["regularMarketChange"])
    change_pct = _coalesce(info, ["regularMarketChangePercent"])
    market_cap = _coalesce(info, ["marketCap"])
    week_low = _coalesce(info, ["fiftyTwoWeekLow"])
    week_high = _coalesce(info, ["fiftyTwoWeekHigh"])

    row.update(
        {
            "symbol": resolved.canonical_ticker,
            "companyName": _coalesce(info, ["longName", "shortName"]) or resolved.company_name or resolved.yahoo_symbol,
            "currency": _coalesce(info, ["currency"]) or "JPY",
            "price": _safe_number(price),
            "marketCap": _safe_number(market_cap),
            "beta": _safe_number(_coalesce(info, ["beta"])),
            "lastDividend": _safe_number(_coalesce(info, ["lastDividendValue", "dividendRate"])),
            "range": _range_text(week_low, week_high),
            "change": _safe_number(change),
            "changePercentage": _safe_number(change_pct),
            "volume": _safe_number(_coalesce(info, ["volume", "regularMarketVolume", "averageVolume"])),
            "cik": _coalesce(info, ["cik"]) or "",
            "isin": resolved.isin or (_coalesce(info, ["isin"]) or ""),
            "cusip": _coalesce(info, ["cusip"]) or "",
            "exchange": _coalesce(info, ["exchange"]) or "TYO",
            "exchangeFullName": _coalesce(info, ["fullExchangeName"]) or "Tokyo Stock Exchange",
            "industry": _coalesce(info, ["industry"]) or "",
            "sector": _coalesce(info, ["sector"]) or "",
            "country": _coalesce(info, ["country"]) or "Japan",
            "fullTimeEmployees": _safe_number(_coalesce(info, ["fullTimeEmployees"])),
            "ceo": _coalesce(info, ["companyOfficers", "ceo"]) or "",
            "website": _coalesce(info, ["website"]) or "",
            "phone": _coalesce(info, ["phone"]) or "",
            "address": _coalesce(info, ["address1"]) or "",
            "city": _coalesce(info, ["city"]) or "",
            "state": _coalesce(info, ["state"]) or "",
            "zip": _coalesce(info, ["zip"]) or "",
            "isEtf": bool(str(_coalesce(info, ["quoteType"]) or "").upper() == "ETF"),
            "isAdr": bool(_coalesce(info, ["isAdr"]) or False),
            "isActivelyTrading": bool(
                _coalesce(info, ["regularMarketPrice", "currentPrice", "volume"]) is not None
            ),
        }
    )

    if isinstance(row.get("ceo"), list):
        officers = row["ceo"]
        if officers and isinstance(officers[0], dict):
            row["ceo"] = officers[0].get("name", "")
        else:
            row["ceo"] = ""

    return row


def _normalize_metric_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def _extract_date_columns(df) -> list[tuple[object, str]]:
    pd = _require_pandas()
    pairs: list[tuple[object, str]] = []
    for column in list(df.columns):
        parsed = pd.to_datetime(column, errors="coerce")
        if parsed is pd.NaT or pd.isna(parsed):
            continue
        pairs.append((column, parsed.date().isoformat()))
    pairs.sort(key=lambda pair: pair[1], reverse=True)
    return pairs


def _find_series(raw_df, aliases: Iterable[str]):
    pd = _require_pandas()
    if raw_df is None or getattr(raw_df, "empty", True):
        return None

    labels = [str(index) for index in raw_df.index]
    normalized = [_normalize_metric_name(label) for label in labels]

    for alias in aliases:
        target = _normalize_metric_name(alias)
        if not target:
            continue
        for idx, label_norm in enumerate(normalized):
            if label_norm == target:
                row = raw_df.iloc[idx]
                if isinstance(row, pd.DataFrame):
                    return row.iloc[0]
                return row

    for alias in aliases:
        target = _normalize_metric_name(alias)
        if not target:
            continue
        for idx, label_norm in enumerate(normalized):
            if target in label_norm:
                row = raw_df.iloc[idx]
                if isinstance(row, pd.DataFrame):
                    return row.iloc[0]
                return row

    return None


def _values_from_series(series, date_columns: list[tuple[object, str]]) -> list:
    pd = _require_pandas()
    values = []
    for raw_column, _ in date_columns:
        if series is None:
            values.append(pd.NA)
            continue
        values.append(pd.to_numeric(series.get(raw_column), errors="coerce"))
    return values


def _iter_source_rows(raw_df):
    pd = _require_pandas()
    if raw_df is None or getattr(raw_df, "empty", True):
        return

    for idx in range(len(raw_df)):
        label = str(raw_df.index[idx]).strip()
        if not label:
            continue
        row = raw_df.iloc[idx]
        if isinstance(row, pd.DataFrame):
            if row.empty:
                continue
            row = row.iloc[0]
        yield label, row


def _build_statement_frame(raw_df, specs: list[StatementSpec], include_all_rows: bool = True):
    pd = _require_pandas()
    date_columns = _extract_date_columns(raw_df)
    if not date_columns:
        return pd.DataFrame()

    records = []
    seen_labels = set()
    for spec in specs:
        series = _find_series(raw_df, spec.aliases)
        values = _values_from_series(series, date_columns)
        if series is None and spec.default_zero:
            values = [0.0 for _ in date_columns]

        row = {
            "concept": spec.concept,
            "label": spec.label,
        }
        for (_, iso_column), value in zip(date_columns, values):
            row[iso_column] = value
        records.append(row)
        seen_labels.add(_normalize_metric_name(spec.label))
        for alias in spec.aliases:
            seen_labels.add(_normalize_metric_name(alias))

    if include_all_rows:
        for label, series in _iter_source_rows(raw_df):
            normalized_label = _normalize_metric_name(label)
            if not normalized_label or normalized_label in seen_labels:
                continue

            values = _values_from_series(series, date_columns)
            if not any((value is not None) and (not pd.isna(value)) for value in values):
                continue

            row = {
                "concept": f"yahoo_{normalized_label}",
                "label": label,
            }
            for (_, iso_column), value in zip(date_columns, values):
                row[iso_column] = value
            records.append(row)
            seen_labels.add(normalized_label)

    ordered_columns = ["concept", "label"] + [iso for _, iso in date_columns]
    statement_df = pd.DataFrame(records, columns=ordered_columns)
    return statement_df


def _write_profile(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=_PROFILE_COLUMNS)
        writer.writeheader()
        writer.writerow({column: row.get(column, "") for column in _PROFILE_COLUMNS})


def fetch_japanese_company_data(
    resolved: ResolvedJapaneseCompany,
    data_dir: Path,
) -> JapanFetchResult:
    yf = _require_yfinance()
    pd = _require_pandas()

    data_dir.mkdir(parents=True, exist_ok=True)
    annual_dir = data_dir / "financial_statements" / "annual"
    annual_dir.mkdir(parents=True, exist_ok=True)

    ticker = yf.Ticker(resolved.yahoo_symbol)

    try:
        info = ticker.get_info() or {}
    except Exception:
        info = {}

    financials = getattr(ticker, "financials", None)
    balance_sheet = getattr(ticker, "balance_sheet", None)
    cashflow = getattr(ticker, "cashflow", None)

    financials = financials if hasattr(financials, "empty") else pd.DataFrame()
    balance_sheet = balance_sheet if hasattr(balance_sheet, "empty") else pd.DataFrame()
    cashflow = cashflow if hasattr(cashflow, "empty") else pd.DataFrame()

    if financials.empty or balance_sheet.empty or cashflow.empty:
        raise RuntimeError(
            f"Unable to load full annual statements from Yahoo Finance for {resolved.yahoo_symbol}."
        )

    income_df = _build_statement_frame(financials, _INCOME_SPECS)
    balance_df = _build_statement_frame(balance_sheet, _BALANCE_SPECS)
    cash_df = _build_statement_frame(cashflow, _CASH_SPECS)

    if income_df.empty:
        raise RuntimeError("Income statement extraction returned no parseable annual periods.")
    if balance_df.empty:
        raise RuntimeError("Balance sheet extraction returned no parseable annual periods.")
    if cash_df.empty:
        raise RuntimeError("Cash flow extraction returned no parseable annual periods.")

    profile_row = _build_profile_row(resolved, info)

    profile_path = data_dir / "company_profile.csv"
    income_path = annual_dir / "income_statement.csv"
    balance_path = annual_dir / "balance_sheet.csv"
    cash_path = annual_dir / "cash_flow_statement.csv"

    _write_profile(profile_path, profile_row)
    income_df.to_csv(income_path, index=False)
    balance_df.to_csv(balance_path, index=False)
    cash_df.to_csv(cash_path, index=False)

    source_metadata = {
        "source": "yfinance",
        "retrieved": date.today().isoformat(),
        "input_identifier": resolved.input_identifier,
        "canonical_ticker": resolved.canonical_ticker,
        "local_code": resolved.local_code,
        "yahoo_symbol": resolved.yahoo_symbol,
        "isin": resolved.isin,
    }
    source_metadata_path = data_dir / "source-metadata.json"
    source_metadata_path.write_text(json.dumps(source_metadata, indent=2))

    return JapanFetchResult(
        resolved=resolved,
        profile_path=profile_path,
        income_statement_path=income_path,
        balance_sheet_path=balance_path,
        cash_flow_path=cash_path,
        source_metadata_path=source_metadata_path,
    )
