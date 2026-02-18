from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Dict

from data_paths import resolve_data_root


@dataclass
class CompanyData:
    income_annual: "pd.DataFrame"
    balance_annual: "pd.DataFrame"
    cashflow_annual: "pd.DataFrame"
    profile: "pd.DataFrame"
    key_metrics: "pd.DataFrame | None" = None
    ratios: "pd.DataFrame | None" = None
    analyst_estimates: "pd.DataFrame | None" = None


def _require_pandas():
    try:
        import pandas as pd  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise ImportError(
            "pandas is required. Install with "
            "packages listed in `.agents/skills/fetch-us-company-data/agents/openai.yaml`."
        ) from exc
    return pd


def _load_csv(path: Path):
    pd = _require_pandas()
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


_DATE_COL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _period_columns(df):
    cols = []
    for col in df.columns:
        if _DATE_COL_RE.match(str(col)):
            cols.append(col)
    return cols


def _find_row(df, concepts, labels):
    if "concept" in df.columns:
        for concept in concepts:
            matches = df[df["concept"].str.lower() == concept.lower()]
            if not matches.empty:
                return matches.iloc[0]
    if "label" in df.columns:
        for label in labels:
            matches = df[df["label"].str.contains(label, case=False, na=False, regex=False)]
            if not matches.empty:
                return matches.iloc[0]
    return None


def _attach_metric(df, series, name, period_cols):
    pd = _require_pandas()
    if series is None:
        df[name] = pd.NA
        return
    values = [series.get(col) for col in period_cols]
    df[name] = pd.to_numeric(values, errors="coerce")


def _build_base_frame(period_cols, ticker, period_label, currency):
    pd = _require_pandas()
    dates = [pd.to_datetime(col, errors="coerce").date() for col in period_cols]
    return pd.DataFrame(
        {
            "date": [d.isoformat() if d is not None else "" for d in dates],
            "symbol": ticker,
            "reportedCurrency": currency or "",
            "fiscalYear": [d.year if d is not None else None for d in dates],
            "period": period_label,
        }
    )


def _build_income_from_financials(df, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    period_cols = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, ticker, period_label, currency)

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
    operating_income = _find_row(
        df,
        concepts=["us-gaap_OperatingIncomeLoss"],
        labels=["Operating Income", "Operating Income (Loss)", "Operating Income Loss"],
    )
    income_before_tax = _find_row(
        df,
        concepts=[
            "us-gaap_IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "us-gaap_IncomeLossBeforeIncomeTaxes",
        ],
        labels=["Income Before Tax", "Income Before Taxes", "Income (Loss) Before Income Taxes"],
    )
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
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out


def _build_balance_from_financials(df, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    period_cols = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, ticker, period_label, currency)

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
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out


def _build_cash_from_financials(df, ticker: str, period_label: str, currency: str):
    pd = _require_pandas()
    period_cols = _period_columns(df)
    if not period_cols:
        return pd.DataFrame()

    out = _build_base_frame(period_cols, ticker, period_label, currency)

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

    if "operatingCashFlow" in out.columns and "capitalExpenditure" in out.columns:
        capex_values = pd.to_numeric(out["capitalExpenditure"], errors="coerce").fillna(0.0)
        ocf_values = pd.to_numeric(out["operatingCashFlow"], errors="coerce").fillna(0.0)
        fcf = ocf_values + capex_values
        if (capex_values > 0).any():
            fcf = ocf_values - capex_values.abs()
        out["freeCashFlow"] = fcf
    else:
        out["freeCashFlow"] = pd.NA

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out


def _normalize_share_counts(df):
    pd = _require_pandas()
    for col in ("weightedAverageShsOut", "weightedAverageShsOutDil"):
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        values = series.dropna()
        values = values[values > 0]
        if len(values) < 2:
            continue
        median = values.median()
        if median <= 0:
            continue

        adjusted = series.copy()
        for idx, value in series.items():
            if pd.isna(value) or value <= 0:
                continue
            ratio = value / median
            if ratio <= 5:
                continue
            while ratio > 5 and value >= 1_000_000:
                value /= 10
                ratio = value / median
            adjusted.loc[idx] = value
        df[col] = adjusted


def _resolve_data_dir(ticker: str) -> Path:
    companies_dir = resolve_data_root() / "companies"
    normalized = ticker.upper()

    direct_candidates = [
        companies_dir / "US" / normalized / "data",
    ]
    for candidate in direct_candidates:
        if candidate.exists():
            return candidate

    if not companies_dir.exists():
        raise FileNotFoundError(f"Missing companies directory: {companies_dir}")

    for country_dir in companies_dir.iterdir():
        if not country_dir.is_dir():
            continue
        for candidate in country_dir.iterdir():
            if not candidate.is_dir():
                continue
            if candidate.name.upper() != normalized:
                continue
            data_dir = candidate / "data"
            if data_dir.exists():
                return data_dir

    raise FileNotFoundError(
        "Missing data directory for "
        f"{ticker}. Expected canonical layout under "
        f"{companies_dir / '<COUNTRY>' / normalized / 'data'} "
        "with country as ISO alpha-2 (for example US, JP, GB)."
    )


def load_company_data(ticker: str) -> CompanyData:
    data_dir = _resolve_data_dir(ticker)

    profile = _load_csv(data_dir / "company_profile.csv")
    currency = ""
    if not profile.empty and "currency" in profile.columns:
        currency = str(profile.iloc[0].get("currency") or "")

    financials_annual_dir = data_dir / "financial_statements" / "annual"
    income = None
    balance = None
    cashflow = None

    if financials_annual_dir.exists():
        income_path = financials_annual_dir / "income_statement.csv"
        balance_path = financials_annual_dir / "balance_sheet.csv"
        cash_path = financials_annual_dir / "cash_flow_statement.csv"

        if income_path.exists():
            income_df = _load_csv(income_path)
            income = _build_income_from_financials(income_df, ticker, "FY", currency)
        if balance_path.exists():
            balance_df = _load_csv(balance_path)
            balance = _build_balance_from_financials(balance_df, ticker, "FY", currency)
        if cash_path.exists():
            cash_df = _load_csv(cash_path)
            cashflow = _build_cash_from_financials(cash_df, ticker, "FY", currency)

    if income is None or income.empty:
        raise FileNotFoundError(
            f"Missing parseable annual income statement for {ticker}. "
            "Expected data/financial_statements/annual/income_statement.csv."
        )
    if balance is None or balance.empty:
        raise FileNotFoundError(
            f"Missing parseable annual balance sheet for {ticker}. "
            "Expected data/financial_statements/annual/balance_sheet.csv."
        )
    if cashflow is None or cashflow.empty:
        raise FileNotFoundError(
            f"Missing parseable annual cash flow for {ticker}. "
            "Expected data/financial_statements/annual/cash_flow_statement.csv."
        )

    if not income.empty and not cashflow.empty and "depreciationAndAmortization" in cashflow.columns:
        try:
            pd = _require_pandas()
            merged = income.merge(
                cashflow[["date", "depreciationAndAmortization"]],
                on="date",
                how="left",
            )
            ebit = pd.to_numeric(merged["ebit"], errors="coerce")
            da = pd.to_numeric(merged["depreciationAndAmortization"], errors="coerce").fillna(0.0)
            income["ebitda"] = ebit + da
        except Exception:
            pass

    if not income.empty:
        _normalize_share_counts(income)

    key_metrics_path = data_dir / "key_metrics.csv"
    ratios_path = data_dir / "ratios.csv"
    analyst_estimates_candidates = [
        data_dir / "analyst_revenue_estimates.csv",
    ]

    key_metrics = _load_csv(key_metrics_path) if key_metrics_path.exists() else None
    ratios = _load_csv(ratios_path) if ratios_path.exists() else None
    analyst_estimates = None
    for analyst_estimates_path in analyst_estimates_candidates:
        if not analyst_estimates_path.exists():
            continue
        analyst_estimates = _load_csv(analyst_estimates_path)
        break

    return CompanyData(
        income_annual=income,
        balance_annual=balance,
        cashflow_annual=cashflow,
        profile=profile,
        key_metrics=key_metrics,
        ratios=ratios,
        analyst_estimates=analyst_estimates,
    )
