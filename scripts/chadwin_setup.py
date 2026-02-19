#!/usr/bin/env python3
"""Bootstrap Chadwin by installing required skills and initializing data root."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse


@dataclass
class SkillSpec:
    name: str
    repo: str
    ref: str
    path: str


FLOATING_REFS = {"main", "master", "head"}


def _print(msg: str) -> None:
    print(msg, flush=True)


def _redact_arg(arg: str) -> str:
    if arg.startswith("https://") or arg.startswith("http://"):
        return _strip_credentials(arg)
    return arg


def _run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    rendered = " ".join(_redact_arg(item) for item in cmd)
    _print(f"$ {rendered}")
    try:
        subprocess.run(cmd, check=True, env=env, cwd=str(cwd) if cwd else None)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Command failed ({exc.returncode}): {rendered}") from exc


def _capture(cmd: list[str], *, cwd: Path | None = None) -> str:
    try:
        proc = subprocess.run(
            cmd,
            check=True,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise RuntimeError(stderr or f"Failed command: {' '.join(cmd)}") from exc
    return proc.stdout.strip()


def _repo_root(start: Path) -> Path:
    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in [candidate, *candidate.parents]:
        if (parent / ".git").exists():
            return parent
    return start.resolve()


def _inject_github_token(repo: str, token: str | None) -> str:
    if not token:
        return repo
    parsed = urlparse(repo)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        return repo
    netloc = f"x-access-token:{token}@{parsed.netloc}"
    return urlunparse(parsed._replace(netloc=netloc))


def _strip_credentials(url: str) -> str:
    parsed = urlparse(url)
    if "@" not in parsed.netloc:
        return url
    netloc = parsed.netloc.split("@", 1)[1]
    return urlunparse(parsed._replace(netloc=netloc))


def _parse_manifest(path: Path) -> tuple[bool, list[SkillSpec], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Invalid manifest (expected object): {path}")

    requires_edgar_identity = bool(payload.get("requires_edgar_identity", False))

    raw_skills = payload.get("skills")
    if not isinstance(raw_skills, list):
        raise SystemExit("Invalid manifest: `skills` must be a list")

    skills: list[SkillSpec] = []
    seen_names: set[str] = set()
    for idx, raw in enumerate(raw_skills, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Invalid skill entry at index {idx}: expected object")
        name = str(raw.get("name", "")).strip()
        repo = str(raw.get("repo", "")).strip()
        ref = str(raw.get("ref", "")).strip() or "main"
        path_value = str(raw.get("path", ".")).strip() or "."

        if not name or not repo:
            raise SystemExit(f"Invalid skill entry at index {idx}: `name` and `repo` are required")
        if name in seen_names:
            raise SystemExit(f"Duplicate skill name in manifest: {name}")
        seen_names.add(name)

        skills.append(
            SkillSpec(
                name=name,
                repo=repo,
                ref=ref,
                path=path_value,
            )
        )

    deprecated = payload.get("deprecated_skills", [])
    if not isinstance(deprecated, list) or not all(isinstance(x, str) for x in deprecated):
        raise SystemExit("Invalid manifest: `deprecated_skills` must be list[str]")

    return requires_edgar_identity, skills, [x.strip() for x in deprecated if x.strip()]


def _ensure_tool(tool: str) -> None:
    if shutil.which(tool) is None:
        raise SystemExit(f"Required tool not found in PATH: {tool}")


def _ensure_venv(venv_dir: Path) -> Path:
    py = venv_dir / "bin" / "python"
    if not py.exists():
        _run(["python3", "-m", "venv", str(venv_dir)])
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    return py


def _is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def _origin_url(path: Path) -> str | None:
    try:
        value = _capture(["git", "-C", str(path), "config", "--get", "remote.origin.url"])
    except RuntimeError:
        return None
    return value or None


def _backup_path(path: Path) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return path.with_name(f"{path.name}.bak-{stamp}")


def _safe_local_name(name: str) -> str:
    return name.replace("/", "-").replace("..", "-")


def _apply_skill_subpath(skill_root: Path, subpath: str) -> Path:
    if subpath in ("", "."):
        return skill_root
    resolved = (skill_root / subpath).resolve()
    if not str(resolved).startswith(str(skill_root.resolve())):
        raise SystemExit(f"Skill path escapes repo root: {subpath}")
    return resolved


def _clone_or_update_skill(*, skills_dir: Path, spec: SkillSpec, token: str | None, dry_run: bool) -> None:
    target_dir = skills_dir / _safe_local_name(spec.name)
    clean_clone_source = _strip_credentials(spec.repo)
    auth_clone_source = _inject_github_token(clean_clone_source, token)

    if not target_dir.exists():
        if dry_run:
            _print(f"[dry-run] would clone {spec.repo}@{spec.ref} -> {target_dir}")
            return
        skills_dir.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", auth_clone_source, str(target_dir)])
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        _run(["git", "-C", str(target_dir), "checkout", "--force", spec.ref])
        return

    if not _is_git_repo(target_dir):
        backup = _backup_path(target_dir)
        if dry_run:
            _print(f"[dry-run] would move non-git skill dir {target_dir} -> {backup} and reinstall")
            return
        target_dir.rename(backup)
        _print(f"Moved non-git skill dir to backup: {backup}")
        _run(["git", "clone", auth_clone_source, str(target_dir)])
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        _run(["git", "-C", str(target_dir), "checkout", "--force", spec.ref])
        return

    existing_origin = _origin_url(target_dir)
    cleaned_existing_origin = _strip_credentials(existing_origin) if existing_origin else None
    if cleaned_existing_origin != clean_clone_source:
        backup = _backup_path(target_dir)
        if dry_run:
            _print(
                "[dry-run] would move mismatched origin skill dir "
                f"{target_dir} -> {backup} (found: {existing_origin}, expected: {spec.repo})"
            )
            return
        target_dir.rename(backup)
        _print(f"Moved mismatched skill dir to backup: {backup}")
        _run(["git", "clone", auth_clone_source, str(target_dir)])
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        _run(["git", "-C", str(target_dir), "checkout", "--force", spec.ref])
        return

    if dry_run:
        _print(f"[dry-run] would update {spec.name} to {spec.ref} at {target_dir}")
        return

    if auth_clone_source != clean_clone_source:
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", auth_clone_source])
    _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
    _run(["git", "-C", str(target_dir), "checkout", "--force", spec.ref])
    _run(["git", "-C", str(target_dir), "reset", "--hard", spec.ref])
    _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])


def _load_env_identity(app_root: Path) -> str | None:
    env_path = app_root / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        if key.strip() not in {"EDGAR_IDENTITY", "SEC_IDENTITY_EMAIL"}:
            continue
        parsed = value.strip().strip('"').strip("'").strip()
        if parsed:
            return parsed
    return None


def _require_edgar_identity(
    *,
    required: bool,
    explicit_identity: str | None,
    env: dict[str, str],
    app_root: Path,
) -> str | None:
    identity = (explicit_identity or "").strip()
    if not identity:
        identity = env.get("EDGAR_IDENTITY", "").strip() or env.get("SEC_IDENTITY_EMAIL", "").strip()
    if not identity:
        identity = _load_env_identity(app_root) or ""
    if required and not identity:
        raise SystemExit(
            "EDGAR identity is required by this manifest. Provide --edgar-identity, set "
            "EDGAR_IDENTITY/SEC_IDENTITY_EMAIL in the environment, or set EDGAR_IDENTITY in "
            f"{app_root / '.env'}."
        )
    return identity or None


def parse_args() -> argparse.Namespace:
    repo_root = _repo_root(Path.cwd())
    parser = argparse.ArgumentParser(
        description=(
            "Install/update required Chadwin skills from skills.lock.json, "
            "and bootstrap <DATA_ROOT>."
        )
    )
    parser.add_argument(
        "--manifest",
        default=str(repo_root / "skills.lock.json"),
        help="Path to skills.lock.json (default: repo-root/skills.lock.json)",
    )
    parser.add_argument(
        "--app-root",
        default=str(repo_root),
        help="Application workspace root (default: detected git repo root)",
    )
    parser.add_argument(
        "--codex-home",
        default=os.getenv("CODEX_HOME", str(Path.home() / ".codex")),
        help="Codex home path (default: $CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--edgar-identity",
        help="SEC identity string (for example: 'Name email@domain.com').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifest and print planned actions without mutating state.",
    )
    parser.add_argument(
        "--skip-data-bootstrap",
        action="store_true",
        help="Skip running setup_chadwin_data_dirs.py and validate_data_contract.py.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    app_root = Path(args.app_root).expanduser().resolve()
    codex_home = Path(args.codex_home).expanduser().resolve()

    _ensure_tool("git")
    _ensure_tool("python3")

    requires_identity, specs, deprecated = _parse_manifest(manifest_path)
    _print(f"Manifest: {manifest_path}")
    _print(f"Required skills: {', '.join(spec.name for spec in specs)}")
    floating = [spec.name for spec in specs if spec.ref.lower() in FLOATING_REFS]
    if floating:
        _print(
            "WARNING: floating refs detected in manifest "
            f"({', '.join(floating)}). Prefer pinned tags or SHAs for reproducible releases."
        )
    if deprecated:
        _print(f"Deprecated (not installed): {', '.join(deprecated)}")

    env = dict(os.environ)
    env["CHADWIN_APP_ROOT"] = str(app_root)
    env["CHADWIN_SKILLS_DIR"] = str(codex_home / "skills")

    identity = _require_edgar_identity(
        required=requires_identity,
        explicit_identity=args.edgar_identity,
        env=env,
        app_root=app_root,
    )
    if identity:
        env["EDGAR_IDENTITY"] = identity

    venv_dir = app_root / ".venv"
    if args.dry_run:
        _print(f"[dry-run] would ensure venv: {venv_dir}")
        py = venv_dir / "bin" / "python"
    else:
        py = _ensure_venv(venv_dir)

    token = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")
    skills_dir = Path(env["CHADWIN_SKILLS_DIR"])

    for spec in specs:
        _clone_or_update_skill(skills_dir=skills_dir, spec=spec, token=token, dry_run=args.dry_run)

        if args.dry_run:
            continue
        resolved_root = _apply_skill_subpath(skills_dir / _safe_local_name(spec.name), spec.path)
        if not (resolved_root / "SKILL.md").exists():
            raise SystemExit(
                f"Installed skill {spec.name} is invalid: SKILL.md not found at {resolved_root}"
            )

    if not args.skip_data_bootstrap:
        setup_spec = next((spec for spec in specs if spec.name == "chadwin-setup"), None)
        if setup_spec is None:
            raise SystemExit("Manifest must include chadwin-setup when data bootstrap is enabled")

        setup_root = _apply_skill_subpath(skills_dir / _safe_local_name(setup_spec.name), setup_spec.path)
        setup_script = setup_root / "scripts" / "setup_chadwin_data_dirs.py"
        validate_script = setup_root / "scripts" / "validate_data_contract.py"
        if args.dry_run:
            _print(f"[dry-run] would run: {py} {setup_script}")
            _print(f"[dry-run] would run: {py} {validate_script}")
        else:
            if not setup_script.exists() or not validate_script.exists():
                raise SystemExit(
                    "chadwin-setup scripts missing. Expected both setup_chadwin_data_dirs.py and "
                    "validate_data_contract.py"
                )
            _run([str(py), str(setup_script)], env=env, cwd=app_root)
            _run([str(py), str(validate_script)], env=env, cwd=app_root)

    _print("Bootstrap completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
