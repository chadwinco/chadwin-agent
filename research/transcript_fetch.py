from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional, Tuple
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None


@dataclass
class TranscriptResult:
    path: Path
    source_url: str
    published_date: Optional[date]


def _fetch_url(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "ignore")
    except Exception:
        return None


def _search_duckduckgo(query: str, max_results: int = 8) -> list[str]:
    html = _fetch_url(f"https://duckduckgo.com/html/?q={quote(query)}")
    if not html:
        return []
    urls = []
    for match in re.finditer(r'class="result__a" href="([^"]+)"', html):
        link = match.group(1)
        if link.startswith("//"):
            link = f"https:{link}"
        if "duckduckgo.com/l/" in link:
            parsed = urlparse(link)
            qs = parse_qs(parsed.query)
            if "uddg" in qs and qs["uddg"]:
                link = unquote(qs["uddg"][0])
        if link.startswith("http"):
            urls.append(link)
        if len(urls) >= max_results:
            break
    # de-dup while preserving order
    seen = set()
    deduped = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def _extract_published_date(html: str, soup) -> Optional[date]:
    if not html:
        return None
    if soup is not None:
        meta = soup.find("meta", attrs={"property": "article:published_time"})
        if meta and meta.get("content"):
            return _parse_date(meta["content"])
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return _parse_date(time_tag["datetime"])

    for match in re.finditer(r'"datePublished"\\s*:\\s*"([^"]+)"', html):
        parsed = _parse_date(match.group(1))
        if parsed:
            return parsed
    return None


def _parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    text = value.strip()
    text = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        pass
    match = re.search(r"(\\d{4}-\\d{2}-\\d{2})", text)
    if match:
        try:
            return datetime.fromisoformat(match.group(1)).date()
        except ValueError:
            return None
    return None


def _extract_title(html: str, soup) -> str:
    if soup is not None:
        meta = soup.find("meta", attrs={"property": "og:title"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        if soup.title and soup.title.string:
            return soup.title.string.strip()
    return "Earnings Call Transcript"


def _extract_body(soup) -> str:
    if soup is None:
        return ""
    candidates = []
    for selector in [
        "article",
        "main",
        "div.article-body",
        "div.body__content",
        "div.post-content",
        "div.post-body",
        "div.article-content",
    ]:
        node = soup.select_one(selector)
        if node is not None:
            candidates.append(node)
    if not candidates:
        return ""

    best = max(candidates, key=lambda n: len(n.get_text(" ", strip=True)))
    parts = []
    for node in best.find_all(["h2", "h3", "p", "li"]):
        text = node.get_text(" ", strip=True)
        if text:
            parts.append(text)
    # remove duplicates while preserving order
    seen = set()
    cleaned = []
    for part in parts:
        if part in seen:
            continue
        seen.add(part)
        cleaned.append(part)
    return "\n\n".join(cleaned).strip()


def _candidate_filter(urls: Iterable[str]) -> list[str]:
    allowed_domains = (
        "fool.com",
        "nasdaq.com",
        "insidermonkey.com",
        "investing.com",
        "finance.yahoo.com",
    )
    filtered = []
    for url in urls:
        netloc = urlparse(url).netloc.lower()
        if any(domain in netloc for domain in allowed_domains):
            filtered.append(url)
        elif "earnings-call-transcript" in url.lower() or "earnings call transcript" in url.lower():
            filtered.append(url)
    return filtered


def _fetch_transcript(url: str) -> Tuple[Optional[str], Optional[date], str]:
    html = _fetch_url(url)
    if not html:
        return None, None, ""
    soup = BeautifulSoup(html, "html.parser") if BeautifulSoup else None
    body = _extract_body(soup)
    if len(body) < 1000:
        return None, None, ""
    title = _extract_title(html, soup)
    published = _extract_published_date(html, soup)
    return title, published, body


def fetch_latest_transcript(
    ticker: str,
    data_dir: Path,
    company_name: Optional[str] = None,
    asof: Optional[str] = None,
) -> Optional[TranscriptResult]:
    if BeautifulSoup is None:
        return None

    query = f"{company_name or ticker} earnings call transcript"
    urls = _candidate_filter(_search_duckduckgo(query))
    if not urls:
        return None

    best = None
    best_date = None
    best_title = None
    best_body = None

    for url in urls:
        title, published, body = _fetch_transcript(url)
        if not body:
            continue
        if best is None:
            best = url
            best_date = published
            best_title = title
            best_body = body
            continue
        if published and (best_date is None or published > best_date):
            best = url
            best_date = published
            best_title = title
            best_body = body

    if not best or not best_body:
        return None

    date_value = best_date or (date.fromisoformat(asof) if asof else date.today())
    source_slug = urlparse(best).netloc.replace("www.", "")
    filename = f"earnings-call-{date_value.isoformat()}-{source_slug}.md"
    path = data_dir / filename

    header = [
        f"# {best_title or 'Earnings Call Transcript'}",
        "",
        f"- Source: {best}",
        f"- Published: {best_date.isoformat() if best_date else 'Unknown'}",
        f"- Retrieved: {date.today().isoformat()}",
        "",
    ]
    path.write_text("\n".join(header) + best_body + "\n")

    return TranscriptResult(path=path, source_url=best, published_date=best_date)
