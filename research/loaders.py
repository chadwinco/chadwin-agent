from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


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
            "pandas is required. Install with `python3 -m pip install -r requirements.txt`."
        ) from exc
    return pd


def _load_csv(path: Path):
    pd = _require_pandas()
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_company_data(base_dir: Path, ticker: str) -> CompanyData:
    data_dir = base_dir / "companies" / ticker / "data"
    if not data_dir.exists():
        raise FileNotFoundError(f"Missing data directory: {data_dir}")

    income = _load_csv(data_dir / "income_statement_annual.csv")
    balance = _load_csv(data_dir / "balance_sheet_annual.csv")
    cashflow = _load_csv(data_dir / "cash_flow_statement_annual.csv")
    profile = _load_csv(data_dir / "company_profile.csv")

    key_metrics_path = data_dir / "key_metrics.csv"
    ratios_path = data_dir / "ratios.csv"
    analyst_estimates_path = data_dir / "analyst_estimates.csv"

    key_metrics = _load_csv(key_metrics_path) if key_metrics_path.exists() else None
    ratios = _load_csv(ratios_path) if ratios_path.exists() else None
    analyst_estimates = (
        _load_csv(analyst_estimates_path) if analyst_estimates_path.exists() else None
    )

    return CompanyData(
        income_annual=income,
        balance_annual=balance,
        cashflow_annual=cashflow,
        profile=profile,
        key_metrics=key_metrics,
        ratios=ratios,
        analyst_estimates=analyst_estimates,
    )
