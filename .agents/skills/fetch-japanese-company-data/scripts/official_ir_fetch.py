from __future__ import annotations

import io
import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime
from html import unescape
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


_NINTENDO_NEWS_FEED_URL = "https://www.nintendo.co.jp/corporate/common/data/news_en.xml"
_NINTENDO_BASE_URL = "https://www.nintendo.co.jp"
_FAST_RETAILING_IR_SOURCES = {
    "earnings_library": "https://www.fastretailing.com/eng/ir/library/earning.html",
    "annual_report_library": "https://www.fastretailing.com/eng/ir/library/annual.html",
    "ir_news": "https://www.fastretailing.com/eng/ir/news/",
}


@dataclass
class OfficialIRAttempt:
    title: str
    source_url: str
    released_date: Optional[date]
    status: str
    message: Optional[str] = None
    output_path: Optional[Path] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "source_url": self.source_url,
            "released_date": self.released_date.isoformat() if self.released_date else None,
            "status": self.status,
            "message": self.message,
            "output_path": str(self.output_path) if self.output_path else None,
        }


@dataclass
class OfficialIRFetchResult:
    report_path: Path
    attempts: list[OfficialIRAttempt]
    transcript_path: Optional[Path] = None
    transcript_url: Optional[str] = None
    transcript_date: Optional[date] = None

    @property
    def documents_written(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.status == "success")

    def transcript_report_payload(self) -> dict:
        attempts = []
        if self.transcript_url:
            attempts.append(
                {
                    "url": self.transcript_url,
                    "status": "success" if self.transcript_path else "not_found",
                    "http_status": 200 if self.transcript_path else None,
                    "body_length": 0,
                    "published_date": (
                        self.transcript_date.isoformat() if self.transcript_date else None
                    ),
                    "message": "Nintendo official IR feed" if self.transcript_path else None,
                }
            )

        return {
            "query": "Nintendo official IR documents",
            "manual_url": self.transcript_url,
            "candidate_urls": [self.transcript_url] if self.transcript_url else [],
            "selected_transcript": (
                {
                    "path": str(self.transcript_path),
                    "source_url": self.transcript_url,
                    "published_date": (
                        self.transcript_date.isoformat() if self.transcript_date else None
                    ),
                }
                if self.transcript_path and self.transcript_url
                else None
            ),
            "attempts": attempts,
        }


def _require_pypdf():
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pypdf is required to extract text from Nintendo IR PDFs. "
            "Install with `python3 -m pip install -r requirements.txt`."
        ) from exc
    return PdfReader


def _fetch_bytes(url: str) -> tuple[Optional[bytes], Optional[int], Optional[str]]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=45) as resp:
            return resp.read(), getattr(resp, "status", None), None
    except HTTPError as exc:
        return None, exc.code, str(exc)
    except URLError as exc:
        return None, None, str(exc.reason)
    except Exception as exc:
        return None, None, str(exc)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:100] if slug else "document"


def _source_stem(url: str) -> str:
    path = urlparse(url).path
    stem = Path(path).stem
    return _slugify(stem)[:24] if stem else "source"


def _parse_feed_date(value: str) -> Optional[date]:
    if not value:
        return None
    cleaned = value.strip()
    for fmt in ("%Y.%m.%d", "%Y.%m.%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    # Handle values like 2026.2.3
    parts = re.findall(r"\d+", cleaned)
    if len(parts) >= 3:
        try:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None
    return None


def _resolve_asof(asof: Optional[str]) -> date:
    if asof:
        try:
            return date.fromisoformat(asof)
        except ValueError:
            pass
    return date.today()


def _clean_text(value: Optional[str]) -> str:
    text = unescape((value or "").strip())
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_pdf_url(url: str) -> bool:
    return str(url or "").lower().endswith(".pdf")


def _is_relevant_nintendo_ir_item(title: str, page: str, category: str) -> bool:
    hay = f"{title} {page} {category}".lower()
    keywords = (
        "earnings",
        "financial results",
        "q & a",
        "q&a",
        "briefing",
        "annual report",
        "presentation",
        "explanatory material",
        "dividend",
        "forecast",
        "convocation",
        "resolution",
    )
    return any(keyword in hay for keyword in keywords)


def _is_qa_title(title: str) -> bool:
    lowered = title.lower()
    return "q & a" in lowered or "q&a" in lowered


def _fetch_html(url: str) -> tuple[Optional[str], Optional[int], Optional[str]]:
    payload, status_code, error = _fetch_bytes(url)
    if not payload:
        return None, status_code, error
    try:
        return payload.decode("utf-8", "ignore"), status_code, None
    except Exception as exc:
        return None, status_code, str(exc)


def _strip_html_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_pdf_anchors(html: str, page_url: str) -> list[tuple[str, str]]:
    anchors: list[tuple[str, str]] = []
    pattern = re.compile(
        r'<a[^>]+href="([^"]+\.pdf(?:\?[^"]*)?)"[^>]*>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html or ""):
        href = (match.group(1) or "").strip()
        if not href:
            continue
        source_url = urljoin(page_url, href)
        title = _strip_html_tags(match.group(2) or "")
        anchors.append((source_url, title))
    return anchors


def _parse_yymmdd_token(token: str) -> Optional[date]:
    if len(token) != 6 or not token.isdigit():
        return None
    year = int(token[0:2])
    month = int(token[2:4])
    day = int(token[4:6])
    year += 2000 if year < 80 else 1900
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _parse_fast_retailing_release_date(source_url: str) -> Optional[date]:
    lower = source_url.lower()

    yyyymmdd = re.search(r"(20\d{6})", lower)
    if yyyymmdd:
        token = yyyymmdd.group(1)
        try:
            return date(int(token[0:4]), int(token[4:6]), int(token[6:8]))
        except ValueError:
            pass

    yymmddhhmm = re.search(r"/(\d{10})_", lower)
    if yymmddhhmm:
        parsed = _parse_yymmdd_token(yymmddhhmm.group(1)[:6])
        if parsed:
            return parsed

    tanshin = re.search(r"tanshin(20\d{2})(\d{2})", lower)
    if tanshin:
        year = int(tanshin.group(1))
        month = int(tanshin.group(2))
        try:
            return date(year, month, 1)
        except ValueError:
            pass

    annual = re.search(r"ar(20\d{2})_en", lower)
    if annual:
        try:
            return date(int(annual.group(1)), 12, 31)
        except ValueError:
            pass

    return None


def _is_relevant_fast_retailing_pdf(source_url: str, title: str, source_label: str) -> bool:
    lowered = f"{source_url} {title}".lower()
    source_lower = source_url.lower()

    if source_label == "annual_report_library":
        return bool(re.search(r"/ar20\d{2}_en(?:_financial)?\.pdf(?:\?|$)", source_lower))

    if source_label == "earnings_library":
        keywords = ("results", "tanshin", "summary", "faq", "factbook", "earnings")
        return any(keyword in lowered for keyword in keywords)

    if source_label == "ir_news":
        keywords = ("dividend", "earning", "results", "financial", "trading halt", "notice")
        return any(keyword in lowered for keyword in keywords)

    return False


def _fast_retailing_priority(source_url: str, title: str, source_label: str) -> int:
    lowered = f"{source_url} {title}".lower()
    source_lower = source_url.lower()
    score = 0
    if source_label == "earnings_library":
        score += 60
    elif source_label == "annual_report_library":
        score += 40
    elif source_label == "ir_news":
        score += 20

    if "results" in lowered or "tanshin" in lowered:
        score += 50
    if re.search(r"/ar20\d{2}_en\.pdf(?:\?|$)", source_lower):
        score += 45
    if "_financial" in lowered:
        score += 30
    if "faq" in lowered:
        score += 15
    if "factbook" in lowered:
        score += 10
    if "dividend" in lowered:
        score += 5
    return score


def _fast_retailing_display_title(source_url: str, fallback_title: str) -> str:
    cleaned_fallback = (fallback_title or "").strip()
    if cleaned_fallback and not re.fullmatch(r"\(?\d[\d.,]*\s*(kb|mb)\)?", cleaned_fallback.lower()):
        return fallback_title
    stem = Path(urlparse(source_url).path).stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem.title() if stem else "Fast Retailing IR Document"


def _extract_pdf_text(
    payload: bytes,
    max_chars: int = 180000,
) -> tuple[str, int, int, bool]:
    previous_disable = logging.root.manager.disable
    logging.disable(logging.ERROR)
    try:
        PdfReader = _require_pypdf()
        reader = PdfReader(io.BytesIO(payload))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                # If decrypt fails, we still attempt extraction; some PDFs only need user empty password.
                pass

        pages = []
        total_chars = 0
        processed = 0
        truncated = False

        for idx, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            processed += 1
            if not text:
                continue

            remaining = max_chars - total_chars
            if remaining <= 0:
                truncated = True
                break

            if len(text) > remaining:
                text = text[:remaining]
                truncated = True

            pages.append(f"### Page {idx}\n\n{text}")
            total_chars += len(text)

            if total_chars >= max_chars:
                truncated = True
                break

        return "\n\n".join(pages).strip(), len(reader.pages), processed, truncated
    finally:
        logging.disable(previous_disable)


def _parse_nintendo_news_items(xml_payload: bytes) -> list[dict]:
    root = ET.fromstring(xml_payload)
    entries: list[dict] = []

    for item in root.findall("./item"):
        name_sub = _clean_text(item.findtext("name_sub"))
        name_main = _clean_text(item.findtext("name_main"))
        if name_sub and name_main:
            title = f"{name_sub} {name_main}".strip()
        else:
            title = name_sub or name_main

        relative_url = _clean_text(item.findtext("url"))
        source_url = urljoin(_NINTENDO_BASE_URL, relative_url)
        released_date = _parse_feed_date(_clean_text(item.findtext("date_released")))
        updated_date = _parse_feed_date(_clean_text(item.findtext("date_updated")))
        page = _clean_text(item.findtext("page"))
        category = _clean_text(item.findtext("category"))

        entries.append(
            {
                "title": title,
                "source_url": source_url,
                "released_date": released_date,
                "updated_date": updated_date,
                "page": page,
                "category": category,
            }
        )

    return entries


def fetch_nintendo_official_ir_documents(
    data_dir: Path,
    asof: Optional[str] = None,
    max_documents: int = 12,
) -> OfficialIRFetchResult:
    filings_dir = data_dir / "filings"
    filings_dir.mkdir(parents=True, exist_ok=True)

    # Keep generated official-IR artifacts deterministic across re-runs.
    for stale in filings_dir.glob("ir-document-*.md"):
        stale.unlink(missing_ok=True)
    for stale in filings_dir.glob("earnings-call-*-nintendo-co-jp.md"):
        stale.unlink(missing_ok=True)

    asof_date = _resolve_asof(asof)
    report_path = filings_dir / f"official-ir-fetch-report-{asof_date.isoformat()}.json"

    attempts: list[OfficialIRAttempt] = []
    transcript_path: Optional[Path] = None
    transcript_url: Optional[str] = None
    transcript_date: Optional[date] = None

    xml_payload, http_status, error = _fetch_bytes(_NINTENDO_NEWS_FEED_URL)
    if not xml_payload:
        attempts.append(
            OfficialIRAttempt(
                title="Nintendo IR feed",
                source_url=_NINTENDO_NEWS_FEED_URL,
                released_date=None,
                status="feed_fetch_error",
                message=f"status={http_status} error={error}",
            )
        )
        report_path.write_text(
            json.dumps(
                {
                    "feed_url": _NINTENDO_NEWS_FEED_URL,
                    "asof": asof_date.isoformat(),
                    "attempts": [attempt.to_dict() for attempt in attempts],
                },
                indent=2,
            )
        )
        return OfficialIRFetchResult(report_path=report_path, attempts=attempts)

    try:
        entries = _parse_nintendo_news_items(xml_payload)
    except Exception as exc:
        attempts.append(
            OfficialIRAttempt(
                title="Nintendo IR feed",
                source_url=_NINTENDO_NEWS_FEED_URL,
                released_date=None,
                status="feed_parse_error",
                message=str(exc),
            )
        )
        report_path.write_text(
            json.dumps(
                {
                    "feed_url": _NINTENDO_NEWS_FEED_URL,
                    "asof": asof_date.isoformat(),
                    "attempts": [attempt.to_dict() for attempt in attempts],
                },
                indent=2,
            )
        )
        return OfficialIRFetchResult(report_path=report_path, attempts=attempts)

    deduped: dict[str, dict] = {}
    for entry in entries:
        source_url = entry.get("source_url")
        if not source_url or not _is_pdf_url(source_url):
            continue

        title = entry.get("title") or "Nintendo IR Document"
        if not _is_relevant_nintendo_ir_item(
            title,
            entry.get("page") or "",
            entry.get("category") or "",
        ):
            continue

        released = entry.get("released_date") or entry.get("updated_date")
        if released and released > asof_date:
            continue

        existing = deduped.get(source_url)
        if existing is None:
            deduped[source_url] = entry
            continue

        existing_date = existing.get("released_date") or existing.get("updated_date")
        if released and (existing_date is None or released > existing_date):
            deduped[source_url] = entry

    candidates = list(deduped.values())
    candidates.sort(
        key=lambda item: item.get("released_date") or item.get("updated_date") or date.min,
        reverse=True,
    )
    candidates = candidates[:max_documents]

    if not candidates:
        attempts.append(
            OfficialIRAttempt(
                title="Nintendo IR feed",
                source_url=_NINTENDO_NEWS_FEED_URL,
                released_date=None,
                status="no_relevant_documents",
            )
        )
        report_path.write_text(
            json.dumps(
                {
                    "feed_url": _NINTENDO_NEWS_FEED_URL,
                    "asof": asof_date.isoformat(),
                    "attempts": [attempt.to_dict() for attempt in attempts],
                },
                indent=2,
            )
        )
        return OfficialIRFetchResult(report_path=report_path, attempts=attempts)

    for item in candidates:
        title = item.get("title") or "Nintendo IR Document"
        source_url = item.get("source_url") or ""
        released = item.get("released_date") or item.get("updated_date")

        payload, status_code, error_detail = _fetch_bytes(source_url)
        if not payload:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="document_fetch_error",
                    message=f"status={status_code} error={error_detail}",
                )
            )
            continue

        try:
            body, total_pages, pages_processed, truncated = _extract_pdf_text(payload)
        except Exception as exc:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="pdf_extract_error",
                    message=str(exc),
                )
            )
            continue

        if not body:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="pdf_empty",
                    message="No text extracted from PDF.",
                )
            )
            continue

        release_date = released or asof_date
        if transcript_path is None and _is_qa_title(title):
            filename = f"earnings-call-{release_date.isoformat()}-nintendo-co-jp.md"
        else:
            title_slug = _slugify(title)[:72]
            filename = (
                f"ir-document-{release_date.isoformat()}-{title_slug}-{_source_stem(source_url)}.md"
            )

        out_path = filings_dir / filename
        header = [
            f"# {title}",
            "",
            "- Source: Nintendo official IR site",
            f"- URL: {source_url}",
            f"- Released: {release_date.isoformat()}",
            f"- Retrieved: {date.today().isoformat()}",
            f"- Pages: {pages_processed}/{total_pages}",
            f"- Truncated: {'yes' if truncated else 'no'}",
            "",
        ]
        out_path.write_text("\n".join(header) + body + "\n")

        attempts.append(
            OfficialIRAttempt(
                title=title,
                source_url=source_url,
                released_date=release_date,
                status="success",
                output_path=out_path,
            )
        )

        if transcript_path is None and _is_qa_title(title):
            transcript_path = out_path
            transcript_url = source_url
            transcript_date = release_date

    report_path.write_text(
        json.dumps(
            {
                "feed_url": _NINTENDO_NEWS_FEED_URL,
                "asof": asof_date.isoformat(),
                "transcript": {
                    "path": str(transcript_path) if transcript_path else None,
                    "source_url": transcript_url,
                    "published_date": transcript_date.isoformat() if transcript_date else None,
                },
                "attempts": [attempt.to_dict() for attempt in attempts],
            },
            indent=2,
        )
    )

    return OfficialIRFetchResult(
        report_path=report_path,
        attempts=attempts,
        transcript_path=transcript_path,
        transcript_url=transcript_url,
        transcript_date=transcript_date,
    )


def fetch_fast_retailing_official_ir_documents(
    data_dir: Path,
    asof: Optional[str] = None,
    max_documents: int = 10,
) -> OfficialIRFetchResult:
    filings_dir = data_dir / "filings"
    filings_dir.mkdir(parents=True, exist_ok=True)

    # Keep generated official-IR artifacts deterministic across re-runs.
    for stale in filings_dir.glob("ir-document-*.md"):
        stale.unlink(missing_ok=True)

    asof_date = _resolve_asof(asof)
    report_path = filings_dir / f"official-ir-fetch-report-{asof_date.isoformat()}.json"

    attempts: list[OfficialIRAttempt] = []
    deduped_candidates: dict[str, dict] = {}

    for source_label, source_page in _FAST_RETAILING_IR_SOURCES.items():
        html, http_status, error = _fetch_html(source_page)
        if not html:
            attempts.append(
                OfficialIRAttempt(
                    title=f"Fast Retailing {source_label}",
                    source_url=source_page,
                    released_date=None,
                    status="page_fetch_error",
                    message=f"status={http_status} error={error}",
                )
            )
            continue

        anchors = _extract_pdf_anchors(html, source_page)
        if not anchors:
            attempts.append(
                OfficialIRAttempt(
                    title=f"Fast Retailing {source_label}",
                    source_url=source_page,
                    released_date=None,
                    status="page_no_pdf_links",
                )
            )
            continue

        for source_url, anchor_title in anchors:
            if not _is_relevant_fast_retailing_pdf(source_url, anchor_title, source_label):
                continue

            released = _parse_fast_retailing_release_date(source_url)
            if released and released > asof_date:
                continue

            priority = _fast_retailing_priority(source_url, anchor_title, source_label)
            existing = deduped_candidates.get(source_url)
            if existing is None or priority > existing.get("priority", -1):
                deduped_candidates[source_url] = {
                    "title": _fast_retailing_display_title(source_url, anchor_title),
                    "source_url": source_url,
                    "released_date": released,
                    "source_page": source_page,
                    "source_label": source_label,
                    "priority": priority,
                }

    candidates = list(deduped_candidates.values())
    candidates.sort(
        key=lambda item: (
            item.get("released_date") or date.min,
            item.get("priority", 0),
            item.get("source_url", ""),
        ),
        reverse=True,
    )
    candidates = candidates[:max_documents]

    if not candidates:
        attempts.append(
            OfficialIRAttempt(
                title="Fast Retailing official IR pages",
                source_url="; ".join(_FAST_RETAILING_IR_SOURCES.values()),
                released_date=None,
                status="no_relevant_documents",
            )
        )
        report_path.write_text(
            json.dumps(
                {
                    "source_pages": _FAST_RETAILING_IR_SOURCES,
                    "asof": asof_date.isoformat(),
                    "attempts": [attempt.to_dict() for attempt in attempts],
                },
                indent=2,
            )
        )
        return OfficialIRFetchResult(report_path=report_path, attempts=attempts)

    for item in candidates:
        title = item.get("title") or "Fast Retailing IR Document"
        source_url = item.get("source_url") or ""
        source_page = item.get("source_page") or ""
        released = item.get("released_date")

        payload, status_code, error_detail = _fetch_bytes(source_url)
        if not payload:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="document_fetch_error",
                    message=f"status={status_code} error={error_detail}",
                )
            )
            continue

        try:
            body, total_pages, pages_processed, truncated = _extract_pdf_text(payload)
        except Exception as exc:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="pdf_extract_error",
                    message=str(exc),
                )
            )
            continue

        if not body:
            attempts.append(
                OfficialIRAttempt(
                    title=title,
                    source_url=source_url,
                    released_date=released,
                    status="pdf_empty",
                    message="No text extracted from PDF.",
                )
            )
            continue

        release_date = released or asof_date
        title_slug = _slugify(title)[:72]
        filename = f"ir-document-{release_date.isoformat()}-{title_slug}-{_source_stem(source_url)}.md"
        out_path = filings_dir / filename

        header = [
            f"# {title}",
            "",
            "- Source: Fast Retailing official IR site",
            f"- URL: {source_url}",
            f"- Source Page: {source_page}",
            f"- Released: {release_date.isoformat()}",
            f"- Retrieved: {date.today().isoformat()}",
            f"- Pages: {pages_processed}/{total_pages}",
            f"- Truncated: {'yes' if truncated else 'no'}",
            "",
        ]
        out_path.write_text("\n".join(header) + body + "\n")

        attempts.append(
            OfficialIRAttempt(
                title=title,
                source_url=source_url,
                released_date=release_date,
                status="success",
                output_path=out_path,
            )
        )

    report_path.write_text(
        json.dumps(
            {
                "source_pages": _FAST_RETAILING_IR_SOURCES,
                "asof": asof_date.isoformat(),
                "attempts": [attempt.to_dict() for attempt in attempts],
            },
            indent=2,
        )
    )

    return OfficialIRFetchResult(report_path=report_path, attempts=attempts)
