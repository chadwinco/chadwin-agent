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
from research.valuation import load_assumptions, run_valuation  # noqa: E402


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


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
        paragraph = " ".join(lines).strip()
        if len(paragraph) >= 40:
            paragraphs.append(paragraph)
    return paragraphs


def _excerpt(text: str, max_chars: int = 8000) -> str:
    if not text:
        return ""
    paragraphs = _paragraphs(text)
    if not paragraphs:
        return text[:max_chars]
    chunks = []
    total = 0
    for paragraph in paragraphs:
        if total + len(paragraph) > max_chars:
            break
        chunks.append(paragraph)
        total += len(paragraph)
    return "\n\n".join(chunks) if chunks else text[:max_chars]


def _latest_filing(data_dir: Path) -> Path | None:
    filings = sorted(data_dir.glob("10-K-*.md")) + sorted(data_dir.glob("20-F-*.md"))
    return filings[-1] if filings else None


def _latest_transcript(data_dir: Path) -> Path | None:
    transcripts = sorted(data_dir.glob("earnings-call-*.md"))
    return transcripts[-1] if transcripts else None


def _format_df(df, max_rows: int = 12) -> str:
    if df is None or getattr(df, "empty", True):
        return ""
    if len(df) > max_rows:
        df = df.head(max_rows)
    try:
        return df.to_csv(index=False)
    except Exception:
        return df.to_string(index=False)


def _build_context(base_dir: Path, ticker: str, asof: str) -> str:
    data = load_company_data(base_dir, ticker)
    metrics = compute_metrics(data)
    assumptions = load_assumptions(base_dir / "companies" / ticker / "model" / "assumptions.yaml")
    valuation = run_valuation(data, assumptions, metrics)

    data_dir = base_dir / "companies" / ticker / "data"
    filing_path = _latest_filing(data_dir)
    transcript_path = _latest_transcript(data_dir)

    filing_text = filing_path.read_text() if filing_path else ""
    business_text = _find_section(
        filing_text,
        start_patterns=[
            r"^##\s*Business\b",
            r"^##\s*Item\s*1\.?\s*Business\b",
            r"^##\s*ITEM\s*1\.?\s*Business\b",
        ],
        end_patterns=[
            r"^##\s*Item\s*1A\b",
            r"^##\s*Risk\s*Factors\b",
            r"^##\s*Item\s*1B\b",
        ],
    )
    risk_text = _find_section(
        filing_text,
        start_patterns=[
            r"^##\s*Item\s*1A\.?\s*Risk\s*Factors\b",
            r"^##\s*Risk\s*Factors\b",
        ],
        end_patterns=[
            r"^##\s*Item\s*1B\b",
            r"^##\s*Item\s*2\b",
        ],
    )
    mdna_text = _find_section(
        filing_text,
        start_patterns=[
            r"^##\s*Item\s*7\.?\s*Management",
            r"^##\s*ITEM\s*7\.?\s*Management",
            r"^##\s*Management\s*'?s\s*Discussion",
        ],
        end_patterns=[
            r"^##\s*Item\s*7A\b",
            r"^##\s*ITEM\s*7A\b",
            r"^##\s*Item\s*8\b",
        ],
    )

    transcript_text = transcript_path.read_text() if transcript_path else ""

    profile_text = json.dumps(data.profile.iloc[0].to_dict(), indent=2) if not data.profile.empty else ""

    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None

    assumptions_text = json.dumps(assumptions, indent=2)
    if yaml is not None:
        assumptions_text = yaml.safe_dump(assumptions, sort_keys=False)

    context_parts = [
        f"# LLM Context Pack: {ticker}",
        "",
        f"As of: {asof}",
        "",
        "## Company Profile (companies/<TICKER>/data/company_profile.csv)",
        "```json",
        profile_text,
        "```",
        "",
        "## Key Metrics (computed)",
        "```json",
        json.dumps(
            {
                "latest_year": metrics.get("latest_year"),
                "latest_revenue": metrics.get("latest_revenue"),
                "latest_ebit": metrics.get("latest_ebit"),
                "latest_fcf": metrics.get("latest_fcf"),
                "latest_net_debt": metrics.get("latest_net_debt"),
                "avg_revenue_growth": metrics.get("avg_revenue_growth"),
                "avg_ebit_margin": metrics.get("avg_ebit_margin"),
                "avg_fcf_margin": metrics.get("avg_fcf_margin"),
                "avg_roic": metrics.get("avg_roic"),
                "avg_reinvestment_rate": metrics.get("avg_reinvestment_rate"),
                "avg_leverage": metrics.get("avg_leverage"),
            },
            indent=2,
        ),
        "```",
        "",
        "## Financial Summary Table (last 4 years)",
        metrics.get("financial_table", ""),
        "",
        "## Model Assumptions (assumptions.yaml)",
        "```yaml",
        assumptions_text.strip(),
        "```",
        "",
        "## Valuation Outputs",
        "```json",
        json.dumps(valuation, indent=2),
        "```",
    ]

    if data.analyst_estimates is not None and not data.analyst_estimates.empty:
        context_parts += [
            "",
            "## Analyst Revenue Forecasts (analyst_estimates.csv)",
            "```csv",
            _format_df(data.analyst_estimates, max_rows=20),
            "```",
            "",
            "Source: https://stockanalysis.com/stocks/{}/forecast/".format(ticker.lower()),
        ]

    if filing_path:
        context_parts += [
            "",
            f"## 10-K Business Section ({filing_path.name})",
            _excerpt(business_text, max_chars=8000),
            "",
            f"## 10-K Risk Factors Section ({filing_path.name})",
            _excerpt(risk_text, max_chars=8000),
            "",
            f"## 10-K MD&A Section ({filing_path.name})",
            _excerpt(mdna_text, max_chars=8000),
        ]

    if transcript_path:
        context_parts += [
            "",
            f"## Earnings Call Transcript ({transcript_path.name})",
            _excerpt(transcript_text, max_chars=5000),
        ]

    return "\n".join(part for part in context_parts if part is not None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare LLM context pack for a company")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--asof", default=str(date.today()))
    parser.add_argument("--base-dir", default=str(BASE_DIR))
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    ticker = args.ticker.upper()

    context = _build_context(base_dir, ticker, args.asof)
    analysis_dir = base_dir / "companies" / ticker / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    output_path = analysis_dir / f"{args.asof}-llm-context.md"
    output_path.write_text(context)
    print(f"LLM context written to {output_path}")


if __name__ == "__main__":
    main()
