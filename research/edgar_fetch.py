from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

from .loaders import _require_pandas


PAGE_DIV_PATTERN = re.compile(
    r'<div\s+align\s*=\s*([\'"])center\1\s*>\s*(\d+)\s*</div>',
    re.IGNORECASE,
)


@dataclass
class FilingSummary:
    form: str
    filing_date: date
    path: Path


def ensure_edgar_identity(identity: Optional[str] = None) -> str:
    from edgar import set_identity  # type: ignore

    if load_dotenv:
        load_dotenv()

    identity_value = identity or os.getenv("EDGAR_IDENTITY") or os.getenv("SEC_IDENTITY_EMAIL")
    if not identity_value:
        raise RuntimeError(
            "EDGAR_IDENTITY is not set. Add it to .env or pass --identity."
        )

    set_identity(identity_value)
    return identity_value


def _to_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def to_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return None


def iso_date(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def inject_page_headers(markdown: Optional[str]) -> Optional[str]:
    if not markdown:
        return markdown

    def _replacement(match: re.Match) -> str:
        page_number = match.group(2)
        return f"### Page {page_number} {{#page-{page_number}}}"

    return PAGE_DIV_PATTERN.sub(_replacement, markdown)


def filing_markdown(
    filing,
    include_attachments: bool = False,
    attachment_forms: Optional[Set[str]] = None,
) -> str:
    sections: List[str] = []

    try:
        primary_markdown = inject_page_headers(filing.markdown())
        if primary_markdown:
            sections.append(primary_markdown.strip())
    except Exception:
        pass

    if not include_attachments:
        return "\n\n---\n\n".join(sections).strip()

    if attachment_forms is not None:
        form_type = getattr(filing, "form", None)
        if form_type and form_type.upper() not in {f.upper() for f in attachment_forms}:
            return "\n\n---\n\n".join(sections).strip()

    try:
        attachments = filing.attachments
    except Exception:
        attachments = None

    if attachments:
        primary_documents: Set[str] = set()
        try:
            primary_documents = {
                attachment.document
                for attachment in attachments.primary_documents
                if attachment is not None and getattr(attachment, "document", None)
            }
        except Exception:
            primary_documents = set()

        for attachment in attachments:
            try:
                if not hasattr(attachment, "is_html") or not attachment.is_html():
                    continue
                document_name = getattr(attachment, "document", None)
                if document_name and document_name in primary_documents:
                    continue
                markdown_content = inject_page_headers(attachment.markdown())
                if not markdown_content:
                    continue

                title_parts: List[str] = []
                if document_name:
                    title_parts.append(document_name)
                description = getattr(attachment, "description", None)
                if description and description not in title_parts:
                    title_parts.append(description)
                document_type = getattr(attachment, "document_type", None)
                if document_type:
                    title_parts.append(f"Type: {document_type}")

                heading = " - ".join(title_parts) if title_parts else "Attachment"
                sections.append(f"### Attachment: {heading}\n\n{markdown_content.strip()}")
            except Exception:
                continue

    return "\n\n---\n\n".join(section for section in sections if section).strip()


def _get_attr(obj, names: Iterable[str]):
    for name in names:
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


def _get_filing_date(filing):
    return _get_attr(filing, ["filed_date", "filed", "filing_date"])


def _get_period_end(filing):
    return _get_attr(filing, ["period_end", "period_ending", "period_of_report", "date_of_report"])


def _get_accession(filing):
    return _get_attr(filing, ["accession_number", "accession_no", "accession"])


def _list_filings(filings) -> List:
    try:
        return list(filings)
    except TypeError:
        return []


def _latest_filing(filings):
    if filings is None:
        return None
    if hasattr(filings, "latest"):
        try:
            return filings.latest()
        except Exception:
            pass
    entries = _list_filings(filings)
    if not entries:
        return None

    def _key(f):
        return _to_date(_get_filing_date(f)) or date.min

    entries.sort(key=_key, reverse=True)
    return entries[0]


def _filing_filename(filing) -> str:
    form = getattr(filing, "form", "FILING")
    form = str(form).replace("/", "-").replace(" ", "")
    filing_date = _get_filing_date(filing) or "unknown"
    accession = _get_accession(filing)
    if accession:
        return f"{form}-{filing_date}-{accession}.md"
    return f"{form}-{filing_date}.md"


def _write_filing_markdown(
    filing,
    data_dir: Path,
    include_attachments: bool = False,
    attachment_forms: Optional[Set[str]] = None,
) -> Optional[FilingSummary]:
    filename = _filing_filename(filing)
    path = data_dir / filename
    if not path.exists():
        markdown = filing_markdown(
            filing,
            include_attachments=include_attachments,
            attachment_forms=attachment_forms,
        )
        path.write_text(markdown)

    return FilingSummary(
        form=str(getattr(filing, "form", "")),
        filing_date=_to_date(_get_filing_date(filing)) or date.min,
        path=path,
    )


def fetch_company_filings(
    ticker: str,
    data_dir: Path,
    identity: Optional[str] = None,
) -> List[FilingSummary]:
    ensure_edgar_identity(identity)
    from edgar import Company  # type: ignore

    company = Company(ticker)

    try:
        is_fpi = len(company.get_filings(form="20-F")) > 0
    except Exception:
        is_fpi = False

    if is_fpi:
        periodic_forms = ["20-F"]
        current_form = "6-K"
    else:
        periodic_forms = ["10-K", "10-Q"]
        current_form = "8-K"

    latest_periodic_date: Optional[datetime] = None
    latest_10k_date: Optional[datetime] = None
    summaries: List[FilingSummary] = []

    for form in periodic_forms:
        if not is_fpi and form == "10-Q":
            continue

        latest_filing = _latest_filing(company.get_filings(form=form))
        if not latest_filing:
            continue

        filing_date_dt = to_datetime(_get_filing_date(latest_filing))
        if filing_date_dt:
            if latest_periodic_date is None or filing_date_dt > latest_periodic_date:
                latest_periodic_date = filing_date_dt
            if form == "10-K":
                latest_10k_date = filing_date_dt

        summary = _write_filing_markdown(latest_filing, data_dir)
        if summary:
            summaries.append(summary)

    if not is_fpi:
        try:
            all_10qs = list(company.get_filings(form="10-Q"))
        except Exception:
            all_10qs = []

        if latest_10k_date is None:
            latest_only = _latest_filing(all_10qs)
            ten_q_candidates = [latest_only] if latest_only else []
        else:
            ten_q_candidates = []
            for filing in all_10qs:
                filing_date_dt = to_datetime(_get_filing_date(filing))
                if filing_date_dt and filing_date_dt <= latest_10k_date:
                    continue
                ten_q_candidates.append(filing)

        for filing in sorted(
            ten_q_candidates,
            key=lambda f: to_datetime(_get_filing_date(f)) or datetime.min,
        ):
            filing_date_dt = to_datetime(_get_filing_date(filing))
            if filing_date_dt:
                if latest_periodic_date is None or filing_date_dt > latest_periodic_date:
                    latest_periodic_date = filing_date_dt

            summary = _write_filing_markdown(filing, data_dir)
            if summary:
                summaries.append(summary)

    events = _list_filings(company.get_filings(form=current_form))
    for filing in events:
        filing_date_dt = to_datetime(_get_filing_date(filing))
        if latest_periodic_date and filing_date_dt and filing_date_dt <= latest_periodic_date:
            continue
        summary = _write_filing_markdown(
            filing,
            data_dir,
            include_attachments=True,
            attachment_forms={current_form},
        )
        if summary:
            summaries.append(summary)

    return summaries


def _prepare_statement_df(df):
    pd = _require_pandas()
    if df is None:
        return None
    if hasattr(df, "copy"):
        df = df.copy()
    if df is None:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join([str(c) for c in col if c]) for col in df.columns]
    df.columns = [str(c) for c in df.columns]
    df.index = [str(i) for i in df.index]
    return df


def _period_columns(df) -> Tuple[object, List[str], dict]:
    pd = _require_pandas()
    period_cols = []
    date_map = {}
    for col in df.columns:
        parsed = pd.to_datetime(col, errors="coerce")
        if parsed is not pd.NaT and not pd.isna(parsed):
            period_cols.append(col)
            date_map[col] = parsed.date()
    if period_cols:
        return df, period_cols, date_map

    idx_dates = [pd.to_datetime(i, errors="coerce") for i in df.index]
    if any(not pd.isna(d) for d in idx_dates):
        df = df.transpose()
        period_cols = []
        date_map = {}
        for col in df.columns:
            parsed = pd.to_datetime(col, errors="coerce")
            if parsed is not pd.NaT and not pd.isna(parsed):
                period_cols.append(col)
                date_map[col] = parsed.date()
        return df, period_cols, date_map

    return df, [], {}


def _find_row(df, candidates: Iterable[str]):
    labels = [str(i).strip() for i in df.index]
    for cand in candidates:
        cand_lower = cand.lower()
        for idx, label in enumerate(labels):
            if label.lower() == cand_lower:
                return df.iloc[idx]
    for cand in candidates:
        cand_lower = cand.lower()
        for idx, label in enumerate(labels):
            if cand_lower in label.lower():
                return df.iloc[idx]
    return None


def _build_base_frame(period_cols, date_map, ticker, period_label, currency):
    pd = _require_pandas()
    dates = [date_map[c] for c in period_cols]
    df = pd.DataFrame(
        {
            "date": [d.isoformat() for d in dates],
            "symbol": ticker,
            "reportedCurrency": currency or "",
            "fiscalYear": [d.year for d in dates],
            "period": period_label,
        }
    )
    return df


def _attach_metric(df, series, name, period_cols):
    pd = _require_pandas()
    if series is None:
        df[name] = pd.NA
        return
    values = [series.get(col) for col in period_cols]
    df[name] = pd.to_numeric(values, errors="coerce")


def _build_income_statement(financials, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    df = _prepare_statement_df(financials)
    if df is None:
        return pd.DataFrame()

    df, period_cols, date_map = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, date_map, ticker, period_label, currency)

    revenue = _find_row(df, ["Revenue", "Revenues", "Total Revenue", "Sales"])
    gross_profit = _find_row(df, ["Gross Profit"])
    operating_income = _find_row(df, ["Operating Income", "Operating Income (Loss)", "Operating Income Loss"])
    income_before_tax = _find_row(df, ["Income Before Tax", "Income (Loss) Before Income Taxes"])
    income_tax = _find_row(df, ["Income Tax Expense", "Provision for Income Taxes"])
    net_income = _find_row(df, ["Net Income", "Net Income (Loss)"])
    shares_basic = _find_row(df, ["Weighted Average Shares Basic", "Weighted Average Shares"])
    shares_dil = _find_row(df, ["Weighted Average Shares Diluted", "Weighted Average Shares Diluted Shares"])

    _attach_metric(out, revenue, "revenue", period_cols)
    _attach_metric(out, gross_profit, "grossProfit", period_cols)
    _attach_metric(out, operating_income, "ebit", period_cols)
    _attach_metric(out, income_before_tax, "incomeBeforeTax", period_cols)
    _attach_metric(out, income_tax, "incomeTaxExpense", period_cols)
    _attach_metric(out, net_income, "netIncome", period_cols)
    _attach_metric(out, shares_basic, "weightedAverageShsOut", period_cols)
    _attach_metric(out, shares_dil, "weightedAverageShsOutDil", period_cols)

    out["ebitda"] = pd.NA
    return out


def _build_balance_sheet(financials, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    df = _prepare_statement_df(financials)
    if df is None:
        return pd.DataFrame()

    df, period_cols, date_map = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, date_map, ticker, period_label, currency)

    cash = _find_row(df, ["Cash and Cash Equivalents", "Cash & Cash Equivalents"])
    total_assets = _find_row(df, ["Total Assets"])
    total_equity = _find_row(df, ["Total Stockholders' Equity", "Total Stockholders Equity", "Total Equity"])
    total_debt = _find_row(df, ["Total Debt"])
    short_debt = _find_row(df, ["Short-Term Debt", "Short Term Debt", "Current Portion of Long-Term Debt"])
    long_debt = _find_row(df, ["Long-Term Debt", "Long Term Debt"])

    _attach_metric(out, cash, "cashAndCashEquivalents", period_cols)
    _attach_metric(out, total_assets, "totalAssets", period_cols)
    _attach_metric(out, total_equity, "totalEquity", period_cols)

    if total_debt is not None:
        _attach_metric(out, total_debt, "totalDebt", period_cols)
    else:
        debt_series = None
        if short_debt is not None and long_debt is not None:
            debt_series = short_debt.add(long_debt, fill_value=0)
        elif short_debt is not None:
            debt_series = short_debt
        elif long_debt is not None:
            debt_series = long_debt
        _attach_metric(out, debt_series, "totalDebt", period_cols)

    out["netDebt"] = out["totalDebt"] - out["cashAndCashEquivalents"]
    return out


def _build_cash_flow(financials, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    df = _prepare_statement_df(financials)
    if df is None:
        return pd.DataFrame()

    df, period_cols, date_map = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, date_map, ticker, period_label, currency)

    ocf = _find_row(
        df,
        [
            "Net Cash Provided by Operating Activities",
            "Net Cash Provided by Operating Activities (Continuing Operations)",
        ],
    )
    capex = _find_row(
        df,
        [
            "Payments to Acquire Property, Plant, and Equipment",
            "Capital Expenditures",
            "Purchases of Property and Equipment",
        ],
    )
    depreciation = _find_row(
        df,
        [
            "Depreciation and Amortization",
            "Depreciation",
            "Depreciation and Amortization of Property, Plant and Equipment",
        ],
    )

    _attach_metric(out, ocf, "operatingCashFlow", period_cols)
    _attach_metric(out, capex, "capitalExpenditure", period_cols)
    _attach_metric(out, depreciation, "depreciationAndAmortization", period_cols)

    if "operatingCashFlow" in out.columns:
        if "capitalExpenditure" in out.columns:
            capex_values = out["capitalExpenditure"].fillna(0)
            ocf_values = out["operatingCashFlow"].fillna(0)
            fcf = ocf_values + capex_values
            if (capex_values > 0).any():
                fcf = ocf_values - capex_values.abs()
            out["freeCashFlow"] = fcf
        else:
            out["freeCashFlow"] = pd.NA

    return out


def _write_company_profile(company, data_dir: Path, ticker: str, currency: str):
    pd = _require_pandas()
    data = getattr(company, "data", None)
    name = None
    cik = None
    industry = None
    sector = None
    country = None
    if data is not None:
        name = getattr(data, "name", None) or getattr(data, "company_name", None)
        cik = getattr(data, "cik", None)
        industry = getattr(data, "industry", None)
        sector = getattr(data, "sector", None)
        country = getattr(data, "country", None)

    if not name:
        name = getattr(company, "name", None) or getattr(company, "company_name", None)

    columns = [
        "symbol",
        "price",
        "marketCap",
        "beta",
        "lastDividend",
        "range",
        "change",
        "changePercentage",
        "volume",
        "averageVolume",
        "companyName",
        "currency",
        "cik",
        "isin",
        "cusip",
        "exchangeFullName",
        "exchange",
        "industry",
        "website",
        "description",
        "ceo",
        "sector",
        "country",
        "fullTimeEmployees",
        "phone",
        "address",
        "city",
        "state",
        "zip",
        "image",
        "ipoDate",
        "defaultImage",
        "isEtf",
        "isActivelyTrading",
        "isAdr",
        "isFund",
    ]
    row = {col: "" for col in columns}
    row["symbol"] = ticker
    row["companyName"] = name or ticker
    row["currency"] = currency
    if cik:
        row["cik"] = str(cik)
    if industry:
        row["industry"] = industry
    if sector:
        row["sector"] = sector
    if country:
        row["country"] = country

    df = pd.DataFrame([row])
    df.to_csv(data_dir / "company_profile.csv", index=False)


def fetch_company_financials(ticker: str, data_dir: Path, identity: Optional[str] = None) -> None:
    ensure_edgar_identity(identity)
    from edgar import Company  # type: ignore

    pd = _require_pandas()
    company = Company(ticker)
    currency = "USD"

    _write_company_profile(company, data_dir, ticker, currency)

    financials = company.get_financials()
    income_annual = _build_income_statement(financials.income, ticker, "FY", currency)
    balance_annual = _build_balance_sheet(financials.balance_sheet, ticker, "FY", currency)
    cash_annual = _build_cash_flow(financials.cash_flow, ticker, "FY", currency)

    raw_dir = data_dir / "edgar_raw"
    raw_dir.mkdir(exist_ok=True)
    raw_income = _prepare_statement_df(financials.income)
    raw_balance = _prepare_statement_df(financials.balance_sheet)
    raw_cash = _prepare_statement_df(financials.cash_flow)
    if raw_income is not None:
        raw_income.to_csv(raw_dir / "income_statement_raw.csv")
    if raw_balance is not None:
        raw_balance.to_csv(raw_dir / "balance_sheet_raw.csv")
    if raw_cash is not None:
        raw_cash.to_csv(raw_dir / "cash_flow_statement_raw.csv")

    if income_annual.empty or balance_annual.empty or cash_annual.empty:
        raise RuntimeError(
            "Unable to parse annual financial statements from EDGAR. "
            "Check the raw statement files under data/edgar_raw."
        )

    if not income_annual.empty and not cash_annual.empty:
        merged = income_annual.merge(
            cash_annual[["date", "depreciationAndAmortization"]],
            on="date",
            how="left",
        )
        income_annual["ebitda"] = merged["ebit"] + merged["depreciationAndAmortization"].fillna(0)

    income_annual.to_csv(data_dir / "income_statement_annual.csv", index=False)
    balance_annual.to_csv(data_dir / "balance_sheet_annual.csv", index=False)
    cash_annual.to_csv(data_dir / "cash_flow_statement_annual.csv", index=False)

    quarterly = company.get_quarterly_financials()
    income_q = _build_income_statement(quarterly.income, ticker, "Q", currency)
    balance_q = _build_balance_sheet(quarterly.balance_sheet, ticker, "Q", currency)
    cash_q = _build_cash_flow(quarterly.cash_flow, ticker, "Q", currency)

    if not income_q.empty and not cash_q.empty:
        merged_q = income_q.merge(
            cash_q[["date", "depreciationAndAmortization"]],
            on="date",
            how="left",
        )
        income_q["ebitda"] = merged_q["ebit"] + merged_q["depreciationAndAmortization"].fillna(0)

    income_q.to_csv(data_dir / "income_statement_quarterly.csv", index=False)
    balance_q.to_csv(data_dir / "balance_sheet_quarterly.csv", index=False)
    cash_q.to_csv(data_dir / "cash_flow_statement_quarterly.csv", index=False)
