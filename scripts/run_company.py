#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from research.loaders import load_company_data  # noqa: E402
from research.metrics import compute_metrics  # noqa: E402
from research.quality import run_quality_checks  # noqa: E402
from research.valuation import load_assumptions, run_valuation  # noqa: E402


def _llm_placeholder(section: str, ticker: str, extra: str | None = None) -> str:
    note = (
        f"LLM_REQUIRED: Use .agents/skills/run-company-research/prompts/{section}.md "
        f"and search companies/{ticker}/data for evidence."
    )
    if extra:
        note = f"{note} {extra}"
    return note


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


def _report_dir(base_dir: Path, ticker: str, asof: str) -> Path:
    return base_dir / "companies" / ticker / "reports" / asof


def _assumptions_path(base_dir: Path, ticker: str, asof: str) -> Path:
    report_dir = _report_dir(base_dir, ticker, asof)
    assumptions_path = report_dir / "valuation" / "inputs.yaml"
    if assumptions_path.exists():
        return assumptions_path

    reports_dir = base_dir / "companies" / ticker / "reports"
    candidates = []
    for path in reports_dir.glob("*/valuation/inputs.yaml"):
        if path.parent.parent.name == asof:
            continue
        candidates.append(path)

    if not candidates:
        raise FileNotFoundError(
            f"Missing valuation inputs for {ticker} as of {asof}: "
            f"{assumptions_path}. Run .agents/skills/fetch-company-data/scripts/add_company.py first or create this file."
        )

    latest = sorted(candidates, key=lambda p: p.parent.parent.name)[-1]
    assumptions_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(latest, assumptions_path)
    return assumptions_path


def run_company(base_dir: Path, ticker: str, asof: str) -> None:
    data = load_company_data(base_dir, ticker)
    issues = run_quality_checks(data)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        for issue in issues:
            print(f"{issue.severity.upper()}: {issue.message}")
        raise SystemExit("Quality checks failed.")

    metrics = compute_metrics(data)

    assumptions_path = _assumptions_path(base_dir, ticker, asof)
    assumptions = load_assumptions(assumptions_path)
    valuation = run_valuation(data, assumptions, metrics)

    outputs_path = _report_dir(base_dir, ticker, asof) / "valuation" / "outputs.json"
    outputs_path.parent.mkdir(parents=True, exist_ok=True)
    outputs_path.write_text(json.dumps(valuation, indent=2))

    profile = data.profile.iloc[0]
    company_name = profile.get("companyName", ticker)
    price = valuation["inputs"].get("current_price")

    data_dir = base_dir / "companies" / ticker / "data"
    transcript_files = sorted((data_dir / "filings").glob("earnings-call-*.md"))
    if not transcript_files:
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

    def _fmt_bn(value):
        if value is None:
            return "n/a"
        return f"${value/1e9:,.1f}b"

    def _fmt_pct(value):
        return f"{value:.1%}" if value is not None else "n/a"

    def _fmt_ratio(value):
        if value is None or value != value:
            return "n/a"
        return f"{value:.1f}x"

    annual = metrics["annual"].sort_values("fiscalYear")
    latest = annual.iloc[-1]
    earliest = annual.iloc[0]
    net_debt_change = float(latest["net_debt"] - earliest["net_debt"])
    debt_direction = "decreased" if net_debt_change < 0 else "increased"
    capex_rate = metrics.get("avg_reinvestment_rate")

    capital_allocation = (
        f"Free cash flow averaged {_fmt_pct(metrics['avg_fcf_margin'])} of revenue over the last four fiscal years, "
        f"with reinvestment running at {_fmt_pct(capex_rate)}. Net debt {debt_direction} by {_fmt_bn(abs(net_debt_change))} "
        "over the same period, indicating how much of cash generation has gone to balance-sheet management."
    )

    business_overview = _llm_placeholder(
        "business-and-competitive-position",
        ticker,
        "Summarize products, customers, and geographies using filings and profile data.",
    )
    competitive_position = _llm_placeholder(
        "business-and-competitive-position",
        ticker,
        "Use margins and ROIC to support the moat discussion.",
    )
    key_risks = _llm_placeholder(
        "key-risks-and-disconfirming-signals",
        ticker,
        "Prioritize risks that impact cash generation and underwriting outcomes.",
    )

    exec_bullets = [
        f"{company_name} generated {_fmt_bn(metrics['latest_revenue'])} in FY{metrics['latest_year']} revenue.",
        f"Average EBIT margin {_fmt_pct(metrics['avg_ebit_margin'])} and ROIC {_fmt_pct(metrics['avg_roic'])} indicate strong operating leverage and capital efficiency.",
        f"Net debt stands at {_fmt_bn(metrics['latest_net_debt'])}, with leverage averaging {_fmt_ratio(metrics['avg_leverage'])} when measured against EBITDA.",
        f"Base-case DCF implies {_fmt_money(base_value)} per share vs. current price {_fmt_money(price)}, for a margin of safety of {_fmt_pct(base_mos)}.",
        "Top risks and qualitative drivers require LLM synthesis from filings and transcripts.",
    ]
    executive_summary = "\n".join([f"- {item}" for item in exec_bullets])

    context = {
        "company_name": company_name,
        "ticker": ticker,
        "asof_date": asof,
        "executive_summary": executive_summary,
        "business_overview": business_overview,
        "competitive_position": competitive_position,
        "financial_quality": (
            "Key metrics show average revenue growth of {rev_growth:.1%}, "
            "EBIT margin of {ebit_margin:.1%}, FCF margin of {fcf_margin:.1%}, "
            "and ROIC of {roic:.1%} over the last four fiscal years. "
            "Net debt to EBITDA averages {leverage}, providing a view of balance-sheet leverage."
        ).format(
            rev_growth=metrics["avg_revenue_growth"],
            ebit_margin=metrics["avg_ebit_margin"],
            fcf_margin=metrics["avg_fcf_margin"],
            roic=metrics["avg_roic"],
            leverage=_fmt_ratio(metrics["avg_leverage"]),
        ),
        "capital_allocation": capital_allocation,
        "key_risks": key_risks,
        "valuation_summary": (
            "Base-case DCF implies {value} per share versus current price {price}. "
            "Assumptions are summarized below."
        ).format(
            value=_fmt_money(base_value),
            price=_fmt_money(price),
        ),
        "margin_of_safety": (
            "Base-case margin of safety is {mos}. "
            "Interpret alongside leverage and cyclicality risks."
        ).format(mos=_fmt_pct(base_mos)),
        "conclusion": _llm_placeholder(
            "conclusion",
            ticker,
            "State the recommendation and list 2-3 next research steps.",
        ),
        "data_coverage": (
            f"Annual statements through fiscal year {metrics['latest_year']}. "
            "Source files: data/financial_statements/annual/income_statement.csv, "
            "data/financial_statements/annual/balance_sheet.csv, "
            "data/financial_statements/annual/cash_flow_statement.csv. "
            f"{transcript_note}"
        ),
        "financial_table": metrics["financial_table"],
        "valuation_table": valuation["valuation_table"],
        "assumptions_summary": _assumptions_summary(assumptions),
    }

    report_template = _read_template(base_dir / "templates" / "report.md")
    report = _render_template(report_template, context)

    report_dir = _report_dir(base_dir, ticker, asof)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.md"
    report_path.write_text(report)

    _append_source_log(base_dir, ticker, asof)

    print(f"Report written to {report_path}")


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
