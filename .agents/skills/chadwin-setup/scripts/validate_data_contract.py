#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


APP_DATA_DIR_NAME = "Chadwin"
DATA_ROOT_ENV_VAR = "CHADWIN_DATA_DIR"
IDEA_SCREENS_SUBDIR = Path("idea-screens")
COMPANIES_SUBDIR = Path("companies")
IDEAS_LOG_PATH = IDEA_SCREENS_SUBDIR / "company-ideas-log.jsonl"
IMPROVEMENT_LOG_PATH = Path("improvement-log.md")
PREFERENCES_PATH = Path("user_preferences.json")
COUNTRY_CODE_RE = re.compile(r"^[A-Z]{2}$")
REPORT_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-\d{2})?$")
TICKER_RE = re.compile(r"^[A-Z0-9][A-Z0-9.\-]*$")

REQUIRED_PREFERENCES_KEYS = {
    "markets",
    "sector_and_industry_preferences",
    "investment_strategy_preferences",
    "report_preferences",
    "updated_at_utc",
}
MARKET_TOKENS = {"us", "non-us"}


@dataclass
class ValidationIssue:
    severity: str
    code: str
    path: str
    message: str


def default_data_root() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_DATA_DIR_NAME
        return Path.home() / "AppData" / "Roaming" / APP_DATA_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DATA_DIR_NAME
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / APP_DATA_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DATA_DIR_NAME


def resolve_data_root(cli_data_root: str | None) -> Path:
    if cli_data_root:
        candidate = Path(cli_data_root).expanduser()
    else:
        configured = os.getenv(DATA_ROOT_ENV_VAR, "").strip()
        if configured:
            candidate = Path(configured).expanduser()
        else:
            return default_data_root()
    if candidate.is_absolute():
        return candidate
    return (Path.cwd() / candidate).resolve()


def _append_issue(
    issues: list[ValidationIssue],
    *,
    severity: str,
    code: str,
    path: Path,
    message: str,
) -> None:
    issues.append(
        ValidationIssue(
            severity=severity,
            code=code,
            path=str(path),
            message=message,
        )
    )


def _is_iso_country_code(value: Any) -> bool:
    if value is None:
        return False
    return bool(COUNTRY_CODE_RE.match(str(value).strip().upper()))


def _validate_preferences(path: Path, issues: list[ValidationIssue]) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _append_issue(
            issues,
            severity="error",
            code="preferences_invalid_json",
            path=path,
            message=f"Unable to parse JSON: {exc}",
        )
        return

    if not isinstance(payload, dict):
        _append_issue(
            issues,
            severity="error",
            code="preferences_not_object",
            path=path,
            message="`user_preferences.json` must contain a JSON object.",
        )
        return

    missing = sorted(REQUIRED_PREFERENCES_KEYS - set(payload.keys()))
    if missing:
        _append_issue(
            issues,
            severity="error",
            code="preferences_missing_keys",
            path=path,
            message=f"Missing required top-level keys: {', '.join(missing)}",
        )

    markets = payload.get("markets")
    if not isinstance(markets, dict):
        _append_issue(
            issues,
            severity="error",
            code="preferences_markets_not_object",
            path=path,
            message="`markets` must be a JSON object.",
        )
        return

    included = markets.get("included_countries")
    if included is None:
        return
    if not isinstance(included, list):
        _append_issue(
            issues,
            severity="error",
            code="preferences_included_countries_not_list",
            path=path,
            message="`markets.included_countries` must be a list.",
        )
        return

    for idx, raw in enumerate(included, start=1):
        raw_token = str(raw).strip()
        token = raw_token.upper()
        if not token:
            _append_issue(
                issues,
                severity="error",
                code="preferences_empty_country_token",
                path=path,
                message=f"`markets.included_countries[{idx}]` is empty.",
            )
            continue
        if raw_token != token:
            _append_issue(
                issues,
                severity="error",
                code="preferences_country_token_not_uppercase",
                path=path,
                message=(
                    f"`markets.included_countries[{idx}]={raw!r}` must be uppercase ISO "
                    "alpha-2 (for example `US`, `JP`, `GB`)."
                ),
            )
            continue
        if _is_iso_country_code(token):
            continue
        _append_issue(
            issues,
            severity="error",
            code="preferences_invalid_country_token",
            path=path,
            message=(
                f"`markets.included_countries[{idx}]={raw!r}` is invalid. "
                "Use ISO 3166-1 alpha-2 uppercase country codes only (for example US, JP, GB)."
            ),
        )


def _validate_ideas_log(path: Path, issues: list[ValidationIssue]) -> None:
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_invalid_jsonl",
                path=path,
                message=f"Line {line_number}: invalid JSON ({exc}).",
            )
            continue

        if not isinstance(payload, dict):
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_non_object_entry",
                path=path,
                message=f"Line {line_number}: entry must be a JSON object.",
            )
            continue

        ticker = str(payload.get("ticker") or "").strip().upper()
        if not ticker or not TICKER_RE.match(ticker):
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_invalid_ticker",
                path=path,
                message=f"Line {line_number}: invalid ticker value {payload.get('ticker')!r}.",
            )

        market = str(payload.get("market") or "").strip().lower()
        if market not in MARKET_TOKENS:
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_invalid_market",
                path=path,
                message=f"Line {line_number}: `market` must be `us` or `non-us`.",
            )

        raw_country = str(payload.get("exchange_country") or "").strip()
        country = raw_country.upper()
        if raw_country and raw_country != country:
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_exchange_country_not_uppercase",
                path=path,
                message=f"Line {line_number}: `exchange_country` must use uppercase ISO alpha-2.",
            )
        if country and not _is_iso_country_code(country):
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_invalid_exchange_country",
                path=path,
                message=f"Line {line_number}: `exchange_country` must be ISO alpha-2 when present.",
            )
        if market == "us" and country and country != "US":
            _append_issue(
                issues,
                severity="error",
                code="ideas_log_market_country_mismatch",
                path=path,
                message=f"Line {line_number}: US market entry cannot use exchange_country={country}.",
            )


def _validate_report_dir(report_dir: Path, issues: list[ValidationIssue]) -> None:
    if not REPORT_DIR_RE.match(report_dir.name):
        _append_issue(
            issues,
            severity="error",
            code="invalid_report_dir_name",
            path=report_dir,
            message="Report folder must match YYYY-MM-DD or YYYY-MM-DD-##.",
        )

    report_path = report_dir / "report.md"
    valuation_dir = report_dir / "valuation"
    inputs_path = valuation_dir / "inputs.yaml"
    outputs_path = valuation_dir / "outputs.json"
    noncanonical_outputs_path = valuation_dir / "output.json"

    has_report = report_path.is_file()
    has_inputs = inputs_path.is_file()
    has_outputs = outputs_path.is_file()
    has_noncanonical_outputs = noncanonical_outputs_path.is_file()

    if has_noncanonical_outputs:
        _append_issue(
            issues,
            severity="error",
            code="noncanonical_output_json",
            path=noncanonical_outputs_path,
            message="Use `valuation/outputs.json`. `valuation/output.json` is not supported.",
        )

    if has_report or has_outputs:
        if not has_inputs:
            _append_issue(
                issues,
                severity="error",
                code="missing_report_inputs",
                path=report_dir,
                message="`valuation/inputs.yaml` is required when report.md or outputs.json exists.",
            )
    if has_report and not has_outputs:
        _append_issue(
            issues,
            severity="error",
            code="missing_outputs_json",
            path=report_dir,
            message="Completed report packages must include `valuation/outputs.json`.",
        )
    if has_outputs and not has_report:
        _append_issue(
            issues,
            severity="error",
            code="missing_report_md",
            path=report_dir,
            message="Completed report packages must include `report.md`.",
        )


def _validate_company_package(company_dir: Path, issues: list[ValidationIssue]) -> None:
    ticker = company_dir.name.upper()
    if not TICKER_RE.match(ticker):
        _append_issue(
            issues,
            severity="warning",
            code="nonstandard_ticker_folder",
            path=company_dir,
            message="Ticker folder is non-standard. Use uppercase ticker-style names when possible.",
        )

    data_dir = company_dir / "data"
    reports_dir = company_dir / "reports"
    if not data_dir.is_dir():
        _append_issue(
            issues,
            severity="warning",
            code="missing_data_dir",
            path=company_dir,
            message="Company package is missing `data/`.",
        )
    if not reports_dir.is_dir():
        _append_issue(
            issues,
            severity="warning",
            code="missing_reports_dir",
            path=company_dir,
            message="Company package is missing `reports/`.",
        )

    if reports_dir.is_dir():
        for child in sorted(reports_dir.iterdir()):
            if child.is_dir():
                _validate_report_dir(child, issues)


def _validate_companies(companies_root: Path, issues: list[ValidationIssue]) -> None:
    for child in sorted(companies_root.iterdir()):
        if not child.is_dir():
            continue

        country_code = child.name.upper()
        if child.name != country_code or not _is_iso_country_code(country_code):
            _append_issue(
                issues,
                severity="error",
                code="invalid_country_folder",
                path=child,
                message=(
                    "Country folders under `companies/` must be ISO alpha-2 uppercase "
                    "(for example `US`, `JP`, `GB`)."
                ),
            )
            # Continue validating nested folders for visibility, but flag once as invalid.

        for company_dir in sorted(child.iterdir()):
            if company_dir.is_dir():
                _validate_company_package(company_dir, issues)


def validate_data_contract(data_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not data_root.exists():
        _append_issue(
            issues,
            severity="error",
            code="missing_data_root",
            path=data_root,
            message="Data root does not exist. Run setup_chadwin_data_dirs.py first.",
        )
        return issues

    required_paths: list[tuple[Path, str, str]] = [
        (data_root / PREFERENCES_PATH, "file", "Missing required shared file `user_preferences.json`."),
        (data_root / IDEA_SCREENS_SUBDIR, "dir", "Missing required shared directory `idea-screens/`."),
        (data_root / IDEAS_LOG_PATH, "file", "Missing required shared file `idea-screens/company-ideas-log.jsonl`."),
        (data_root / COMPANIES_SUBDIR, "dir", "Missing required shared directory `companies/`."),
        (data_root / IMPROVEMENT_LOG_PATH, "file", "Missing required shared file `improvement-log.md`."),
    ]

    for path, kind, message in required_paths:
        exists = path.is_file() if kind == "file" else path.is_dir()
        if not exists:
            _append_issue(
                issues,
                severity="error",
                code="missing_required_path",
                path=path,
                message=message,
            )

    preferences_path = data_root / PREFERENCES_PATH
    if preferences_path.is_file():
        _validate_preferences(preferences_path, issues)

    ideas_log_path = data_root / IDEAS_LOG_PATH
    if ideas_log_path.is_file():
        _validate_ideas_log(ideas_log_path, issues)

    companies_root = data_root / COMPANIES_SUBDIR
    if companies_root.is_dir():
        _validate_companies(companies_root, issues)

    return issues


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Chadwin shared data primitives and company/report layout "
            "under <DATA_ROOT>."
        )
    )
    parser.add_argument(
        "--data-root",
        help=(
            "Override data root. Defaults to CHADWIN_DATA_DIR when set, "
            "otherwise OS app-data Chadwin path."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit validation result as JSON.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    data_root = resolve_data_root(args.data_root)
    issues = validate_data_contract(data_root)

    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    status = "ok" if not errors else "error"

    if args.json:
        payload = {
            "status": status,
            "data_root": str(data_root),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "issues": [
                {
                    "severity": issue.severity,
                    "code": issue.code,
                    "path": issue.path,
                    "message": issue.message,
                }
                for issue in issues
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Data root: {data_root}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        for issue in issues:
            label = issue.severity.upper()
            print(f"[{label}] {issue.path}: {issue.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
