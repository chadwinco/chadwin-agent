from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None


_ALLOWED_DOMAINS = (
    "fool.com",
    "nasdaq.com",
    "insidermonkey.com",
    "investing.com",
    "finance.yahoo.com",
)
_BODY_SELECTORS = (
    "article",
    "main",
    "div.article-body",
    "div.body__content",
    "div.post-content",
    "div.post-body",
    "div.article-content",
)


@dataclass
class TranscriptResult:
    path: Path
    source_url: str
    published_date: Optional[date]


@dataclass
class FetchResponse:
    html: Optional[str]
    http_status: Optional[int]
    error_kind: Optional[str]
    error_detail: Optional[str]


@dataclass
class TranscriptAttempt:
    url: str
    status: str
    http_status: Optional[int] = None
    body_length: int = 0
    published_date: Optional[date] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "status": self.status,
            "http_status": self.http_status,
            "body_length": self.body_length,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "message": self.message,
        }


@dataclass
class TranscriptSearchReport:
    query: str
    candidate_urls: list[str]
    attempts: list[TranscriptAttempt]
    transcript: Optional[TranscriptResult] = None
    manual_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "manual_url": self.manual_url,
            "candidate_urls": self.candidate_urls,
            "selected_transcript": (
                {
                    "path": str(self.transcript.path),
                    "source_url": self.transcript.source_url,
                    "published_date": self.transcript.published_date.isoformat()
                    if self.transcript.published_date
                    else None,
                }
                if self.transcript
                else None
            ),
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }


@dataclass
class ParsedTranscript:
    title: str
    published_date: Optional[date]
    body: str


def _fetch_url(url: str) -> FetchResponse:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            status = getattr(resp, "status", None)
            return FetchResponse(
                html=resp.read().decode("utf-8", "ignore"),
                http_status=status,
                error_kind=None,
                error_detail=None,
            )
    except HTTPError as exc:
        return FetchResponse(
            html=None,
            http_status=exc.code,
            error_kind="http_error",
            error_detail=str(exc),
        )
    except URLError as exc:
        return FetchResponse(
            html=None,
            http_status=None,
            error_kind="network_error",
            error_detail=str(exc.reason),
        )
    except Exception as exc:
        return FetchResponse(
            html=None,
            http_status=None,
            error_kind="unknown_error",
            error_detail=str(exc),
        )


def _search_duckduckgo(query: str, max_results: int = 8) -> list[str]:
    response = _fetch_url(f"https://duckduckgo.com/html/?q={quote(query)}")
    if not response.html:
        return []

    html = response.html
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

    for match in re.finditer(r'"datePublished"\s*:\s*"([^"]+)"', html):
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
    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
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
    for selector in _BODY_SELECTORS:
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

    seen = set()
    cleaned = []
    for part in parts:
        if part in seen:
            continue
        seen.add(part)
        cleaned.append(part)
    return "\n\n".join(cleaned).strip()


def _candidate_filter(urls: Iterable[str]) -> list[str]:
    filtered = []
    for url in urls:
        netloc = urlparse(url).netloc.lower()
        if any(domain in netloc for domain in _ALLOWED_DOMAINS):
            filtered.append(url)
        elif "earnings-call-transcript" in url.lower() or "earnings call transcript" in url.lower():
            filtered.append(url)
    return filtered


def _resolve_date(asof: Optional[str]) -> date:
    if asof:
        try:
            return date.fromisoformat(asof)
        except ValueError:
            pass
    return date.today()


def _fetch_transcript_with_attempt(
    url: str,
    min_body_chars: int = 1000,
) -> tuple[Optional[ParsedTranscript], TranscriptAttempt]:
    response = _fetch_url(url)
    if not response.html:
        status = {
            "http_error": "http_error",
            "network_error": "network_error",
        }.get(response.error_kind, "fetch_error")
        return None, TranscriptAttempt(
            url=url,
            status=status,
            http_status=response.http_status,
            message=response.error_detail,
        )

    soup = BeautifulSoup(response.html, "html.parser") if BeautifulSoup else None
    body = _extract_body(soup)
    if not body:
        return None, TranscriptAttempt(
            url=url,
            status="parse_empty",
            http_status=response.http_status,
            body_length=0,
            message="No supported content container found in HTML.",
        )
    if len(body) < min_body_chars:
        return None, TranscriptAttempt(
            url=url,
            status="body_too_short",
            http_status=response.http_status,
            body_length=len(body),
            message=f"Extracted body shorter than {min_body_chars} characters.",
        )

    title = _extract_title(response.html, soup)
    published = _extract_published_date(response.html, soup)
    attempt = TranscriptAttempt(
        url=url,
        status="success",
        http_status=response.http_status,
        body_length=len(body),
        published_date=published,
    )
    return ParsedTranscript(title=title, published_date=published, body=body), attempt


def fetch_latest_transcript_with_report(
    ticker: str,
    data_dir: Path,
    company_name: Optional[str] = None,
    asof: Optional[str] = None,
    transcript_url: Optional[str] = None,
    max_results: int = 20,
    min_body_chars: int = 1000,
) -> TranscriptSearchReport:
    query = f"{company_name or ticker} earnings call transcript"

    if BeautifulSoup is None:
        report = TranscriptSearchReport(
            query=query,
            candidate_urls=[],
            attempts=[],
            manual_url=transcript_url,
        )
        report.attempts.append(
            TranscriptAttempt(
                url=transcript_url or "",
                status="dependency_missing",
                message="beautifulsoup4 is required for transcript extraction.",
            )
        )
        return report

    if transcript_url:
        urls = [transcript_url]
    else:
        urls = _candidate_filter(_search_duckduckgo(query, max_results=max_results))

    report = TranscriptSearchReport(
        query=query,
        candidate_urls=urls,
        attempts=[],
        manual_url=transcript_url,
    )
    if not urls:
        report.attempts.append(
            TranscriptAttempt(
                url="",
                status="no_candidates",
                message="No candidate URLs were returned by search/filter.",
            )
        )
        return report

    successes: list[tuple[str, ParsedTranscript]] = []

    for url in urls:
        payload, attempt = _fetch_transcript_with_attempt(url, min_body_chars=min_body_chars)
        report.attempts.append(attempt)
        if payload:
            successes.append((url, payload))

    if not successes:
        return report

    best_url, best_payload = max(
        successes,
        key=lambda item: item[1].published_date or date.min,
    )
    best_date = best_payload.published_date

    date_value = best_date or _resolve_date(asof)
    source_slug = urlparse(best_url).netloc.replace("www.", "")
    filename = f"earnings-call-{date_value.isoformat()}-{source_slug}.md"
    filings_dir = data_dir / "filings"
    filings_dir.mkdir(parents=True, exist_ok=True)
    path = filings_dir / filename

    header = [
        f"# {best_payload.title or 'Earnings Call Transcript'}",
        "",
        f"- Source: {best_url}",
        f"- Published: {best_date.isoformat() if best_date else 'Unknown'}",
        f"- Retrieved: {date.today().isoformat()}",
        "",
    ]
    path.write_text("\n".join(header) + best_payload.body + "\n")
    report.transcript = TranscriptResult(path=path, source_url=best_url, published_date=best_date)
    return report


def fetch_latest_transcript(
    ticker: str,
    data_dir: Path,
    company_name: Optional[str] = None,
    asof: Optional[str] = None,
    transcript_url: Optional[str] = None,
    max_results: int = 20,
    min_body_chars: int = 1000,
) -> Optional[TranscriptResult]:
    report = fetch_latest_transcript_with_report(
        ticker=ticker,
        data_dir=data_dir,
        company_name=company_name,
        asof=asof,
        transcript_url=transcript_url,
        max_results=max_results,
        min_body_chars=min_body_chars,
    )
    return report.transcript
