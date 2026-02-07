from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Optional
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None

from loaders import _require_pandas


@dataclass
class ForecastResult:
    path: Path
    source_url: str
    fiscal_years: list[int]


def _fetch_url(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "ignore")
    except Exception:
        return None


def _parse_year(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(20\d{2})", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _parse_amount(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace(",", "").replace("$", "").strip()
    cleaned = cleaned.replace("\u2014", "").replace("\u2013", "").strip()
    if not cleaned or cleaned.lower() in ("n/a", "na", "--", "-"):
        return None

    unit_match = re.search(r"([TMBK])$", cleaned, re.IGNORECASE)
    multiplier = 1.0
    if unit_match:
        unit = unit_match.group(1).upper()
        cleaned = cleaned[:-1].strip()
        multiplier = {
            "T": 1e12,
            "B": 1e9,
            "M": 1e6,
            "K": 1e3,
        }.get(unit, 1.0)
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return value * multiplier


def _find_revenue_forecast_table(soup) -> Optional[object]:
    if soup is None:
        return None
    for tag in soup.find_all(["h2", "h3"]):
        if tag.get_text(strip=True).lower() == "revenue forecast":
            table = tag.find_next("table")
            if table is not None:
                return table

    section = soup.find(id=re.compile("revenue-forecast", re.IGNORECASE))
    if section is not None:
        table = section.find("table")
        if table is not None:
            return table
    return None


def _parse_revenue_forecast(table) -> Optional[tuple[list[int], Dict[int, Dict[str, Optional[float]]]]]:
    header_cells = []
    thead = table.find("thead")
    if thead is not None:
        header_cells = [th.get_text(" ", strip=True) for th in thead.find_all("th")]
    if not header_cells:
        first_row = table.find("tr")
        if first_row is not None:
            header_cells = [
                cell.get_text(" ", strip=True) for cell in first_row.find_all(["th", "td"])
            ]
    if len(header_cells) < 2:
        return None

    years = []
    for header in header_cells[1:]:
        year = _parse_year(header)
        if year:
            years.append(year)
    if not years:
        return None

    data: Dict[int, Dict[str, Optional[float]]] = {
        year: {"high": None, "avg": None, "low": None} for year in years
    }

    label_map = {
        "high": "high",
        "avg": "avg",
        "average": "avg",
        "low": "low",
    }

    for row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        if len(cells) < 2:
            continue
        label = label_map.get(cells[0].strip().lower())
        if not label:
            continue
        for year, value_text in zip(years, cells[1:]):
            data[year][label] = _parse_amount(value_text)

    if not any(
        (entry.get("high") or entry.get("avg") or entry.get("low"))
        for entry in data.values()
    ):
        return None

    return years, data


def fetch_analyst_forecasts(ticker: str, data_dir: Path) -> Optional[ForecastResult]:
    if BeautifulSoup is None:
        return None
    url = f"https://stockanalysis.com/stocks/{ticker.lower()}/forecast/"
    html = _fetch_url(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    table = _find_revenue_forecast_table(soup)
    if table is None:
        return None

    parsed = _parse_revenue_forecast(table)
    if not parsed:
        return None
    years, data = parsed

    pd = _require_pandas()
    rows = []
    for year in sorted(years):
        entry = data.get(year, {})
        rows.append(
            {
                "metric": "revenue",
                "fiscalYear": year,
                "high": entry.get("high"),
                "avg": entry.get("avg"),
                "low": entry.get("low"),
                "source": url,
                "retrieved": date.today().isoformat(),
            }
        )

    if not rows:
        return None

    df = pd.DataFrame(
        rows,
        columns=["metric", "fiscalYear", "high", "avg", "low", "source", "retrieved"],
    )
    path = data_dir / "analyst_estimates.csv"
    df.to_csv(path, index=False)
    return ForecastResult(path=path, source_url=url, fiscal_years=sorted(years))
