#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

DATA_ROOT_RELATIVE_PATH = Path(".chadwin-data")
COMPANIES_ROOT_RELATIVE_PATH = DATA_ROOT_RELATIVE_PATH / "companies"


def _default_base_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / DATA_ROOT_RELATIVE_PATH).exists() and (parent / ".agents" / "skills").exists():
            return parent
    return Path.cwd()


def _repo_scoped_path(path: Path, base_dir: Path) -> str:
    base = base_dir.resolve()
    candidate = path if path.is_absolute() else (base / path)
    resolved_candidate = candidate.resolve()
    try:
        relative = resolved_candidate.relative_to(base)
    except ValueError:
        return str(candidate)

    relative_text = relative.as_posix()
    if not relative_text or relative_text == ".":
        return base.name
    return f"{base.name}/{relative_text}"


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date {value!r}; expected YYYY-MM-DD.") from exc


def _configured_edgar_identity(base_dir: Path) -> str | None:
    if load_dotenv:
        load_dotenv(base_dir / ".env")
    return os.getenv("EDGAR_IDENTITY") or os.getenv("SEC_IDENTITY_EMAIL")


def _resolve_edgar_identity(
    base_dir: Path,
    requested_identity: str | None,
    allow_identity_override: bool,
) -> tuple[str, str]:
    configured_identity = _configured_edgar_identity(base_dir=base_dir)
    requested = requested_identity.strip() if requested_identity else None

    if requested:
        if (
            configured_identity
            and requested != configured_identity
            and not allow_identity_override
        ):
            raise RuntimeError(
                "Provided --identity differs from configured EDGAR_IDENTITY. "
                "Use the configured .env identity or pass --allow-identity-override."
            )
        source = "identity-override" if configured_identity and requested != configured_identity else "identity-arg"
        return requested, source

    if configured_identity:
        return configured_identity, "env"

    raise RuntimeError(
        "EDGAR_IDENTITY (or SEC_IDENTITY_EMAIL) is not set in environment/.env and no --identity was provided."
    )


def _load_fetch_helpers(base_dir: Path):
    helper_dir = (
        base_dir
        / ".agents"
        / "skills"
        / "fetch-us-company-data"
        / "scripts"
    )
    if not helper_dir.exists():
        raise RuntimeError(f"Helper path not found: {helper_dir}")
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))

    try:
        from edgar_fetch import ensure_edgar_identity, filing_markdown  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Unable to import fetch helpers from fetch-us-company-data skill."
        ) from exc
    return ensure_edgar_identity, filing_markdown


def _get_attr(obj: Any, names: tuple[str, ...]) -> Any:
    for name in names:
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


def _to_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
        except ValueError:
            return None


def _filing_date(filing: Any) -> date | None:
    raw = _get_attr(filing, ("filed_date", "filed", "filing_date"))
    return _to_date(raw)


def _normalize_accession(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^0-9a-zA-Z]", "", value).lower()


def _filing_filename(filing: Any, filing_date: date | None) -> str:
    form = str(getattr(filing, "form", "FILING")).replace("/", "-").replace(" ", "")
    filed = filing_date.isoformat() if filing_date else "unknown"
    accession = _get_attr(filing, ("accession_number", "accession_no", "accession"))
    if accession:
        accession_text = str(accession).replace("/", "-")
        return f"{form}-{filed}-{accession_text}.md"
    return f"{form}-{filed}.md"


def _resolve_output_path(
    base_dir: Path,
    ticker: str,
    output_path: str | None,
    filing: Any,
    filing_date: date | None,
) -> Path:
    if output_path:
        candidate = Path(output_path)
        return candidate if candidate.is_absolute() else base_dir / candidate
    return (
        base_dir
        / COMPANIES_ROOT_RELATIVE_PATH
        / "US"
        / ticker
        / "data"
        / "filings"
        / "third_party"
        / _filing_filename(filing=filing, filing_date=filing_date)
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch a specific SEC filing via edgartools and save markdown to a local path."
        )
    )
    parser.add_argument("--ticker", required=True, help="Ticker symbol (for example HRMY or JAZZ).")
    parser.add_argument("--form", default="8-K", help="SEC form type (default: 8-K).")
    parser.add_argument(
        "--filed-date",
        type=lambda raw: _parse_iso_date(raw),
        help="Optional filing date filter (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--accession",
        help="Optional accession number filter (with or without dashes).",
    )
    parser.add_argument(
        "--result-index",
        type=int,
        default=0,
        help="Select Nth match after filtering, zero-based (default: 0).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=60,
        help="Maximum filings to scan per form before filtering (default: 60).",
    )
    parser.add_argument(
        "--include-attachments",
        action="store_true",
        help="Include filing attachments in markdown extraction when supported.",
    )
    parser.add_argument(
        "--identity",
        help="SEC identity override. Otherwise uses EDGAR_IDENTITY or SEC_IDENTITY_EMAIL.",
    )
    parser.add_argument(
        "--allow-identity-override",
        action="store_true",
        help=(
            "Allow --identity to differ from configured EDGAR_IDENTITY in .env. "
            "Use sparingly for explicit operational reasons."
        ),
    )
    parser.add_argument("--base-dir", default=str(_default_base_dir()))
    parser.add_argument(
        "--output-path",
        help=(
            "Optional output path. Defaults to "
            ".chadwin-data/companies/US/<TICKER>/data/filings/third_party/<auto-filename>.md"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.result_index < 0:
        print("--result-index must be >= 0", file=sys.stderr)
        return 2
    if args.limit <= 0:
        print("--limit must be > 0", file=sys.stderr)
        return 2

    base_dir = Path(args.base_dir)
    ticker = args.ticker.upper().strip()
    form = args.form.upper().strip()
    accession_filter = _normalize_accession(args.accession)

    try:
        ensure_edgar_identity, filing_markdown = _load_fetch_helpers(base_dir=base_dir)
    except Exception as exc:
        print(f"Unable to load fetch helpers: {exc}", file=sys.stderr)
        return 1

    try:
        resolved_identity, identity_source = _resolve_edgar_identity(
            base_dir=base_dir,
            requested_identity=args.identity,
            allow_identity_override=args.allow_identity_override,
        )
        ensure_edgar_identity(resolved_identity)
    except Exception as exc:
        print(f"EDGAR identity setup failed: {exc}", file=sys.stderr)
        return 1

    print(f"Using SEC identity source: {identity_source}")

    try:
        from edgar import Company  # type: ignore
    except Exception as exc:
        print(f"Unable to import edgar package: {exc}", file=sys.stderr)
        return 1

    try:
        company = Company(ticker)
    except Exception as exc:
        print(f"Unable to initialize company for {ticker}: {exc}", file=sys.stderr)
        return 1

    try:
        filings = list(company.get_filings(form=form))
    except Exception as exc:
        print(f"Unable to fetch filings for {ticker} {form}: {exc}", file=sys.stderr)
        return 1

    filings = sorted(
        filings,
        key=lambda filing: _filing_date(filing) or date.min,
        reverse=True,
    )[: args.limit]

    matches: list[Any] = []
    for filing in filings:
        filing_date = _filing_date(filing)
        if args.filed_date and filing_date != args.filed_date:
            continue
        if accession_filter:
            accession = _get_attr(filing, ("accession_number", "accession_no", "accession"))
            if _normalize_accession(str(accession) if accession else "") != accession_filter:
                continue
        matches.append(filing)

    if not matches:
        print(
            "No filings matched the provided filters. "
            "Try increasing --limit or adjusting --filed-date/--accession.",
            file=sys.stderr,
        )
        return 1

    if args.result_index >= len(matches):
        print(
            f"--result-index {args.result_index} is out of range for {len(matches)} matches.",
            file=sys.stderr,
        )
        return 2

    filing = matches[args.result_index]
    filing_date = _filing_date(filing)
    target = _resolve_output_path(
        base_dir=base_dir,
        ticker=ticker,
        output_path=args.output_path,
        filing=filing,
        filing_date=filing_date,
    )
    target.parent.mkdir(parents=True, exist_ok=True)

    attachment_forms = {form} if args.include_attachments else None
    try:
        markdown = filing_markdown(
            filing,
            include_attachments=args.include_attachments,
            attachment_forms=attachment_forms,
        )
    except TypeError:
        markdown = filing_markdown(filing, include_attachments=args.include_attachments)
    except Exception as exc:
        print(f"Unable to extract filing markdown: {exc}", file=sys.stderr)
        return 1

    body = str(markdown or "").strip()
    if not body:
        body = f"# {ticker} {form} filing\n\nNo markdown content extracted."
    target.write_text(body + "\n", encoding="utf-8")

    accession = _get_attr(filing, ("accession_number", "accession_no", "accession"))
    meta = {
        "ticker": ticker,
        "form": form,
        "filed_date": filing_date.isoformat() if filing_date else None,
        "accession": str(accession) if accession else None,
        "identity_source": identity_source,
        "include_attachments": args.include_attachments,
        "output_path": _repo_scoped_path(target, base_dir=base_dir),
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    meta_path = target.with_suffix(target.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote filing markdown: {_repo_scoped_path(target, base_dir=base_dir)}")
    print(f"Wrote metadata: {_repo_scoped_path(meta_path, base_dir=base_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
