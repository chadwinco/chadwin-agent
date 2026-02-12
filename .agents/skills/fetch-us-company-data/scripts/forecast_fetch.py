from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
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
    generated_paths: list[Path] = field(default_factory=list)


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


def _normalize_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").strip().lower())


def _is_locked_value(text: str) -> bool:
    value = (text or "").strip().lower()
    return value in {"", "n/a", "na", "--", "-", "pro", "upgrade"}


def _is_paywalled_text(text: str) -> bool:
    value = _normalize_label(text)
    if not value:
        return False
    if value in {"pro", "upgrade"}:
        return True
    return "pro" in value or "upgrade" in value


def _parse_amount(text: str) -> Optional[float]:
    if _is_locked_value(text):
        return None
    cleaned = (text or "").replace(",", "").replace("$", "").strip()
    cleaned = cleaned.replace("\u2014", "").replace("\u2013", "").strip()
    if _is_locked_value(cleaned):
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


def _parse_percent(text: str) -> Optional[float]:
    if _is_locked_value(text):
        return None
    cleaned = (text or "").replace(",", "").replace("%", "").replace("+", "").strip()
    cleaned = cleaned.replace("\u2014", "").replace("\u2013", "").strip()
    if _is_locked_value(cleaned):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_ratio(text: str) -> Optional[float]:
    if _is_locked_value(text):
        return None
    cleaned = (text or "").replace(",", "").replace("x", "").replace("X", "").strip()
    cleaned = cleaned.replace("\u2014", "").replace("\u2013", "").strip()
    if _is_locked_value(cleaned):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_us_date(text: str) -> Optional[date]:
    value = (text or "").strip()
    if not value:
        return None
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _find_table_by_heading(soup, heading: str) -> Optional[object]:
    if soup is None:
        return None
    target = (heading or "").strip().lower()
    for tag in soup.find_all(["h2", "h3"]):
        if tag.get_text(" ", strip=True).lower() == target:
            table = tag.find_next("table")
            if table is not None:
                return table
    return None


def _find_revenue_forecast_table(soup) -> Optional[object]:
    table = _find_table_by_heading(soup, "Revenue Forecast")
    if table is not None:
        return table

    section = soup.find(id=re.compile("revenue-forecast", re.IGNORECASE))
    if section is not None:
        table = section.find("table")
        if table is not None:
            return table
    return None


def _table_headers(table) -> list[str]:
    thead = table.find("thead")
    if thead is not None:
        header_row = thead.find("tr")
        if header_row is not None:
            headers = [th.get_text(" ", strip=True) for th in header_row.find_all(["th", "td"])]
            if headers:
                return headers
    first_row = table.find("tr")
    if first_row is None:
        return []
    return [cell.get_text(" ", strip=True) for cell in first_row.find_all(["th", "td"])]


def _parse_revenue_forecast(
    table,
) -> Optional[tuple[list[int], Dict[int, Dict[str, Optional[float] | str]]]]:
    header_cells = _table_headers(table)
    if len(header_cells) < 2:
        return None

    year_columns: list[tuple[int, int]] = []
    for idx, header in enumerate(header_cells[1:]):
        year = _parse_year(header)
        if year is not None:
            year_columns.append((idx, year))
    if not year_columns:
        return None

    years = [year for _, year in year_columns]
    data: Dict[int, Dict[str, Optional[float] | str]] = {
        year: {
            "high": None,
            "avg": None,
            "low": None,
            "highRaw": None,
            "avgRaw": None,
            "lowRaw": None,
        }
        for year in years
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
        values = cells[1:]
        for col_idx, year in year_columns:
            value_text = values[col_idx] if col_idx < len(values) else ""
            raw_text = value_text.strip()
            data[year][label] = _parse_amount(raw_text)
            data[year][f"{label}Raw"] = raw_text or None

    if not data:
        return None

    return years, data


def _parse_revenue_estimates_from_embedded(
    html: str,
) -> Dict[int, Dict[str, Optional[float] | str]]:
    out: Dict[int, Dict[str, Optional[float] | str]] = {}

    charts_match = re.search(r"estimatesCharts:\{(?P<body>.*?)\},recommendations:", html, re.DOTALL)
    if charts_match is None:
        return out
    charts_body = charts_match.group("body")

    revenue_match = re.search(r"revenue:\{(?P<body>.*?)\},epsGrowth:", charts_body, re.DOTALL)
    if revenue_match is None:
        return out
    revenue_body = revenue_match.group("body")

    entry_re = re.compile(
        r'"(?P<date>20\d{2}-\d{2}-\d{2})"\s*:\s*(?P<payload>\{[^{}]*\}|"[^"]*"|null)',
        re.DOTALL,
    )
    value_re = re.compile(r"(?P<key>high|avg|low)\s*:\s*(?P<value>null|[-+]?\d*\.?\d+)")

    for match in entry_re.finditer(revenue_body):
        year = int(match.group("date")[:4])
        payload = (match.group("payload") or "").strip()
        entry = out.setdefault(
            year,
            {
                "high": None,
                "avg": None,
                "low": None,
                "highRaw": None,
                "avgRaw": None,
                "lowRaw": None,
            },
        )
        if payload.startswith("{"):
            for value_match in value_re.finditer(payload):
                key = value_match.group("key")
                raw = value_match.group("value")
                if raw == "null":
                    continue
                try:
                    parsed = float(raw)
                except ValueError:
                    continue
                entry[key] = parsed
                entry[f"{key}Raw"] = raw
            continue
        if payload.strip('"') == "[PRO]":
            for key in ("high", "avg", "low"):
                raw_key = f"{key}Raw"
                if entry.get(raw_key) is None:
                    entry[raw_key] = "Pro"

    return out


def _parse_price_target_table(table) -> Optional[dict]:
    rows: dict[str, list[str]] = {}
    for tr in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if len(cells) < 2:
            continue
        rows[_normalize_label(cells[0])] = cells[1:]

    price_cells = rows.get("price")
    change_cells = rows.get("change")
    if not price_cells or len(price_cells) < 4:
        return None

    out = {
        "low": _parse_amount(price_cells[0]),
        "average": _parse_amount(price_cells[1]),
        "median": _parse_amount(price_cells[2]),
        "high": _parse_amount(price_cells[3]),
        "lowChangePct": None,
        "averageChangePct": None,
        "medianChangePct": None,
        "highChangePct": None,
    }
    if change_cells and len(change_cells) >= 4:
        out.update(
            {
                "lowChangePct": _parse_percent(change_cells[0]),
                "averageChangePct": _parse_percent(change_cells[1]),
                "medianChangePct": _parse_percent(change_cells[2]),
                "highChangePct": _parse_percent(change_cells[3]),
            }
        )
    return out


def _parse_financial_forecast(table) -> tuple[list[int], list[dict]]:
    header_cells = _table_headers(table)
    if len(header_cells) < 2:
        return [], []

    year_columns: list[tuple[int, int]] = []
    for idx, header in enumerate(header_cells[1:]):
        year = _parse_year(header)
        if year is not None:
            year_columns.append((idx, year))
    if not year_columns:
        return [], []

    row_map: dict[str, list[str]] = {}
    for tr in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if len(cells) < 2:
            continue
        row_map[_normalize_label(cells[0])] = cells[1:]

    rows: list[dict] = []
    for col_idx, fiscal_year in year_columns:
        period_raw = ""
        period_values = row_map.get("periodending", [])
        if col_idx < len(period_values):
            period_raw = period_values[col_idx]
        period_date = _parse_us_date(period_raw)

        eps_raw = row_map.get("eps", [])
        eps_growth_raw = row_map.get("epsgrowth", [])
        forward_pe_raw = row_map.get("forwardpe", [])

        rows.append(
            {
                "fiscalYear": fiscal_year,
                "periodEnding": period_date.isoformat() if period_date else period_raw,
                "eps": _parse_ratio(eps_raw[col_idx] if col_idx < len(eps_raw) else ""),
                "epsGrowthPct": _parse_percent(
                    eps_growth_raw[col_idx] if col_idx < len(eps_growth_raw) else ""
                ),
                "forwardPE": _parse_ratio(
                    forward_pe_raw[col_idx] if col_idx < len(forward_pe_raw) else ""
                ),
                "epsRaw": eps_raw[col_idx].strip() if col_idx < len(eps_raw) else "",
                "epsGrowthRaw": eps_growth_raw[col_idx].strip()
                if col_idx < len(eps_growth_raw)
                else "",
                "forwardPERaw": forward_pe_raw[col_idx].strip()
                if col_idx < len(forward_pe_raw)
                else "",
            }
        )

    return [year for _, year in year_columns], rows


def _parse_price_target_text(text: str) -> tuple[Optional[float], Optional[float]]:
    numbers = re.findall(r"\$?\s*([-+]?\d+(?:,\d{3})*(?:\.\d+)?)", text or "")
    parsed: list[float] = []
    for value in numbers:
        try:
            parsed.append(float(value.replace(",", "")))
        except ValueError:
            continue
    if not parsed:
        return None, None
    if len(parsed) == 1:
        return None, parsed[0]
    return parsed[0], parsed[1]


def _parse_ratings_actions(table) -> list[dict]:
    if table is None:
        return []

    header_cells = _table_headers(table)
    if not header_cells:
        return []
    normalized_headers = [_normalize_label(header) for header in header_cells]

    rating_indexes = [idx for idx, header in enumerate(normalized_headers) if header == "rating"]
    rating_idx = rating_indexes[-1] if rating_indexes else -1
    action_idx = normalized_headers.index("action") if "action" in normalized_headers else -1
    price_target_idx = (
        normalized_headers.index("pricetarget") if "pricetarget" in normalized_headers else -1
    )
    upside_idx = normalized_headers.index("upside") if "upside" in normalized_headers else -1
    date_idx = normalized_headers.index("date") if "date" in normalized_headers else -1

    required_indexes = [rating_idx, action_idx, price_target_idx, upside_idx, date_idx]
    if any(idx < 0 for idx in required_indexes):
        return []
    max_idx = max(required_indexes)

    rows: list[dict] = []
    for tr in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if len(cells) <= max_idx:
            continue
        rating = cells[rating_idx].strip()
        action = cells[action_idx].strip()
        price_target = cells[price_target_idx].strip()
        upside = cells[upside_idx].strip()
        date_text = cells[date_idx].strip()
        parsed_date = _parse_us_date(date_text)
        if parsed_date is None:
            continue
        old_target, new_target = _parse_price_target_text(price_target)
        rows.append(
            {
                "_date": parsed_date,
                "rating": rating,
                "action": action,
                "priceTarget": price_target,
                "priceTargetOld": old_target,
                "priceTargetNew": new_target,
                "upsidePct": _parse_percent(upside),
                "date": parsed_date.isoformat(),
            }
        )
    return rows


def _filter_last_12_months(rows: list[dict], asof: date) -> list[dict]:
    cursor = date(asof.year, asof.month, 1)
    for _ in range(11):
        if cursor.month == 1:
            cursor = date(cursor.year - 1, 12, 1)
        else:
            cursor = date(cursor.year, cursor.month - 1, 1)
    cutoff = cursor
    return [row for row in rows if cutoff <= row["_date"] <= asof]


def _parse_consensus_widget(html: str) -> Optional[dict]:
    widget_match = re.search(r"widget:\{all:\{(?P<body>[^}]*)\}\}", html)
    if widget_match is None:
        return None

    body = widget_match.group("body")
    consensus_match = re.search(r'consensus:"(?P<consensus>[^"]+)"', body)
    count_match = re.search(r"count:(?P<count>\d+)", body)
    price_target_match = re.search(r"price_target:(?P<target>null|[-+]?\d*\.?\d+)", body)
    if consensus_match is None:
        return None

    analyst_count = int(count_match.group("count")) if count_match else None
    average_target = None
    if price_target_match:
        raw = price_target_match.group("target")
        if raw != "null":
            try:
                average_target = float(raw)
            except ValueError:
                average_target = None

    return {
        "consensus": consensus_match.group("consensus"),
        "analystCount": analyst_count,
        "averagePriceTarget": average_target,
    }


def fetch_analyst_forecasts(ticker: str, data_dir: Path) -> Optional[ForecastResult]:
    if BeautifulSoup is None:
        return None

    pd = _require_pandas()
    asof = date.today()
    retrieved = asof.isoformat()
    generated_paths: list[Path] = []
    fiscal_years: list[int] = []

    forecast_url = f"https://stockanalysis.com/stocks/{ticker.lower()}/forecast/"
    ratings_url = f"https://stockanalysis.com/stocks/{ticker.lower()}/ratings/"

    revenue_path: Optional[Path] = None
    source_url = forecast_url

    stale_history_path = data_dir / "analyst_ratings_history_12m.csv"
    if stale_history_path.exists():
        try:
            stale_history_path.unlink()
        except OSError:
            pass

    forecast_html = _fetch_url(forecast_url)
    if forecast_html:
        forecast_soup = BeautifulSoup(forecast_html, "html.parser")

        revenue_table_years: list[int] = []
        revenue_table_data: Dict[int, Dict[str, Optional[float] | str]] = {}
        revenue_table = _find_revenue_forecast_table(forecast_soup)
        if revenue_table is not None:
            parsed_revenue = _parse_revenue_forecast(revenue_table)
            if parsed_revenue:
                revenue_table_years, revenue_table_data = parsed_revenue

        embedded_revenue_data = _parse_revenue_estimates_from_embedded(forecast_html)
        all_revenue_years = sorted(set(revenue_table_years) | set(embedded_revenue_data.keys()))
        revenue_rows = []
        for year in all_revenue_years:
            table_entry = revenue_table_data.get(year, {})
            embedded_entry = embedded_revenue_data.get(year, {})

            row: dict[str, object] = {
                "metric": "revenue",
                "fiscalYear": year,
                "source": forecast_url,
                "retrieved": retrieved,
            }
            for key in ("high", "avg", "low"):
                table_value = table_entry.get(key)
                embedded_value = embedded_entry.get(key)
                row[key] = table_value if table_value is not None else embedded_value

                table_raw = table_entry.get(f"{key}Raw")
                embedded_raw = embedded_entry.get(f"{key}Raw")
                row[f"{key}Raw"] = table_raw if table_raw not in (None, "") else embedded_raw

            # Skip paywalled rows (e.g. "Pro"/"Upgrade") to avoid downstream ambiguity.
            if any(_is_paywalled_text(row.get(f"{key}Raw")) for key in ("high", "avg", "low")):
                continue
            # Also skip rows with no numeric estimates at all.
            if all(row.get(key) is None for key in ("high", "avg", "low")):
                continue
            revenue_rows.append(row)

        if revenue_rows:
            revenue_df = pd.DataFrame(
                revenue_rows,
                columns=[
                    "metric",
                    "fiscalYear",
                    "high",
                    "avg",
                    "low",
                    "highRaw",
                    "avgRaw",
                    "lowRaw",
                    "source",
                    "retrieved",
                ],
            )
            revenue_path = data_dir / "analyst_revenue_estimates.csv"
            revenue_df.to_csv(revenue_path, index=False)
            generated_paths.append(revenue_path)
            fiscal_years.extend(all_revenue_years)

        price_target_table = _find_table_by_heading(forecast_soup, "Stock Price Forecast")
        if price_target_table is not None:
            parsed_targets = _parse_price_target_table(price_target_table)
            if parsed_targets:
                price_target_df = pd.DataFrame(
                    [
                        {
                            **parsed_targets,
                            "source": forecast_url,
                            "retrieved": retrieved,
                        }
                    ],
                    columns=[
                        "low",
                        "average",
                        "median",
                        "high",
                        "lowChangePct",
                        "averageChangePct",
                        "medianChangePct",
                        "highChangePct",
                        "source",
                        "retrieved",
                    ],
                )
                price_target_path = data_dir / "analyst_price_targets.csv"
                price_target_df.to_csv(price_target_path, index=False)
                generated_paths.append(price_target_path)

        financial_table = _find_table_by_heading(forecast_soup, "Financial Forecast")
        if financial_table is not None:
            forecast_years, financial_rows = _parse_financial_forecast(financial_table)
            if financial_rows:
                eps_rows = []
                forward_pe_rows = []
                for row in financial_rows:
                    eps_raw = row.get("epsRaw")
                    eps_growth_raw = row.get("epsGrowthRaw")
                    forward_pe_raw = row.get("forwardPERaw")

                    if not (_is_paywalled_text(eps_raw) or _is_paywalled_text(eps_growth_raw)):
                        eps_rows.append(
                            {
                                "fiscalYear": row.get("fiscalYear"),
                                "periodEnding": row.get("periodEnding"),
                                "eps": row.get("eps"),
                                "epsGrowthPct": row.get("epsGrowthPct"),
                                "source": forecast_url,
                                "retrieved": retrieved,
                            }
                        )

                    if not _is_paywalled_text(forward_pe_raw):
                        forward_pe_rows.append(
                            {
                                "fiscalYear": row.get("fiscalYear"),
                                "periodEnding": row.get("periodEnding"),
                                "forwardPE": row.get("forwardPE"),
                                "source": forecast_url,
                                "retrieved": retrieved,
                            }
                        )

                if eps_rows:
                    eps_df = pd.DataFrame(
                        eps_rows,
                        columns=[
                            "fiscalYear",
                            "periodEnding",
                            "eps",
                            "epsGrowthPct",
                            "source",
                            "retrieved",
                        ],
                    )
                    eps_path = data_dir / "analyst_eps_estimates.csv"
                    eps_df.to_csv(eps_path, index=False)
                    generated_paths.append(eps_path)

                if forward_pe_rows:
                    forward_pe_df = pd.DataFrame(
                        forward_pe_rows,
                        columns=[
                            "fiscalYear",
                            "periodEnding",
                            "forwardPE",
                            "source",
                            "retrieved",
                        ],
                    )
                    forward_pe_path = data_dir / "analyst_eps_forward_pe_estimates.csv"
                    forward_pe_df.to_csv(forward_pe_path, index=False)
                    generated_paths.append(forward_pe_path)
                fiscal_years.extend(forecast_years)

    ratings_html = _fetch_url(ratings_url)
    if ratings_html:
        ratings_soup = BeautifulSoup(ratings_html, "html.parser")
        ratings_table = _find_table_by_heading(ratings_soup, "Ratings History")
        if ratings_table is None:
            ratings_table = ratings_soup.find("table")

        parsed_actions = _parse_ratings_actions(ratings_table)
        if parsed_actions:
            actions_12m = _filter_last_12_months(parsed_actions, asof)
            if actions_12m:
                action_rows = []
                for row in actions_12m:
                    action_rows.append(
                        {
                            "rating": row.get("rating"),
                            "action": row.get("action"),
                            "priceTarget": row.get("priceTarget"),
                            "priceTargetOld": row.get("priceTargetOld"),
                            "priceTargetNew": row.get("priceTargetNew"),
                            "upsidePct": row.get("upsidePct"),
                            "date": row.get("date"),
                            "source": ratings_url,
                            "retrieved": retrieved,
                        }
                    )
                actions_df = pd.DataFrame(
                    action_rows,
                    columns=[
                        "rating",
                        "action",
                        "priceTarget",
                        "priceTargetOld",
                        "priceTargetNew",
                        "upsidePct",
                        "date",
                        "source",
                        "retrieved",
                    ],
                )
                actions_path = data_dir / "analyst_ratings_actions_12m.csv"
                actions_df.to_csv(actions_path, index=False)
                generated_paths.append(actions_path)

        consensus = _parse_consensus_widget(ratings_html)
        if consensus:
            consensus_df = pd.DataFrame(
                [
                    {
                        **consensus,
                        "source": ratings_url,
                        "retrieved": retrieved,
                    }
                ],
                columns=[
                    "consensus",
                    "analystCount",
                    "averagePriceTarget",
                    "source",
                    "retrieved",
                ],
            )
            consensus_path = data_dir / "analyst_consensus.csv"
            consensus_df.to_csv(consensus_path, index=False)
            generated_paths.append(consensus_path)

    if not generated_paths:
        return None

    if revenue_path is not None:
        source_url = forecast_url
        path = revenue_path
    else:
        # Keep return contract usable when revenue is missing but other files were generated.
        source_url = forecast_url if forecast_html else ratings_url
        path = generated_paths[0]

    unique_years = sorted(set(fiscal_years))
    return ForecastResult(
        path=path,
        source_url=source_url,
        fiscal_years=unique_years,
        generated_paths=generated_paths,
    )
