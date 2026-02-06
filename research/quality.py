from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .loaders import CompanyData


@dataclass
class QualityIssue:
    severity: str
    message: str


def _check_required_columns(df, required, label) -> List[QualityIssue]:
    missing = [c for c in required if c not in df.columns]
    if missing:
        return [QualityIssue("error", f"{label} missing columns: {missing}")]
    return []


def run_quality_checks(data: CompanyData) -> List[QualityIssue]:
    issues: List[QualityIssue] = []

    issues += _check_required_columns(
        data.income_annual,
        [
            "date",
            "fiscalYear",
            "revenue",
            "ebit",
            "incomeBeforeTax",
            "incomeTaxExpense",
            "weightedAverageShsOut",
        ],
        "income_statement_annual",
    )
    issues += _check_required_columns(
        data.balance_annual,
        [
            "date",
            "fiscalYear",
            "cashAndCashEquivalents",
            "totalDebt",
            "totalEquity",
        ],
        "balance_sheet_annual",
    )
    issues += _check_required_columns(
        data.cashflow_annual,
        [
            "date",
            "fiscalYear",
            "operatingCashFlow",
            "capitalExpenditure",
        ],
        "cash_flow_statement_annual",
    )

    # Basic numeric sanity checks
    for label, df, column in [
        ("income_statement_annual", data.income_annual, "revenue"),
        ("balance_sheet_annual", data.balance_annual, "totalEquity"),
        ("balance_sheet_annual", data.balance_annual, "totalAssets"),
    ]:
        if column in df.columns:
            invalid = df[df[column].isna()]
            if not invalid.empty:
                issues.append(
                    QualityIssue("warn", f"{label} has missing values in {column}.")
                )
            if column == "revenue":
                negative = df[df[column] < 0]
                if not negative.empty:
                    issues.append(
                        QualityIssue("warn", f"{label} has negative revenue values.")
                    )

    # Date alignment by fiscal year
    if "fiscalYear" in data.income_annual.columns and "fiscalYear" in data.cashflow_annual.columns:
        income_years = set(data.income_annual["fiscalYear"].dropna().astype(int))
        cash_years = set(data.cashflow_annual["fiscalYear"].dropna().astype(int))
        missing = income_years.symmetric_difference(cash_years)
        if missing:
            issues.append(
                QualityIssue(
                    "warn",
                    f"Income vs cash flow fiscal years do not align: {sorted(missing)}",
                )
            )

    if "fiscalYear" in data.income_annual.columns and "fiscalYear" in data.balance_annual.columns:
        income_years = set(data.income_annual["fiscalYear"].dropna().astype(int))
        balance_years = set(data.balance_annual["fiscalYear"].dropna().astype(int))
        missing = income_years.symmetric_difference(balance_years)
        if missing:
            issues.append(
                QualityIssue(
                    "warn",
                    f"Income vs balance sheet fiscal years do not align: {sorted(missing)}",
                )
            )

    return issues
