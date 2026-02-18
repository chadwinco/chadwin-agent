#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

from data_paths import detect_repo_root, resolve_data_root


def _default_base_dir() -> Path:
    return detect_repo_root(Path(__file__).resolve())


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


def _clean_form_list(value: str) -> list[str]:
    forms = [piece.strip().upper() for piece in value.split(",") if piece.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for form in forms:
        if form in seen:
            continue
        seen.add(form)
        deduped.append(form)
    return deduped


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


def _filing_filename(filing: Any, filing_date: date | None) -> str:
    form = str(getattr(filing, "form", "FILING")).replace("/", "-").replace(" ", "")
    filed = filing_date.isoformat() if filing_date else "unknown"
    accession = _get_attr(filing, ("accession_number", "accession_no", "accession"))
    if accession:
        accession_text = str(accession).replace("/", "-")
        return f"{form}-{filed}-{accession_text}.md"
    return f"{form}-{filed}.md"


def _filing_date(filing: Any) -> date | None:
    raw = _get_attr(filing, ("filed_date", "filed", "filing_date"))
    return _to_date(raw)


def _resolve_output_dir(base_dir: Path, ticker: str, output_dir: str | None) -> Path:
    if output_dir:
        candidate = Path(output_dir)
        return candidate if candidate.is_absolute() else base_dir / candidate
    return (
        resolve_data_root()
        / "companies"
        / "US"
        / ticker
        / "data"
        / "filings"
        / "historical"
    )


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
                "Use the configured repo .env identity or pass --allow-identity-override."
            )
        source = "identity-override" if configured_identity and requested != configured_identity else "identity-arg"
        return requested, source

    if configured_identity:
        return configured_identity, "env"

    raise RuntimeError(
        "EDGAR_IDENTITY (or SEC_IDENTITY_EMAIL) is not set in repo .env and no --identity was provided."
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch older SEC filings for a US ticker to support progressive hypothesis testing."
        )
    )
    parser.add_argument("--ticker", required=True, help="US ticker symbol (for example ANF).")
    parser.add_argument(
        "--forms",
        default="10-K,10-Q,8-K",
        help="Comma-separated SEC forms to fetch (default: 10-K,10-Q,8-K).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=6,
        help="Maximum filings per form after filters (default: 6).",
    )
    parser.add_argument(
        "--before",
        type=lambda raw: _parse_iso_date(raw),
        help="Optional inclusive upper filing-date bound (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--after",
        type=lambda raw: _parse_iso_date(raw),
        help="Optional inclusive lower filing-date bound (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--include-attachments",
        action="store_true",
        help="Include attachments when markdown extraction supports them.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown files if already present.",
    )
    parser.add_argument(
        "--identity",
        help="SEC identity override. Otherwise uses EDGAR_IDENTITY or SEC_IDENTITY_EMAIL.",
    )
    parser.add_argument(
        "--allow-identity-override",
        action="store_true",
        help=(
            "Allow --identity to differ from configured EDGAR_IDENTITY in repo .env. "
            "Use sparingly for explicit operational reasons."
        ),
    )
    parser.add_argument("--base-dir", default=str(_default_base_dir()))
    parser.add_argument(
        "--output-dir",
        help=(
            "Optional output directory override. Defaults to "
            "<DATA_ROOT>/companies/US/<TICKER>/data/filings/historical."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    ticker = args.ticker.upper().strip()
    forms = _clean_form_list(args.forms)
    if not forms:
        print("No valid forms were provided.", file=sys.stderr)
        return 2
    if args.limit <= 0:
        print("--limit must be a positive integer.", file=sys.stderr)
        return 2
    if args.before and args.after and args.after > args.before:
        print("--after cannot be later than --before.", file=sys.stderr)
        return 2

    base_dir = Path(args.base_dir)
    output_dir = _resolve_output_dir(base_dir=base_dir, ticker=ticker, output_dir=args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

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

    entries: list[dict[str, Any]] = []
    per_form_counts: dict[str, int] = {}
    errors: list[dict[str, str]] = []

    for form in forms:
        try:
            filings = list(company.get_filings(form=form))
        except Exception as exc:
            errors.append({"form": form, "error": str(exc)})
            continue

        filings = sorted(
            filings,
            key=lambda filing: _filing_date(filing) or date.min,
            reverse=True,
        )

        kept = 0
        for filing in filings:
            if kept >= args.limit:
                break
            filed_date = _filing_date(filing)

            if filed_date is None and (args.before or args.after):
                continue
            if args.before and filed_date and filed_date > args.before:
                continue
            if args.after and filed_date and filed_date < args.after:
                continue

            target = output_dir / _filing_filename(filing, filing_date=filed_date)
            write_status = "exists"

            if not target.exists() or args.overwrite:
                attachment_forms = {form} if args.include_attachments else None
                try:
                    markdown = filing_markdown(
                        filing,
                        include_attachments=args.include_attachments,
                        attachment_forms=attachment_forms,
                    )
                except TypeError:
                    markdown = filing_markdown(filing, include_attachments=args.include_attachments)
                except Exception:
                    markdown = None

                body = str(markdown or "").strip()
                if not body:
                    body = f"# {ticker} {form} filing\n\nNo markdown content extracted."
                target.write_text(body + "\n", encoding="utf-8")
                write_status = "written"

            entries.append(
                {
                    "ticker": ticker,
                    "form": form,
                    "filed_date": filed_date.isoformat() if filed_date else None,
                    "path": _repo_scoped_path(target, base_dir=base_dir),
                    "status": write_status,
                }
            )
            kept += 1

        per_form_counts[form] = kept
        print(f"{form}: captured {kept} filings")

    report = {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "forms": forms,
        "limit_per_form": args.limit,
        "before": args.before.isoformat() if args.before else None,
        "after": args.after.isoformat() if args.after else None,
        "output_dir": _repo_scoped_path(output_dir, base_dir=base_dir),
        "identity_source": identity_source,
        "counts": per_form_counts,
        "errors": errors,
        "entries": entries,
    }
    report_path = output_dir / f"historical-filings-fetch-report-{date.today().isoformat()}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Report written: {_repo_scoped_path(report_path, base_dir=base_dir)}")

    if not entries and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
