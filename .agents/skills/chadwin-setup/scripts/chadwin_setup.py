#!/usr/bin/env python3
"""Install/update core Chadwin skills, then run shared data bootstrap/validation."""

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
SETUP_SKILL_NAME = "chadwin-setup"
SCRIPT_PATH = Path(__file__).resolve()
SETUP_SKILL_ROOT = SCRIPT_PATH.parents[1]


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


def _is_floating_ref(ref: str) -> bool:
    return ref.lower() in FLOATING_REFS


def _resolved_ref(ref: str) -> str:
    lower = ref.lower()
    if lower == "head":
        return "origin/HEAD"
    if _is_floating_ref(ref):
        return f"origin/{ref}"
    return ref


def _target_ref(ref: str, latest: bool) -> str:
    if latest:
        return "origin/HEAD"
    return _resolved_ref(ref)


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


def _parse_manifest(path: Path) -> tuple[list[SkillSpec], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Invalid manifest (expected object): {path}")

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

    return skills, [x.strip() for x in deprecated if x.strip()]


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


def _clone_or_update_skill(
    *,
    skills_dir: Path,
    spec: SkillSpec,
    token: str | None,
    latest: bool,
    dry_run: bool,
) -> None:
    target_dir = skills_dir / _safe_local_name(spec.name)
    clean_clone_source = _strip_credentials(spec.repo)
    auth_clone_source = _inject_github_token(clean_clone_source, token)
    hard_reset_ref = _target_ref(spec.ref, latest)
    checkout_ref = spec.ref if not latest else "origin/HEAD"

    if not target_dir.exists():
        if dry_run:
            _print(
                f"[dry-run] would clone {spec.repo}@{spec.ref} and reset to {hard_reset_ref} "
                f"-> {target_dir}"
            )
            return
        skills_dir.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", auth_clone_source, str(target_dir)])
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        _run(["git", "-C", str(target_dir), "checkout", "--force", checkout_ref])
        _run(["git", "-C", str(target_dir), "reset", "--hard", hard_reset_ref])
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
        _run(["git", "-C", str(target_dir), "checkout", "--force", checkout_ref])
        _run(["git", "-C", str(target_dir), "reset", "--hard", hard_reset_ref])
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
        _run(["git", "-C", str(target_dir), "checkout", "--force", checkout_ref])
        _run(["git", "-C", str(target_dir), "reset", "--hard", hard_reset_ref])
        return

    if dry_run:
        _print(
            f"[dry-run] would update {spec.name} to {spec.ref} and reset to {hard_reset_ref} "
            f"at {target_dir}"
        )
        return

    if auth_clone_source != clean_clone_source:
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", auth_clone_source])
    try:
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        _run(["git", "-C", str(target_dir), "checkout", "--force", checkout_ref])
        _run(["git", "-C", str(target_dir), "reset", "--hard", hard_reset_ref])
    finally:
        if auth_clone_source != clean_clone_source:
            _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])


def _resolve_commit(path: Path, ref: str) -> str | None:
    try:
        value = _capture(["git", "-C", str(path), "rev-parse", ref])
    except RuntimeError:
        return None
    return value or None


def _check_skill(
    *,
    skills_dir: Path,
    spec: SkillSpec,
    token: str | None,
    latest: bool,
) -> tuple[bool, str]:
    target_dir = skills_dir / _safe_local_name(spec.name)
    clean_clone_source = _strip_credentials(spec.repo)
    auth_clone_source = _inject_github_token(clean_clone_source, token)

    if not target_dir.exists():
        return False, f"missing install at {target_dir}"
    if not _is_git_repo(target_dir):
        return False, "installed path is not a git repository"

    existing_origin = _origin_url(target_dir)
    cleaned_existing_origin = _strip_credentials(existing_origin) if existing_origin else None
    if cleaned_existing_origin != clean_clone_source:
        return (
            False,
            f"origin mismatch (found: {existing_origin or '<none>'}, expected: {clean_clone_source})",
        )

    if auth_clone_source != clean_clone_source:
        _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", auth_clone_source])
    try:
        _run(["git", "-C", str(target_dir), "fetch", "--tags", "--prune", "origin"])
        desired_ref = _target_ref(spec.ref, latest)
        desired_commit = _resolve_commit(target_dir, desired_ref)
        local_commit = _resolve_commit(target_dir, "HEAD")
    finally:
        if auth_clone_source != clean_clone_source:
            _run(["git", "-C", str(target_dir), "remote", "set-url", "origin", clean_clone_source])

    if desired_commit is None:
        return False, f"unable to resolve target ref {desired_ref}"
    if local_commit is None:
        return False, "unable to resolve local HEAD"

    if local_commit == desired_commit:
        return True, f"up-to-date ({local_commit[:7]})"
    return (
        False,
        f"outdated local={local_commit[:7]} target={desired_commit[:7]} ({desired_ref})",
    )


def _delegate_data_bootstrap(
    *,
    setup_skill_root: Path,
    py: Path,
    env: dict[str, str],
    app_root: Path,
    dry_run: bool,
) -> None:
    setup_script = setup_skill_root / "scripts" / "setup_chadwin_data_dirs.py"
    validate_script = setup_skill_root / "scripts" / "validate_data_contract.py"

    if dry_run:
        _print(f"[dry-run] would run: {py} {setup_script}")
        _print(f"[dry-run] would run: {py} {validate_script}")
        return

    if not setup_script.exists() or not validate_script.exists():
        raise SystemExit(
            "chadwin-setup scripts missing. Expected both setup_chadwin_data_dirs.py and "
            "validate_data_contract.py"
        )
    _run([str(py), str(setup_script)], env=env, cwd=app_root)
    _run([str(py), str(validate_script)], env=env, cwd=app_root)


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


def _configured_edgar_identity(env: dict[str, str], app_root: Path) -> str | None:
    identity = env.get("EDGAR_IDENTITY", "").strip() or env.get("SEC_IDENTITY_EMAIL", "").strip()
    if identity:
        return identity
    return _load_env_identity(app_root)


def _upsert_edgar_identity(app_root: Path, identity: str) -> Path:
    env_path = app_root / ".env"
    escaped = identity.replace("\\", "\\\\").replace('"', '\\"')
    new_line = f'EDGAR_IDENTITY="{escaped}"'

    existing_lines: list[str] = []
    if env_path.exists():
        existing_lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    replaced = False
    for raw in existing_lines:
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key == "EDGAR_IDENTITY":
                updated_lines.append(new_line)
                replaced = True
                continue
        updated_lines.append(raw)

    if not replaced:
        if updated_lines and updated_lines[-1].strip():
            updated_lines.append("")
        updated_lines.append(new_line)

    env_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return env_path


def parse_args() -> argparse.Namespace:
    default_app_root = _repo_root(Path.cwd())
    parser = argparse.ArgumentParser(
        description=(
            "Install/update core skills from bundled chadwin-setup assets/skills.lock.json and then run "
            "shared <DATA_ROOT> bootstrap + validation."
        )
    )
    parser.add_argument(
        "--manifest",
        default=str(SETUP_SKILL_ROOT / "assets" / "skills.lock.json"),
        help=(
            "Path to core skills manifest "
            "(default: .agents/skills/chadwin-setup/assets/skills.lock.json)"
        ),
    )
    parser.add_argument(
        "--app-root",
        default=str(default_app_root),
        help="Application workspace root (default: detected git repo root)",
    )
    parser.add_argument(
        "--codex-home",
        default=os.getenv("CODEX_HOME", str(Path.home() / ".codex")),
        help="Codex home path (default: $CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--edgar-identity",
        help=(
            "Optional SEC identity string (for example: 'Name email@domain.com'). "
            "If provided, write/update EDGAR_IDENTITY in repo .env."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifest and print planned actions without mutating state.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether installed skills match the selected manifest target refs.",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help=(
            "Ignore manifest refs and align each skill repo to its remote default branch tip "
            "(origin/HEAD)."
        ),
    )
    parser.add_argument(
        "--skip-data-bootstrap",
        action="store_true",
        help=(
            "Skip delegating shared data bootstrap/validation to the bundled chadwin-setup "
            "skill."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check and args.dry_run:
        raise SystemExit("--check cannot be combined with --dry-run")

    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    app_root = Path(args.app_root).expanduser().resolve()
    codex_home = Path(args.codex_home).expanduser().resolve()

    _ensure_tool("git")
    if not args.check:
        _ensure_tool("python3")

    specs, deprecated = _parse_manifest(manifest_path)
    if any(spec.name == SETUP_SKILL_NAME for spec in specs):
        raise SystemExit(
            "Manifest must list external core skills only. "
            f"Remove `{SETUP_SKILL_NAME}` from {manifest_path}."
        )
    _print(f"Manifest: {manifest_path}")
    _print(f"Mode: {'latest' if args.latest else 'locked'}")
    _print(f"Core skills: {', '.join(spec.name for spec in specs)}")
    _print(
        "Ownership: bundled chadwin-setup owns core-skill install/update, shared data-root "
        "bootstrap, and data-contract validation."
    )
    floating = [spec.name for spec in specs if _is_floating_ref(spec.ref)]
    if floating and not args.latest:
        _print(
            "WARNING: floating refs detected in manifest "
            f"({', '.join(floating)}). Prefer pinned tags or SHAs for reproducible releases."
        )
    if deprecated:
        _print(f"Deprecated (not installed): {', '.join(deprecated)}")

    env = dict(os.environ)
    env["CHADWIN_APP_ROOT"] = str(app_root)
    env["CHADWIN_SKILLS_DIR"] = str(codex_home / "skills")

    if args.edgar_identity and args.edgar_identity.strip():
        normalized_identity = args.edgar_identity.strip()
        env["EDGAR_IDENTITY"] = normalized_identity
        env_path = app_root / ".env"
        if args.dry_run or args.check:
            mode = "dry-run" if args.dry_run else "check"
            _print(f"[{mode}] would write EDGAR identity to {env_path}")
        else:
            persisted_path = _upsert_edgar_identity(app_root=app_root, identity=normalized_identity)
            _print(f"Persisted EDGAR identity to {persisted_path}")

    configured_identity = _configured_edgar_identity(env=env, app_root=app_root)
    if not configured_identity:
        _print(
            "NOTE: EDGAR identity is not configured. SEC fetch workflows will need "
            f"`EDGAR_IDENTITY` in {app_root / '.env'}. During onboarding, ask the user for "
            "name/email and write that value to `.env`."
        )

    token = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")
    skills_dir = Path(env["CHADWIN_SKILLS_DIR"])

    if args.check:
        all_current = True
        for spec in specs:
            is_current, detail = _check_skill(
                skills_dir=skills_dir,
                spec=spec,
                token=token,
                latest=args.latest,
            )
            if is_current:
                _print(f"[OK] {spec.name}: {detail}")
            else:
                _print(f"[OUTDATED] {spec.name}: {detail}")
                all_current = False
        if all_current:
            _print("All core skills are up to date with manifest refs.")
            return 0
        _print("One or more core skills are not aligned with manifest refs.")
        return 2

    venv_dir = app_root / ".venv"
    if args.dry_run:
        _print(f"[dry-run] would ensure venv: {venv_dir}")
        py = venv_dir / "bin" / "python"
    else:
        py = _ensure_venv(venv_dir)

    for spec in specs:
        _clone_or_update_skill(
            skills_dir=skills_dir,
            spec=spec,
            token=token,
            latest=args.latest,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            continue
        resolved_root = _apply_skill_subpath(skills_dir / _safe_local_name(spec.name), spec.path)
        if not (resolved_root / "SKILL.md").exists():
            raise SystemExit(
                f"Installed skill {spec.name} is invalid: SKILL.md not found at {resolved_root}"
            )

    if not args.skip_data_bootstrap:
        _delegate_data_bootstrap(
            setup_skill_root=SETUP_SKILL_ROOT,
            py=py,
            env=env,
            app_root=app_root,
            dry_run=args.dry_run,
        )

    _print("Bootstrap completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
