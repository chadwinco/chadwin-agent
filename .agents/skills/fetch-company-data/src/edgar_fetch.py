from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None

from loaders import _require_pandas


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
    filings_dir = data_dir / "filings"
    filings_dir.mkdir(parents=True, exist_ok=True)

    filename = _filing_filename(filing)
    path = filings_dir / filename
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

        try:
            latest_filing = _latest_filing(company.get_filings(form=form))
        except Exception:
            latest_filing = None
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

    if latest_10k_date is None:
        for form in ("S-1/A", "S-1", "F-1/A", "F-1"):
            try:
                latest_registration = _latest_filing(company.get_filings(form=form))
            except Exception:
                latest_registration = None
            if not latest_registration:
                continue
            summary = _write_filing_markdown(latest_registration, data_dir)
            if summary:
                summaries.append(summary)
                filing_date_dt = to_datetime(_get_filing_date(latest_registration))
                if filing_date_dt and (
                    latest_periodic_date is None or filing_date_dt > latest_periodic_date
                ):
                    latest_periodic_date = filing_date_dt

    try:
        events = _list_filings(company.get_filings(form=current_form))
    except Exception:
        events = []
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
    if hasattr(df, "to_dataframe"):
        try:
            df = df.to_dataframe(standard=False)
        except TypeError:
            df = df.to_dataframe()
        except Exception:
            pass
    if hasattr(df, "copy"):
        df = df.copy()
    if df is None:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join([str(c) for c in col if c]) for col in df.columns]
    df.columns = [str(c) for c in df.columns]
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


def _series_has_values(series, period_cols) -> bool:
    pd = _require_pandas()
    if series is None:
        return False
    if isinstance(series, pd.DataFrame):
        if series.empty:
            return False
        series = series.iloc[0]
    for col in period_cols:
        value = series.get(col)
        if value is None:
            continue
        if not pd.isna(value):
            return True
    return False


def _combine_rows(rows, period_cols):
    pd = _require_pandas()
    if rows is None or rows.empty:
        return None
    if len(rows) == 1:
        return rows.iloc[0]

    combined = rows.iloc[0].copy()
    for idx in range(1, len(rows)):
        row = rows.iloc[idx]
        for col in period_cols:
            if col not in row.index:
                continue
            current = combined.get(col)
            if current is None or pd.isna(current):
                candidate = row.get(col)
                if candidate is not None and not pd.isna(candidate):
                    combined[col] = candidate
    return combined


_PERIOD_COL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _period_cols_from_df(df) -> list[str]:
    return [col for col in df.columns if _PERIOD_COL_RE.match(str(col))]


def _find_row(df, concepts: Iterable[str] = (), labels: Iterable[str] = ()):
    pd = _require_pandas()
    if df is None or getattr(df, "empty", False):
        return None

    period_cols = _period_cols_from_df(df)

    if "concept" in df.columns:
        concept_series = df["concept"].astype(str).str.lower()
        concept_rows = []
        for cand in concepts:
            rows = df[concept_series == cand.lower()]
            if not rows.empty:
                concept_rows.append(rows)
        if concept_rows:
            return _combine_rows(pd.concat(concept_rows, ignore_index=True), period_cols)

    if "label" in df.columns:
        label_series = df["label"].astype(str)
        label_rows = []
        for cand in labels:
            rows = df[label_series.str.lower() == cand.lower()]
            if not rows.empty:
                label_rows.append(rows)
        if not label_rows:
            for cand in labels:
                rows = df[label_series.str.contains(cand, case=False, na=False, regex=False)]
                if not rows.empty:
                    label_rows.append(rows)
        if label_rows:
            return _combine_rows(pd.concat(label_rows, ignore_index=True), period_cols)

    labels_idx = [str(i).strip() for i in df.index]
    for cand in labels:
        cand_lower = cand.lower()
        for idx, label in enumerate(labels_idx):
            if label.lower() == cand_lower:
                return df.iloc[idx]
    for cand in labels:
        cand_lower = cand.lower()
        for idx, label in enumerate(labels_idx):
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
    if isinstance(series, pd.DataFrame):
        if series.empty:
            df[name] = pd.NA
            return
        series = series.iloc[0]
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

    revenue = _find_row(
        df,
        concepts=[
            "us-gaap_Revenues",
            "us-gaap_SalesRevenueNet",
            "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax",
            "us-gaap_SalesRevenueGoodsNet",
            "us-gaap_SalesRevenueServicesNet",
        ],
        labels=["Revenue", "Revenues", "Total Revenue", "Net Revenue", "Sales"],
    )
    gross_profit = _find_row(
        df,
        concepts=["us-gaap_GrossProfit"],
        labels=["Gross Profit"],
    )
    income_before_tax = _find_row(
        df,
        concepts=[
            "us-gaap_IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "us-gaap_IncomeLossBeforeIncomeTaxes",
        ],
        labels=["Income Before Tax", "Income Before Taxes", "Income (Loss) Before Income Taxes"],
    )
    operating_income = _find_row(
        df,
        concepts=["us-gaap_OperatingIncomeLoss"],
        labels=["Operating Income", "Operating Income (Loss)", "Operating Income Loss"],
    )
    if operating_income is None or not _series_has_values(operating_income, period_cols):
        operating_income = income_before_tax
    income_tax = _find_row(
        df,
        concepts=["us-gaap_IncomeTaxExpenseBenefit"],
        labels=["Income Tax Expense", "Provision for Income Taxes"],
    )
    net_income = _find_row(
        df,
        concepts=["us-gaap_NetIncomeLoss"],
        labels=["Net Income", "Net Income (Loss)", "Profit or Loss"],
    )
    shares_basic = _find_row(
        df,
        concepts=["us-gaap_WeightedAverageNumberOfSharesOutstandingBasic"],
        labels=["Weighted Average Shares Basic", "Shares Outstanding (Basic)"],
    )
    shares_dil = _find_row(
        df,
        concepts=["us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding"],
        labels=["Weighted Average Shares Diluted", "Shares Outstanding (Diluted)"],
    )

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

    cash = _find_row(
        df,
        concepts=[
            "us-gaap_CashAndCashEquivalentsAtCarryingValue",
            "us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ],
        labels=["Cash and Cash Equivalents", "Cash & Cash Equivalents"],
    )
    total_assets = _find_row(
        df,
        concepts=["us-gaap_Assets"],
        labels=["Total Assets"],
    )
    total_equity = _find_row(
        df,
        concepts=[
            "us-gaap_StockholdersEquity",
            "us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "us-gaap_StockholdersEquityIncludingPortionAttributableToParent",
        ],
        labels=["Total Stockholders' Equity", "Total Stockholders Equity", "Total Equity"],
    )
    total_debt = _find_row(
        df,
        concepts=[
            "us-gaap_Debt",
            "us-gaap_LongTermDebt",
            "us-gaap_LongTermDebtAndCapitalLeaseObligations",
        ],
        labels=["Total Debt"],
    )
    short_debt = _find_row(
        df,
        concepts=["us-gaap_DebtCurrent", "us-gaap_ShortTermBorrowings"],
        labels=["Short-Term Debt", "Short Term Debt", "Current Portion of Long-Term Debt"],
    )
    long_debt = _find_row(
        df,
        concepts=["us-gaap_LongTermDebtNoncurrent", "us-gaap_LongTermDebt"],
        labels=["Long-Term Debt", "Long Term Debt"],
    )

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
        concepts=["us-gaap_NetCashProvidedByUsedInOperatingActivities"],
        labels=[
            "Net Cash from Operating Activities",
            "Net Cash Provided by Operating Activities",
        ],
    )
    capex = _find_row(
        df,
        concepts=[
            "us-gaap_PaymentsToAcquirePropertyPlantAndEquipment",
            "us-gaap_PaymentsToAcquireProductiveAssets",
        ],
        labels=[
            "Payments to Acquire Property, Plant, and Equipment",
            "Capital Expenditures",
            "Capital spending",
            "Purchases of Property and Equipment",
        ],
    )
    depreciation = _find_row(
        df,
        concepts=["us-gaap_DepreciationDepletionAndAmortization"],
        labels=[
            "Depreciation and Amortization",
            "Depreciation and amortization",
            "Depreciation",
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


def _get_statement(financials, names: Iterable[str]):
    if financials is None:
        return None
    for name in names:
        attr = getattr(financials, name, None)
        if attr is None:
            continue
        try:
            return attr() if callable(attr) else attr
        except Exception:
            continue
    return None


def _normalize_filings(filings) -> List:
    if filings is None:
        return []
    if isinstance(filings, list):
        return filings
    try:
        return list(filings)
    except TypeError:
        return [filings]


def _latest_n_filings(company, form: str, n: int) -> List:
    try:
        return _normalize_filings(company.latest(form, n=n))
    except Exception:
        return []


def _statement_df_from_xbrls(xbrls, method_name: str, max_periods: int):
    if xbrls is None:
        return None
    stmt_getter = getattr(xbrls.statements, method_name, None)
    if stmt_getter is None:
        return None
    try:
        statement = stmt_getter(max_periods=max_periods, standardize=True)
    except TypeError:
        try:
            statement = stmt_getter()
        except Exception:
            return None
    except Exception:
        return None
    if statement is None:
        return None
    try:
        df = statement.to_dataframe()
    except Exception:
        return None
    return _prepare_statement_df(df)

def _fetch_url(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "ignore")
    except (HTTPError, URLError, ValueError):
        return None


def _parse_table_rows(html: str) -> dict:
    if not html or BeautifulSoup is None:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    rows: dict = {}
    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 2:
            continue
        label = tds[0].get_text(" ", strip=True)
        value = tds[1].get_text(" ", strip=True)
        label = " ".join(label.split())
        value = " ".join(value.split())
        if label and value:
            rows[label] = value
    return rows


def _parse_float(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    cleaned = value.replace(",", "")
    match = re.search(r"[-+]?\d*\.?\d+", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _parse_compact_number(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    token = value.replace(",", "").strip().split()[0]
    match = re.match(r"([-+]?\d*\.?\d+)([KMBT])?", token, re.IGNORECASE)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2)
    multiplier = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
    if suffix:
        number *= multiplier.get(suffix.upper(), 1)
    return number


def _normalize_phone(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return value.strip()


def _normalize_website(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"https://{value}"


def _parse_address_lines(value: Optional[str]) -> Tuple[str, str, str, str]:
    if not value:
        return "", "", "", ""
    lines = [line.strip() for line in str(value).splitlines() if line.strip()]
    address = lines[0].title() if lines else ""
    city = ""
    state = ""
    postal = ""
    if len(lines) > 1:
        match = re.match(r"(.+),\s*([A-Z]{2})\s*(\\d{5}(?:-\\d{4})?)?", lines[1].strip())
        if match:
            city = match.group(1).title()
            state = match.group(2)
            postal = match.group(3) or ""
        else:
            city = lines[1].title()
    return address, city, state, postal


def _stockanalysis_company_data(ticker: str) -> dict:
    html = _fetch_url(f"https://stockanalysis.com/stocks/{ticker.lower()}/company/")
    rows = _parse_table_rows(html or "")
    return rows


def _stockanalysis_market_data(ticker: str) -> dict:
    html = _fetch_url(f"https://stockanalysis.com/stocks/{ticker.lower()}/")
    if not html or BeautifulSoup is None:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    rows = _parse_table_rows(html)

    price = None
    price_tag = soup.find("div", class_=re.compile(r"text-4xl"))
    if price_tag:
        price = _parse_float(price_tag.get_text(" ", strip=True))

    change = None
    change_pct = None
    change_tag = soup.find("div", class_=re.compile(r"text-(green|red)-vivid"))
    if change_tag:
        text = change_tag.get_text(" ", strip=True)
        match = re.search(r"([-+]?\d*\.?\d+)\s*\\(([-+]?\d*\.?\d+)%\\)", text)
        if match:
            change = _parse_float(match.group(1))
            change_pct = _parse_float(match.group(2))

    market_cap = _parse_compact_number(rows.get("Market Cap"))
    volume = _parse_float(rows.get("Volume"))
    beta = _parse_float(rows.get("Beta"))
    dividend = rows.get("Dividend")
    last_dividend = _parse_float(dividend)
    week_range = rows.get("52-Week Range") or rows.get("52 Week Range")

    return {
        "price": price,
        "marketCap": market_cap,
        "beta": beta,
        "lastDividend": last_dividend,
        "range": week_range,
        "change": change,
        "changePercentage": change_pct,
        "volume": volume,
    }


def _yahoo_quote(ticker: str) -> dict:
    html = _fetch_url(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}")
    if not html:
        return {}
    try:
        data = json.loads(html)
        result = data.get("quoteResponse", {}).get("result", [])
        if not result:
            return {}
        quote = result[0]
    except Exception:
        return {}

    low = quote.get("fiftyTwoWeekLow")
    high = quote.get("fiftyTwoWeekHigh")
    week_range = None
    if low is not None and high is not None:
        week_range = f"{float(low):.2f}-{float(high):.2f}"

    change_pct = quote.get("regularMarketChangePercent")
    if change_pct is not None:
        try:
            change_pct = float(change_pct) * 100.0
        except Exception:
            change_pct = None

    return {
        "price": quote.get("regularMarketPrice"),
        "marketCap": quote.get("marketCap"),
        "beta": quote.get("beta"),
        "lastDividend": quote.get("trailingAnnualDividendRate"),
        "range": week_range,
        "change": quote.get("regularMarketChange"),
        "changePercentage": change_pct,
        "volume": quote.get("regularMarketVolume"),
        "companyName": quote.get("longName") or quote.get("shortName"),
        "currency": quote.get("currency"),
        "exchange": quote.get("exchange"),
        "exchangeFullName": quote.get("fullExchangeName"),
    }


def _write_company_profile(company, data_dir: Path, ticker: str, currency: str):
    pd = _require_pandas()
    if BeautifulSoup is None:
        raise ImportError(
            "beautifulsoup4 is required to build company_profile.csv. "
            "Install dependencies with `python -m pip install -r requirements.txt`."
        )

    data = getattr(company, "data", None)
    name = None
    cik = None
    website = None
    phone = None
    business_address = None
    if data is not None:
        name = getattr(data, "name", None) or getattr(data, "company_name", None)
        cik = getattr(data, "cik", None)
        website = getattr(data, "website", None)
        phone = getattr(data, "phone", None)
        business_address = getattr(data, "business_address", None)

    if not name:
        name = getattr(company, "name", None) or getattr(company, "company_name", None)

    if name and name.isupper():
        name = name.title()

    address, city, state, postal = _parse_address_lines(business_address)

    company_rows = _stockanalysis_company_data(ticker)
    market_rows = _stockanalysis_market_data(ticker)
    yahoo_rows = _yahoo_quote(ticker)

    def _fill_missing(target: dict, source: dict, keys: Iterable[str]) -> dict:
        for key in keys:
            if target.get(key) in (None, "") and source.get(key) not in (None, ""):
                target[key] = source[key]
        return target

    market_rows = _fill_missing(
        market_rows or {},
        yahoo_rows,
        [
            "price",
            "marketCap",
            "beta",
            "lastDividend",
            "range",
            "change",
            "changePercentage",
            "volume",
        ],
    )

    reporting_currency = company_rows.get("Reporting Currency") or yahoo_rows.get("currency")
    if reporting_currency:
        currency = reporting_currency

    exchange = company_rows.get("Exchange") or yahoo_rows.get("exchange")
    exchange_full_map = {
        "NASDAQ": "Nasdaq Global Select Market",
        "NYSE": "New York Stock Exchange",
    }
    exchange_full = yahoo_rows.get("exchangeFullName") or exchange_full_map.get(exchange, exchange or "")

    stock_type = (company_rows.get("Stock Type") or "").lower()
    is_etf = "etf" in stock_type
    is_adr = "adr" in stock_type or "depositary" in stock_type
    is_actively_trading = bool(exchange)

    company_rows_norm = {k: v for k, v in company_rows.items()}

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
        "companyName",
        "currency",
        "cik",
        "isin",
        "cusip",
        "exchangeFullName",
        "exchange",
        "industry",
        "website",
        "ceo",
        "sector",
        "country",
        "fullTimeEmployees",
        "phone",
        "address",
        "city",
        "state",
        "zip",
        "ipoDate",
        "isEtf",
        "isActivelyTrading",
        "isAdr",
    ]
    row = {col: "" for col in columns}
    row["symbol"] = ticker
    if not name:
        name = yahoo_rows.get("companyName")
    row["companyName"] = name or ticker
    row["currency"] = currency

    cik_value = company_rows_norm.get("CIK Code") or cik
    if cik_value is not None:
        try:
            cik_int = int(str(cik_value).strip())
            row["cik"] = f"{cik_int:010d}"
        except ValueError:
            row["cik"] = str(cik_value)

    row["isin"] = company_rows_norm.get("ISIN Number", "")
    row["cusip"] = company_rows_norm.get("CUSIP Number", "")
    row["exchange"] = exchange or ""
    row["exchangeFullName"] = exchange_full
    row["industry"] = company_rows_norm.get("Industry", "")
    row["sector"] = company_rows_norm.get("Sector", "")
    row["country"] = company_rows_norm.get("Country", "")
    row["ceo"] = company_rows_norm.get("CEO", "")

    employees = company_rows_norm.get("Employees")
    if employees:
        row["fullTimeEmployees"] = re.sub(r"[^\d]", "", employees)

    row["website"] = _normalize_website(company_rows_norm.get("Website") or website) or ""
    row["phone"] = _normalize_phone(company_rows_norm.get("Phone") or phone) or ""

    row["address"] = address
    row["city"] = city
    row["state"] = state
    row["zip"] = postal

    row["price"] = market_rows.get("price") if market_rows else ""
    row["marketCap"] = market_rows.get("marketCap") if market_rows else ""
    row["beta"] = market_rows.get("beta") if market_rows else ""
    row["lastDividend"] = market_rows.get("lastDividend") if market_rows else ""
    row["range"] = market_rows.get("range") if market_rows else ""
    row["change"] = market_rows.get("change") if market_rows else ""
    row["changePercentage"] = market_rows.get("changePercentage") if market_rows else ""
    row["volume"] = market_rows.get("volume") if market_rows else ""

    row["isEtf"] = "true" if is_etf else "false"
    row["isAdr"] = "true" if is_adr else "false"
    row["isActivelyTrading"] = "true" if is_actively_trading else "false"

    df = pd.DataFrame([row])
    df.to_csv(data_dir / "company_profile.csv", index=False)


def fetch_company_financials(ticker: str, data_dir: Path, identity: Optional[str] = None) -> None:
    ensure_edgar_identity(identity)
    from edgar import Company  # type: ignore
    from edgar.xbrl import XBRLS  # type: ignore

    pd = _require_pandas()
    company = Company(ticker)
    currency = "USD"

    _write_company_profile(company, data_dir, ticker, currency)

    try:
        is_fpi = len(company.get_filings(form="20-F")) > 0
    except Exception:
        is_fpi = False

    annual_form = "20-F" if is_fpi else "10-K"
    candidate_forms: List[Tuple[str, int]] = [(annual_form, 6)]
    candidate_forms.append(("6-K", 12) if is_fpi else ("10-Q", 12))
    candidate_forms.extend(
        [
            ("S-1/A", 6),
            ("S-1", 6),
            ("F-1/A", 6),
            ("F-1", 6),
        ]
    )

    annual_dir = data_dir / "financial_statements" / "annual"
    annual_dir.mkdir(parents=True, exist_ok=True)

    annual_source_form = None
    annual_income_full = None
    annual_balance_full = None
    annual_cash_full = None
    annual_equity_full = None
    annual_comp_full = None

    for form, max_filings in candidate_forms:
        annual_filings = _latest_n_filings(company, form=form, n=max_filings)
        if not annual_filings:
            continue
        try:
            annual_xbrls = XBRLS.from_filings(annual_filings)
        except Exception as exc:
            print(f"Warning: unable to read XBRL from {form} filings for {ticker}: {exc}")
            continue

        candidate_income = _statement_df_from_xbrls(annual_xbrls, "income_statement", max_periods=8)
        candidate_balance = _statement_df_from_xbrls(annual_xbrls, "balance_sheet", max_periods=8)
        candidate_cash = _statement_df_from_xbrls(annual_xbrls, "cashflow_statement", max_periods=8)
        candidate_equity = _statement_df_from_xbrls(annual_xbrls, "statement_of_equity", max_periods=8)
        candidate_comp = _statement_df_from_xbrls(annual_xbrls, "comprehensive_income", max_periods=8)

        if all(
            stmt is None
            for stmt in (
                candidate_income,
                candidate_balance,
                candidate_cash,
                candidate_equity,
                candidate_comp,
            )
        ):
            print(f"Warning: no statement tables found in {form} filings for {ticker}.")
            continue

        annual_source_form = form
        annual_income_full = candidate_income
        annual_balance_full = candidate_balance
        annual_cash_full = candidate_cash
        annual_equity_full = candidate_equity
        annual_comp_full = candidate_comp
        break

    if annual_source_form and annual_source_form != annual_form:
        print(
            f"Warning: using {annual_source_form} filings as annual financial source because {annual_form} is unavailable for {ticker}."
        )
    if annual_source_form is None:
        forms_display = ", ".join(form for form, _ in candidate_forms)
        print(f"Warning: no XBRL financial statements available for {ticker} from forms: {forms_display}")

    if annual_income_full is not None:
        annual_income_full.to_csv(annual_dir / "income_statement.csv", index=False)
    if annual_balance_full is not None:
        annual_balance_full.to_csv(annual_dir / "balance_sheet.csv", index=False)
    if annual_cash_full is not None:
        annual_cash_full.to_csv(annual_dir / "cash_flow_statement.csv", index=False)
    if annual_equity_full is not None:
        annual_equity_full.to_csv(annual_dir / "statement_of_equity.csv", index=False)
    if annual_comp_full is not None:
        annual_comp_full.to_csv(annual_dir / "comprehensive_income.csv", index=False)

    income_annual = _build_income_statement(annual_income_full, ticker, "FY", currency)
    balance_annual = _build_balance_sheet(annual_balance_full, ticker, "FY", currency)
    cash_annual = _build_cash_flow(annual_cash_full, ticker, "FY", currency)

    if income_annual.empty or balance_annual.empty or cash_annual.empty:
        print(
            "Warning: unable to parse complete annual financial statements from EDGAR. "
            "Continuing with available filings/profile data."
        )

    if not income_annual.empty and not cash_annual.empty:
        merged = income_annual.merge(
            cash_annual[["date", "depreciationAndAmortization"]],
            on="date",
            how="left",
        )
        income_annual["ebitda"] = merged["ebit"] + merged["depreciationAndAmortization"].fillna(0)

    if not is_fpi:
        quarterly_filings = _latest_n_filings(company, "10-Q", n=12)
    else:
        quarterly_filings = []

    quarterly_dir = data_dir / "financial_statements" / "quarterly"
    quarterly_dir.mkdir(parents=True, exist_ok=True)

    if quarterly_filings:
        quarterly_xbrls = XBRLS.from_filings(quarterly_filings)
        quarterly_income_full = _statement_df_from_xbrls(quarterly_xbrls, "income_statement", max_periods=12)
        quarterly_balance_full = _statement_df_from_xbrls(quarterly_xbrls, "balance_sheet", max_periods=12)
        quarterly_cash_full = _statement_df_from_xbrls(quarterly_xbrls, "cashflow_statement", max_periods=12)
        quarterly_equity_full = _statement_df_from_xbrls(quarterly_xbrls, "statement_of_equity", max_periods=12)
        quarterly_comp_full = _statement_df_from_xbrls(quarterly_xbrls, "comprehensive_income", max_periods=12)

        if quarterly_income_full is not None:
            quarterly_income_full.to_csv(quarterly_dir / "income_statement.csv", index=False)
        if quarterly_balance_full is not None:
            quarterly_balance_full.to_csv(quarterly_dir / "balance_sheet.csv", index=False)
        if quarterly_cash_full is not None:
            quarterly_cash_full.to_csv(quarterly_dir / "cash_flow_statement.csv", index=False)
        if quarterly_equity_full is not None:
            quarterly_equity_full.to_csv(quarterly_dir / "statement_of_equity.csv", index=False)
        if quarterly_comp_full is not None:
            quarterly_comp_full.to_csv(quarterly_dir / "comprehensive_income.csv", index=False)

        income_q = _build_income_statement(quarterly_income_full, ticker, "Q", currency)
        balance_q = _build_balance_sheet(quarterly_balance_full, ticker, "Q", currency)
        cash_q = _build_cash_flow(quarterly_cash_full, ticker, "Q", currency)
    else:
        income_q = pd.DataFrame()
        balance_q = pd.DataFrame()
        cash_q = pd.DataFrame()

    if not income_q.empty and not cash_q.empty:
        merged_q = income_q.merge(
            cash_q[["date", "depreciationAndAmortization"]],
            on="date",
            how="left",
        )
        income_q["ebitda"] = merged_q["ebit"] + merged_q["depreciationAndAmortization"].fillna(0)
