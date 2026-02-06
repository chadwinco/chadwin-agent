#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from research.loaders import load_company_data  # noqa: E402
from research.metrics import compute_metrics  # noqa: E402
from research.quality import run_quality_checks  # noqa: E402
from research.valuation import load_assumptions, run_valuation  # noqa: E402


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _truncate_words(text: str, max_words: int = 120) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip() + "..."


def _paragraphs(text: str) -> list[str]:
    if not text:
        return []
    chunks = re.split(r"\n\s*\n", text)
    paragraphs = []
    for chunk in chunks:
        lines = []
        for line in chunk.splitlines():
            line = _strip_html(line).strip()
            if not line:
                continue
            if line.startswith("#"):
                stripped = re.sub(r"^#+", "", line).strip()
                if stripped and not stripped.lower().startswith(("item ", "part ")):
                    if lines:
                        paragraph = " ".join(lines).strip()
                        if len(paragraph) >= 40:
                            paragraphs.append(paragraph)
                    lines = []
                continue
            if line.lower().startswith("item ") or line.lower().startswith("part "):
                continue
            lines.append(line)
        if not lines:
            continue
        if lines:
            paragraph = " ".join(lines).strip()
            if len(paragraph) >= 40:
                paragraphs.append(paragraph)

    merged = []
    idx = 0
    while idx < len(paragraphs):
        paragraph = paragraphs[idx]
        while (
            idx + 1 < len(paragraphs)
            and not paragraph.strip().endswith((".", "!", "?"))
            and len(paragraph.split()) < 80
        ):
            paragraph = f"{paragraph} {paragraphs[idx + 1]}"
            idx += 1
        merged.append(paragraph)
        idx += 1
    return merged


def _find_section(text: str, start_patterns: list[str], end_patterns: list[str]) -> str:
    if not text:
        return ""
    start_positions = []
    for pattern in start_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            start_positions.append(match.start())
    if not start_positions:
        return ""
    start = min(start_positions)
    tail = text[start:]
    end_positions = []
    for pattern in end_patterns:
        match = re.search(pattern, tail, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            end_positions.append(match.start())
    end = len(tail)
    if end_positions:
        end = min(end_positions)
    return tail[:end]


def _latest_filing(data_dir: Path) -> str:
    filings = sorted(data_dir.glob("10-K-*.md")) + sorted(data_dir.glob("20-F-*.md"))
    if not filings:
        return ""
    return filings[-1].read_text()


def _latest_transcript(data_dir: Path) -> str:
    transcripts = sorted(data_dir.glob("earnings-call-*.md"))
    if not transcripts:
        return ""
    text = transcripts[-1].read_text()
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if lines:
                lines.append("")
            continue
        if stripped.startswith("#"):
            continue
        lower = stripped.lower()
        if lower.startswith("- source") or lower.startswith("- published") or lower.startswith("- retrieved"):
            continue
        if any(token in lower for token in ("image source", "motley fool", "call participants", "nasdaq :", "date ")):
            continue
        lines.append(stripped)
    return "\n".join(lines).strip()


def _extract_business_text(filing_text: str) -> str:
    return _find_section(
        filing_text,
        start_patterns=[
            r"^##\s*Business\b",
            r"^##\s*Item\s*1\.?\s*Business\b",
            r"^##\s*ITEM\s*1\.?\s*Business\b",
        ],
        end_patterns=[
            r"^##\s*Item\s*1A\b",
            r"^##\s*Risk\s*Factors\b",
            r"^##\s*Item\s*2\b",
        ],
    )


def _extract_risk_text(filing_text: str) -> str:
    return _find_section(
        filing_text,
        start_patterns=[
            r"^##\s*Item\s*1A\.?\s*Risk\s*Factors\b",
            r"^##\s*Risk\s*Factors\b",
        ],
        end_patterns=[
            r"^##\s*Item\s*1B\b",
            r"^##\s*Item\s*2\b",
            r"^##\s*Unresolved\s*Staff\s*Comments\b",
        ],
    )


def _keyword_paragraphs(paragraphs: list[str], keywords: list[str], limit: int = 2) -> list[str]:
    hits = []
    for paragraph in paragraphs:
        lower = paragraph.lower()
        if any(keyword in lower for keyword in keywords):
            hits.append(paragraph)
        if len(hits) >= limit:
            break
    return hits


def _risk_bullets(risk_text: str, limit: int = 5) -> list[str]:
    if not risk_text:
        return []
    cleaned = _strip_html(risk_text)
    cleaned = re.sub(r"^\\s*Risk Factors\\s*$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r"^\\s*#+\\s*.*$", "", cleaned, flags=re.MULTILINE)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    bullets = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 40:
            continue
        sentence = re.sub(r"^#+\s*", "", sentence).strip()
        sentence = re.sub(
            r"^(business risks|risks related to [^.:]+):?\\s*",
            "",
            sentence,
            flags=re.IGNORECASE,
        ).strip()
        lower = sentence.lower()
        if (
            "risk factors" in lower
            or "following risks" in lower
            or "risks related" in lower
            or "other risks" in lower
            or lower.startswith("in that case")
            or lower.startswith("in that event")
            or lower.startswith("business risks")
        ):
            continue
        if lower.endswith("risks"):
            continue
        if not sentence.endswith("."):
            sentence += "."
        bullets.append(sentence)
        if len(bullets) >= limit:
            break
    return bullets


def _extract_transcript_section(text: str, heading: str) -> str:
    if not text:
        return ""
    return _find_section(
        text,
        start_patterns=[rf"^{re.escape(heading)}\s*$"],
        end_patterns=[
            r"^Risks\s*$",
            r"^Summary\s*$",
            r"^Industry glossary\s*$",
            r"^Full Conference Call Transcript\s*$",
        ],
    )


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

    data_dir = base_dir / "companies" / ticker / "data"
    filing_text = _latest_filing(data_dir)
    business_text = _extract_business_text(filing_text)
    risk_text = _extract_risk_text(filing_text)

    business_paragraphs = _paragraphs(business_text)
    business_summary = []
    business_candidates = [
        p for p in business_paragraphs
        if not any(keyword in p.lower() for keyword in ("competition", "competitive", "risk", "regulation"))
        and not p.strip().endswith(":")
    ]
    for paragraph in (business_candidates or business_paragraphs)[:3]:
        business_summary.append(_truncate_words(paragraph, 120))

    if not business_summary:
        industry = profile.get("industry", "")
        sector = profile.get("sector", "")
        hq = ", ".join([str(profile.get("city", "")).strip(), str(profile.get("state", "")).strip()]).strip(", ")
        business_summary = [
            _truncate_words(
                f"{company_name} operates in the {industry or 'industries'} space within the {sector or 'sector'} sector. "
                f"The company is headquartered in {hq or 'its primary operating region'} and reports in {profile.get('currency','')}."
            )
        ]

    competition_paragraphs = _keyword_paragraphs(
        business_paragraphs,
        ["competition", "competitive", "competitors"],
        limit=2,
    )
    competitive_notes = [ _truncate_words(p, 120) for p in competition_paragraphs ]
    competitive_notes.append(
        _truncate_words(
            f"Over the last four fiscal years, average EBIT margin was {_fmt_pct(metrics['avg_ebit_margin'])}, "
            f"FCF margin {_fmt_pct(metrics['avg_fcf_margin'])}, and ROIC {_fmt_pct(metrics['avg_roic'])}. "
            "These economics provide a data-backed view of competitive strength, but still require qualitative validation."
        )
    )

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

    transcript_text = _latest_transcript(data_dir)
    takeaways_text = _extract_transcript_section(transcript_text, "Takeaways")
    summary_text = _extract_transcript_section(transcript_text, "Summary")
    takeaways_paragraphs = _paragraphs(takeaways_text)
    summary_paragraphs = _paragraphs(summary_text)

    if takeaways_paragraphs:
        growth_summary = [f"- {_truncate_words(p, 80)}" for p in takeaways_paragraphs[:4]]
    elif summary_paragraphs:
        growth_summary = [f"- {_truncate_words(p, 80)}" for p in summary_paragraphs[:3]]
    else:
        growth_fallback = (
            f"Revenue growth averaged {_fmt_pct(metrics['avg_revenue_growth'])} over the last four fiscal years. "
            "Future growth should be triangulated using segment disclosures in the 10-K and management commentary."
        )
        growth_summary = [f"- {_truncate_words(growth_fallback, 80)}"]

    risk_bullets = _risk_bullets(risk_text)
    if not risk_bullets:
        risk_bullets = [
            "Key risks are documented in the latest 10-K; include competitive intensity, execution, and macro sensitivity.",
        ]
    risk_section = "\n".join([f"- {bullet}" for bullet in risk_bullets])

    exec_bullets = [
        f"{company_name} generated {_fmt_bn(metrics['latest_revenue'])} in FY{metrics['latest_year']} revenue.",
        f"Average EBIT margin {_fmt_pct(metrics['avg_ebit_margin'])} and ROIC {_fmt_pct(metrics['avg_roic'])} indicate strong operating leverage and capital efficiency.",
        f"Net debt stands at {_fmt_bn(metrics['latest_net_debt'])}, with leverage averaging {_fmt_ratio(metrics['avg_leverage'])} when measured against EBITDA.",
        f"Base-case DCF implies {_fmt_money(base_value)} per share vs. current price {_fmt_money(price)}, for a margin of safety of {_fmt_pct(base_mos)}.",
        f"Top risks include {risk_bullets[0].rstrip('.')}.",
    ]
    executive_summary = "\n".join([f"- {item}" for item in exec_bullets])

    context = {
        "company_name": company_name,
        "ticker": ticker,
        "asof_date": asof,
        "executive_summary": executive_summary,
        "business_overview": "\n\n".join(business_summary),
        "competitive_position": "\n\n".join(competitive_notes),
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
        "growth_opportunities": "\n".join(growth_summary),
        "key_risks": risk_section,
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
        "conclusion": (
            "The base-case valuation implies a margin of safety of {mos}. "
            "Next steps: validate competitive positioning with segment and peer data, "
            "stress-test the margin assumptions in the DCF, and review the latest earnings call for guidance deltas."
        ).format(mos=_fmt_pct(base_mos)),
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
