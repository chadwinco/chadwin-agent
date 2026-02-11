from __future__ import annotations

from typing import Dict

from loaders import CompanyData, _require_pandas


def _to_numeric(df, columns, pd):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def compute_metrics(data: CompanyData) -> Dict:
    pd = _require_pandas()

    income = data.income_annual.copy()
    balance = data.balance_annual.copy()
    cashflow = data.cashflow_annual.copy()

    income = income.sort_values("date").groupby("fiscalYear", as_index=True).last()
    balance = balance.sort_values("date").groupby("fiscalYear", as_index=True).last()
    cashflow = cashflow.sort_values("date").groupby("fiscalYear", as_index=True).last()

    annual = income.join(balance, rsuffix="_bs").join(cashflow, rsuffix="_cf")
    annual = annual.reset_index()

    numeric_cols = [
        "revenue",
        "grossProfit",
        "ebit",
        "ebitda",
        "incomeBeforeTax",
        "incomeTaxExpense",
        "operatingCashFlow",
        "capitalExpenditure",
        "freeCashFlow",
        "totalDebt",
        "totalEquity",
        "cashAndCashEquivalents",
        "netDebt",
        "totalAssets",
    ]
    annual = _to_numeric(annual, [c for c in numeric_cols if c in annual.columns], pd)

    if "freeCashFlow" not in annual.columns or annual["freeCashFlow"].isna().all():
        if "operatingCashFlow" in annual.columns and "capitalExpenditure" in annual.columns:
            annual["freeCashFlow"] = annual["operatingCashFlow"] + annual["capitalExpenditure"]

    annual["revenue_growth"] = annual["revenue"].pct_change()
    if "grossProfit" in annual.columns:
        annual["gross_margin"] = annual["grossProfit"] / annual["revenue"]
    annual["ebit_margin"] = annual["ebit"] / annual["revenue"]
    annual["fcf_margin"] = annual["freeCashFlow"] / annual["revenue"]

    tax_rate = annual["incomeTaxExpense"] / annual["incomeBeforeTax"]
    tax_rate = tax_rate.fillna(0.21).clip(lower=0, upper=0.5)
    annual["nopat"] = annual["ebit"] * (1 - tax_rate)

    if "netDebt" in annual.columns:
        annual["net_debt"] = annual["netDebt"]
    else:
        annual["net_debt"] = annual["totalDebt"] - annual["cashAndCashEquivalents"]

    annual["invested_capital"] = (
        annual["totalDebt"] + annual["totalEquity"] - annual["cashAndCashEquivalents"]
    )
    annual["roic"] = annual["nopat"] / annual["invested_capital"]
    annual["reinvestment_rate"] = annual["capitalExpenditure"].abs() / annual["revenue"]

    if "ebitda" in annual.columns:
        annual["leverage"] = annual["net_debt"] / annual["ebitda"]
    else:
        annual["leverage"] = pd.NA

    latest = annual.tail(1).iloc[0]
    latest_year = int(latest["fiscalYear"])

    metrics = {
        "latest_year": latest_year,
        "latest_revenue": float(latest["revenue"]),
        "latest_ebit": float(latest["ebit"]),
        "latest_fcf": float(latest["freeCashFlow"]),
        "latest_net_debt": float(latest["net_debt"]),
        "avg_revenue_growth": float(annual["revenue_growth"].mean()),
        "avg_ebit_margin": float(annual["ebit_margin"].mean()),
        "avg_fcf_margin": float(annual["fcf_margin"].mean()),
        "avg_roic": float(annual["roic"].mean()),
        "avg_reinvestment_rate": float(annual["reinvestment_rate"].mean()),
        "avg_leverage": float(annual["leverage"].mean()),
    }

    # Build markdown table for the last 4 years
    recent = annual.tail(4)
    lines = [
        "| Fiscal Year | Revenue ($m) | EBIT ($m) | EBIT Margin | FCF ($m) | FCF Margin | Net Debt ($m) | ROIC |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in recent.iterrows():
        lines.append(
            "| {year} | {rev:.1f} | {ebit:.1f} | {ebit_margin:.1%} | {fcf:.1f} | {fcf_margin:.1%} | {net_debt:.1f} | {roic:.1%} |".format(
                year=int(row["fiscalYear"]),
                rev=row["revenue"] / 1e6,
                ebit=row["ebit"] / 1e6,
                ebit_margin=row["ebit_margin"],
                fcf=row["freeCashFlow"] / 1e6,
                fcf_margin=row["fcf_margin"],
                net_debt=row["net_debt"] / 1e6,
                roic=row["roic"],
            )
        )

    metrics["financial_table"] = "\n".join(lines)
    metrics["annual"] = annual

    return metrics
