#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from research.loaders import load_company_data  # noqa: E402
from research.metrics import compute_metrics  # noqa: E402
from research.quality import run_quality_checks  # noqa: E402
from research.valuation import load_assumptions, run_valuation  # noqa: E402


def _read_template(path: Path) -> str:
    return path.read_text()


def _render_template(template: str, context: dict) -> str:
    return template.format(**context)


def _append_source_log(base_dir: Path, ticker: str, asof_date: str):
    log_path = base_dir / "docs" / "source-log.md"
    if not log_path.exists():
        return
    entry = (
        f"| {asof_date} | {ticker} | Local Data Snapshot | "
        f"companies/{ticker}/data | Ingested CSVs and filings for analysis |\n"
    )
    content = log_path.read_text()
    if entry in content:
        return
    with log_path.open("a") as f:
        f.write(entry)


def _assumptions_summary(assumptions: dict) -> str:
    scenarios = assumptions.get("scenarios", {})
    lines = [
        "| Scenario | Revenue Growth | FCF Margin | Discount Rate | Terminal Growth |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, params in scenarios.items():
        lines.append(
            "| {name} | {growth:.1%} | {margin:.1%} | {discount:.1%} | {terminal:.1%} |".format(
                name=name.title(),
                growth=params["revenue_growth"],
                margin=params["fcf_margin"],
                discount=params["discount_rate"],
                terminal=params["terminal_growth"],
            )
        )
    return "\n".join(lines)


def run_company(base_dir: Path, ticker: str, asof: str) -> None:
    data = load_company_data(base_dir, ticker)
    issues = run_quality_checks(data)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        for issue in issues:
            print(f"{issue.severity.upper()}: {issue.message}")
        raise SystemExit("Quality checks failed.")

    metrics = compute_metrics(data)

    assumptions_path = base_dir / "companies" / ticker / "model" / "assumptions.yaml"
    assumptions = load_assumptions(assumptions_path)
    valuation = run_valuation(data, assumptions, metrics)

    outputs_path = base_dir / "companies" / ticker / "model" / "outputs.json"
    outputs_path.parent.mkdir(parents=True, exist_ok=True)
    outputs_path.write_text(json.dumps(valuation, indent=2))

    profile = data.profile.iloc[0]
    company_name = profile.get("companyName", ticker)
    price = valuation["inputs"].get("current_price")

    data_dir = base_dir / "companies" / ticker / "data"
    transcript_files = sorted(data_dir.glob("earnings-call-*.md"))
    transcript_note = (
        f"Earnings call transcript: {transcript_files[-1].name}."
        if transcript_files
        else "Earnings call transcript: not found."
    )

    base_case = valuation["scenarios"].get("base", {})
    base_value = base_case.get("per_share_value")
    base_mos = base_case.get("margin_of_safety")

    def _fmt_money(value):
        return f"${value:,.2f}" if value is not None else "n/a"

    def _fmt_pct(value):
        return f"{value:.1%}" if value is not None else "n/a"

    context = {
        "company_name": company_name,
        "ticker": ticker,
        "asof_date": asof,
        "executive_summary": "- TODO: Summarize thesis, valuation, and key risks.\n",
        "business_overview": "TODO: Summarize business model and segments using 10-K and profile.",
        "competitive_position": "TODO: Assess moat and competitive dynamics.",
        "financial_quality": (
            "Key metrics show average revenue growth of {rev_growth:.1%}, "
            "EBIT margin of {ebit_margin:.1%}, FCF margin of {fcf_margin:.1%}, "
            "and ROIC of {roic:.1%} over the last four fiscal years."
        ).format(
            rev_growth=metrics["avg_revenue_growth"],
            ebit_margin=metrics["avg_ebit_margin"],
            fcf_margin=metrics["avg_fcf_margin"],
            roic=metrics["avg_roic"],
        ),
        "capital_allocation": "TODO: Review reinvestment, debt paydown, and shareholder returns.",
        "growth_opportunities": "TODO: Identify credible long-term growth drivers.",
        "key_risks": "TODO: Summarize top risks from the 10-K and leverage profile.",
        "valuation_summary": (
            "Base-case DCF implies {value} per share versus current price {price}. "
            "Assumptions are in the appendix."
        ).format(
            value=_fmt_money(base_value),
            price=_fmt_money(price),
        ),
        "margin_of_safety": (
            "Base-case margin of safety is {mos}. "
            "Interpret alongside leverage and cyclicality risks."
        ).format(mos=_fmt_pct(base_mos)),
        "conclusion": "TODO: State recommendation and next research steps.",
        "data_coverage": (
            f"Annual statements through fiscal year {metrics['latest_year']}. "
            "Source files: data/financials/annual/income_statement.csv, "
            "data/financials/annual/balance_sheet.csv, "
            "data/financials/annual/cash_flow_statement.csv. "
            f"{transcript_note}"
        ),
        "financial_table": metrics["financial_table"],
        "valuation_table": valuation["valuation_table"],
        "assumptions_summary": _assumptions_summary(assumptions),
    }

    report_template = _read_template(base_dir / "templates" / "report.md")
    appendix_template = _read_template(base_dir / "templates" / "appendix.md")

    report = _render_template(report_template, context)
    appendix = _render_template(appendix_template, context)

    analysis_dir = base_dir / "companies" / ticker / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    report_path = analysis_dir / f"{asof}-report.md"
    appendix_path = analysis_dir / f"{asof}-appendix.md"
    report_path.write_text(report)
    appendix_path.write_text(appendix)

    _append_source_log(base_dir, ticker, asof)

    print(f"Report written to {report_path}")
    print(f"Appendix written to {appendix_path}")


def main():
    parser = argparse.ArgumentParser(description="Run research workflow for a company")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--asof", default=str(date.today()))
    parser.add_argument("--base-dir", default=str(BASE_DIR))

    args = parser.parse_args()
    base_dir = Path(args.base_dir)
    ticker = args.ticker.upper()

    run_company(base_dir, ticker, args.asof)


if __name__ == "__main__":
    main()
