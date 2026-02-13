#!/usr/bin/env python3
"""Render latest US ticker margin-of-safety ranges into deterministic artifacts."""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


REPORT_DIR_RE = re.compile(r"^(?P<asof>\d{4}-\d{2}-\d{2})(?:-(?P<run>\d{2}))?$")


@dataclass
class ValuationRecord:
    ticker: str
    asof_date: str
    report_dir: str
    bear_mos: float
    base_mos: float
    bull_mos: float
    bear_value_per_share: float | None
    base_value_per_share: float | None
    bull_value_per_share: float | None


def repo_scoped_path(path: Path) -> str:
    resolved = path.resolve()
    for parent in resolved.parents:
        if parent.name == "chadwin-codex":
            relative = resolved.relative_to(parent)
            relative_text = relative.as_posix()
            if not relative_text or relative_text == ".":
                return "chadwin-codex"
            return f"chadwin-codex/{relative_text}"
    return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan companies/US for each ticker's latest report, then render a "
            "margin-of-safety range chart (bear/base/bull)."
        )
    )
    parser.add_argument(
        "--companies-root",
        default="companies/US",
        help="Path to US companies root (default: companies/US).",
    )
    parser.add_argument(
        "--output-dir",
        default=".agents/skills/chart-us-valuation-ranges/assets",
        help="Directory for generated files (default: skill assets folder).",
    )
    parser.add_argument(
        "--sort-by",
        choices=("ticker", "base", "spread"),
        default="base",
        help="Sort rows by ticker, base margin, or spread (default: base).",
    )
    parser.add_argument(
        "--order",
        choices=("asc", "desc"),
        default="desc",
        help="Sort direction (default: desc).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max rows to include. 0 means no limit.",
    )
    parser.add_argument(
        "--title",
        default="US Margin of Safety Ranges (Latest Reports)",
        help="Chart title.",
    )
    return parser.parse_args()


def parse_report_rank(report_dir_name: str) -> tuple[date, int] | None:
    match = REPORT_DIR_RE.match(report_dir_name)
    if not match:
        return None
    asof = match.group("asof")
    run = int(match.group("run") or "0")
    try:
        parsed = datetime.strptime(asof, "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed, run


def latest_report_dir(reports_dir: Path) -> Path | None:
    ranked: list[tuple[date, int, Path]] = []
    for child in reports_dir.iterdir():
        if not child.is_dir():
            continue
        rank = parse_report_rank(child.name)
        if rank is None:
            continue
        ranked.append((rank[0], rank[1], child))
    if not ranked:
        return None
    ranked.sort()
    return ranked[-1][2]


def parse_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def load_outputs_json(report_dir: Path) -> dict | None:
    valuation_dir = report_dir / "valuation"
    for filename in ("outputs.json", "output.json"):
        candidate = valuation_dir / filename
        if candidate.exists():
            try:
                return json.loads(candidate.read_text())
            except json.JSONDecodeError:
                return None
    return None


def collect_records(companies_root: Path) -> tuple[list[ValuationRecord], list[str]]:
    records: list[ValuationRecord] = []
    skipped: list[str] = []

    if not companies_root.exists():
        return records, [f"Missing companies root: {companies_root}"]

    for company_dir in sorted(companies_root.iterdir()):
        if not company_dir.is_dir():
            continue
        ticker = company_dir.name.upper()
        reports_dir = company_dir / "reports"
        if not reports_dir.is_dir():
            skipped.append(f"{ticker}: missing reports directory")
            continue

        report_dir = latest_report_dir(reports_dir)
        if report_dir is None:
            skipped.append(f"{ticker}: no dated report folders")
            continue

        payload = load_outputs_json(report_dir)
        if payload is None:
            skipped.append(f"{ticker}: missing or invalid valuation outputs JSON")
            continue

        scenarios = payload.get("scenarios", {})
        bear_mos = parse_float(scenarios.get("bear", {}).get("margin_of_safety"))
        base_mos = parse_float(scenarios.get("base", {}).get("margin_of_safety"))
        bull_mos = parse_float(scenarios.get("bull", {}).get("margin_of_safety"))

        if bear_mos is None or base_mos is None or bull_mos is None:
            skipped.append(f"{ticker}: missing one or more scenario margin_of_safety fields")
            continue

        bear_value_per_share = parse_float(scenarios.get("bear", {}).get("value_per_share"))
        base_value_per_share = parse_float(scenarios.get("base", {}).get("value_per_share"))
        bull_value_per_share = parse_float(scenarios.get("bull", {}).get("value_per_share"))

        if isinstance(payload.get("asof_date"), str):
            asof = payload["asof_date"]
        else:
            match = REPORT_DIR_RE.match(report_dir.name)
            asof = match.group("asof") if match else report_dir.name

        records.append(
            ValuationRecord(
                ticker=ticker,
                asof_date=asof,
                report_dir=report_dir.name,
                bear_mos=bear_mos,
                base_mos=base_mos,
                bull_mos=bull_mos,
                bear_value_per_share=bear_value_per_share,
                base_value_per_share=base_value_per_share,
                bull_value_per_share=bull_value_per_share,
            )
        )

    return records, skipped


def sort_records(records: list[ValuationRecord], sort_by: str, order: str) -> list[ValuationRecord]:
    reverse = order == "desc"
    if sort_by == "ticker":
        return sorted(records, key=lambda r: r.ticker, reverse=reverse)
    if sort_by == "spread":
        return sorted(records, key=lambda r: r.bull_mos - r.bear_mos, reverse=reverse)
    return sorted(records, key=lambda r: r.base_mos, reverse=reverse)


def pct(value: float | None, decimals: int = 1) -> str:
    if value is None or not math.isfinite(value):
        return "n/a"
    return f"{value * 100:+.{decimals}f}%"


def pct_axis(value: float) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value * 100:.0f}%"


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def x_mapper(min_value: float, max_value: float, start_x: float, end_x: float):
    span = max_value - min_value
    if span <= 0:
        span = 1.0

    def _map(value: float) -> float:
        return start_x + ((value - min_value) / span) * (end_x - start_x)

    return _map


def tick_values(min_value: float, max_value: float, count: int = 7) -> list[float]:
    if max_value <= min_value:
        return [min_value]
    step = (max_value - min_value) / max(1, count - 1)
    return [min_value + i * step for i in range(count)]


def build_svg(records: list[ValuationRecord], title: str) -> str:
    if not records:
        raise ValueError("No records to render.")

    left_margin = 170
    right_margin = 220
    top_margin = 120
    row_height = 34
    row_gap = 14
    bottom_margin = 90
    width = 1600
    chart_height = len(records) * (row_height + row_gap)
    height = top_margin + chart_height + bottom_margin
    chart_left = left_margin
    chart_right = width - right_margin
    chart_top = top_margin

    min_value = min(min(r.bear_mos, r.base_mos, r.bull_mos) for r in records)
    max_value = max(max(r.bear_mos, r.base_mos, r.bull_mos) for r in records)
    padding = max((max_value - min_value) * 0.10, 0.03)
    min_value -= padding
    max_value += padding

    map_x = x_mapper(min_value, max_value, chart_left, chart_right)
    ticks = tick_values(min_value, max_value)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{xml_escape(title)}">'
    )
    parts.append("<defs>")
    parts.append(
        '<linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#f7fafc"/>'
        '<stop offset="100%" stop-color="#edf2f7"/>'
        "</linearGradient>"
    )
    parts.append("</defs>")
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="url(#bg)"/>')

    parts.append(
        f'<text x="{chart_left}" y="48" font-size="34" font-family="Avenir Next,Segoe UI,Arial,sans-serif" '
        f'fill="#111827" font-weight="700">{xml_escape(title)}</text>'
    )
    parts.append(
        f'<text x="{chart_left}" y="78" font-size="15" font-family="Avenir Next,Segoe UI,Arial,sans-serif" '
        f'fill="#4b5563">Generated {xml_escape(generated_at)} from latest report per ticker in companies/US</text>'
    )

    legend_y = 100
    legend_items = [
        ("Bear MoS", "#f59e0b"),
        ("Base MoS", "#2563eb"),
        ("Bull MoS", "#10b981"),
    ]
    for idx, (name, color) in enumerate(legend_items):
        x = chart_left + idx * 150
        parts.append(
            f'<circle cx="{x}" cy="{legend_y}" r="6" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{x + 12}" y="{legend_y + 5}" font-size="14" font-family="Avenir Next,Segoe UI,Arial,sans-serif" fill="#374151">{xml_escape(name)}</text>'
        )

    for tick in ticks:
        x = map_x(tick)
        parts.append(
            f'<line x1="{x:.2f}" y1="{chart_top - 16}" x2="{x:.2f}" y2="{chart_top + chart_height}" '
            f'stroke="#d1d5db" stroke-width="1" stroke-dasharray="3 6"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{chart_top - 24}" text-anchor="middle" font-size="12" '
            f'font-family="Avenir Next,Segoe UI,Arial,sans-serif" fill="#4b5563">{xml_escape(pct_axis(tick))}</text>'
        )

    zero_in_range = min_value <= 0.0 <= max_value
    zero_x = map_x(0.0)
    if zero_in_range:
        band_left = max(chart_left, zero_x - 6.0)
        band_right = min(chart_right, zero_x + 6.0)
        band_width = max(0.0, band_right - band_left)
        if band_width > 0:
            parts.append(
                f'<rect x="{band_left:.2f}" y="{chart_top - 6}" width="{band_width:.2f}" '
                f'height="{chart_height + 12}" fill="#111827" opacity="0.08"/>'
            )

    for idx, item in enumerate(records):
        y = chart_top + idx * (row_height + row_gap) + row_height / 2
        label_y = y + 5
        row_bg = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        parts.append(
            f'<rect x="{chart_left - 120}" y="{y - row_height / 2}" width="{chart_right - (chart_left - 120)}" '
            f'height="{row_height}" fill="{row_bg}" opacity="0.45"/>'
        )

        bear_x = map_x(item.bear_mos)
        base_x = map_x(item.base_mos)
        bull_x = map_x(item.bull_mos)

        parts.append(
            f'<line x1="{bear_x:.2f}" y1="{y:.2f}" x2="{bull_x:.2f}" y2="{y:.2f}" '
            f'stroke="#2563eb" stroke-width="9" stroke-linecap="round" opacity="0.35"/>'
        )
        parts.append(
            f'<circle cx="{bear_x:.2f}" cy="{y:.2f}" r="6" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5"/>'
        )
        parts.append(
            f'<circle cx="{base_x:.2f}" cy="{y:.2f}" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>'
        )
        parts.append(
            f'<circle cx="{bull_x:.2f}" cy="{y:.2f}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="1.5"/>'
        )

        parts.append(
            f'<text x="{chart_left - 130}" y="{label_y:.2f}" text-anchor="start" '
            f'font-size="14" font-family="Avenir Next,Segoe UI,Arial,sans-serif" fill="#111827" font-weight="600">{xml_escape(item.ticker)}</text>'
        )
        parts.append(
            f'<text x="{chart_right + 12}" y="{label_y:.2f}" text-anchor="start" '
            f'font-size="13" font-family="Avenir Next,Segoe UI,Arial,sans-serif" fill="#374151">'
            f'{xml_escape(pct(item.bear_mos))} / {xml_escape(pct(item.base_mos))} / {xml_escape(pct(item.bull_mos))}</text>'
        )

    if zero_in_range:
        parts.append(
            f'<line x1="{zero_x:.2f}" y1="{chart_top - 16}" x2="{zero_x:.2f}" y2="{chart_top + chart_height}" '
            f'stroke="#ffffff" stroke-width="5" opacity="0.95"/>'
        )
        parts.append(
            f'<line x1="{zero_x:.2f}" y1="{chart_top - 16}" x2="{zero_x:.2f}" y2="{chart_top + chart_height}" '
            f'stroke="#111827" stroke-width="2.6"/>'
        )
        parts.append(
            f'<text x="{zero_x:.2f}" y="{chart_top - 34}" text-anchor="middle" font-size="12" '
            f'font-family="Avenir Next,Segoe UI,Arial,sans-serif" fill="#111827" font-weight="700">0% MoS</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    args = parse_args()
    companies_root = Path(args.companies_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records, skipped = collect_records(companies_root)
    if not records:
        print("[ERROR] No margin-of-safety records found.")
        if skipped:
            print("Skipped:")
            for reason in skipped:
                print(f"- {reason}")
        return 1

    ordered = sort_records(records, args.sort_by, args.order)
    if args.limit > 0:
        ordered = ordered[: args.limit]

    svg_path = output_dir / "us-valuation-ranges.svg"
    json_path = output_dir / "us-valuation-ranges.json"

    svg_path.write_text(build_svg(ordered, args.title))

    json_rows = []
    for item in ordered:
        json_rows.append(
            {
                "ticker": item.ticker,
                "asof_date": item.asof_date,
                "report_dir": item.report_dir,
                "bear_margin_of_safety": item.bear_mos,
                "base_margin_of_safety": item.base_mos,
                "bull_margin_of_safety": item.bull_mos,
                "bear_value_per_share": item.bear_value_per_share,
                "base_value_per_share": item.base_value_per_share,
                "bull_value_per_share": item.bull_value_per_share,
            }
        )
    json_path.write_text(json.dumps(json_rows, indent=2) + "\n")

    print(f"[OK] Rows rendered: {len(ordered)}")
    print(f"[OK] SVG range chart: {repo_scoped_path(svg_path)}")
    print(f"[OK] JSON data: {repo_scoped_path(json_path)}")

    if skipped:
        print("[WARN] Skipped companies:")
        for reason in skipped:
            print(f"- {reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
