from __future__ import annotations

from pathlib import Path
from typing import Dict

from .loaders import CompanyData, _require_pandas


def load_assumptions(path: Path) -> Dict:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise ImportError(
            "pyyaml is required. Install with `python3 -m pip install -r requirements.txt`."
        ) from exc

    with path.open("r") as f:
        return yaml.safe_load(f)


def _get_latest_row(df):
    df = df.sort_values("date")
    return df.iloc[-1]


def _get_shares_outstanding(income_df):
    latest = _get_latest_row(income_df)
    for col in ("weightedAverageShsOutDil", "weightedAverageShsOut"):
        if col not in income_df.columns:
            continue
        value = latest.get(col)
        if value is None:
            continue
        try:
            if value == value:
                return float(value)
        except Exception:
            continue
    return None


def _get_current_price(profile_df):
    if profile_df.empty:
        return None
    price = profile_df.iloc[0].get("price")
    return float(price) if price == price else None


def _get_market_cap(profile_df):
    if profile_df.empty:
        return None
    cap = profile_df.iloc[0].get("marketCap")
    return float(cap) if cap == cap else None


def run_valuation(data: CompanyData, assumptions: Dict, metrics: Dict) -> Dict:
    _require_pandas()

    income = data.income_annual.copy()
    balance = data.balance_annual.copy()
    profile = data.profile.copy()

    latest_income = _get_latest_row(income)
    latest_balance = _get_latest_row(balance)

    latest_revenue = float(latest_income["revenue"])
    net_debt = float(
        latest_balance["netDebt"]
        if "netDebt" in balance.columns
        else latest_balance["totalDebt"] - latest_balance["cashAndCashEquivalents"]
    )

    shares_out = _get_shares_outstanding(income)
    price = _get_current_price(profile)
    market_cap = _get_market_cap(profile)

    if shares_out is None and market_cap and price:
        shares_out = market_cap / price

    forecast_years = int(assumptions.get("forecast_years", 5))
    scenarios = assumptions.get("scenarios", {})

    results = {
        "inputs": {
            "latest_revenue": latest_revenue,
            "net_debt": net_debt,
            "shares_outstanding": shares_out,
            "current_price": price,
        },
        "scenarios": {},
    }

    for name, params in scenarios.items():
        growth = float(params["revenue_growth"])
        fcf_margin = float(params["fcf_margin"])
        discount = float(params["discount_rate"])
        terminal_growth = float(params["terminal_growth"])

        revenue = latest_revenue
        pv = 0.0
        fcf = 0.0

        for year in range(1, forecast_years + 1):
            revenue *= 1 + growth
            fcf = revenue * fcf_margin
            pv += fcf / ((1 + discount) ** year)

        terminal_value = (fcf * (1 + terminal_growth)) / (discount - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount) ** forecast_years)
        enterprise_value = pv + pv_terminal
        equity_value = enterprise_value - net_debt
        per_share = equity_value / shares_out if shares_out else None

        if per_share is None or per_share <= 0 or price is None:
            margin_of_safety = None
        else:
            margin_of_safety = (per_share - price) / per_share

        results["scenarios"][name] = {
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "per_share_value": per_share,
            "margin_of_safety": margin_of_safety,
            "assumptions": params,
        }

    lines = [
        "| Scenario | Implied Value/Share | Margin of Safety |",
        "| --- | --- | --- |",
    ]
    for name, scenario in results["scenarios"].items():
        per_share = scenario["per_share_value"]
        mos = scenario["margin_of_safety"]
        per_share_text = f"${per_share:,.2f}" if per_share is not None else "n/a"
        mos_text = f"{mos:.1%}" if mos is not None else "n/a"
        lines.append(f"| {name.title()} | {per_share_text} | {mos_text} |")

    results["valuation_table"] = "\n".join(lines)

    return results
