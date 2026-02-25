#!/usr/bin/env python3
"""Install/update core Chadwin skills, then run shared data bootstrap/validation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
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
BUNDLED_SKILL_NAMES = frozenset(
    {"chadwin-setup", "chadwin-preferences", "chadwin-activity-log"}
)
SCRIPT_PATH = Path(__file__).resolve()
SETUP_SKILL_ROOT = SCRIPT_PATH.parents[1]
BUNDLED_SKILLS_ROOT = SETUP_SKILL_ROOT.parent
EDGAR_IDENTITY_RE = re.compile(r"^.+<[^<>\s@]+@[^<>\s@]+>$")
APP_REPO_URL = "https://github.com/chadwinco/chadwin-agent.git"
APP_REPO_CANONICAL = "github.com/chadwinco/chadwin-agent"
APP_BOOTSTRAP_PRESERVE_FILES = (".env",)


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


def _canonical_repo_id(repo: str) -> str | None:
    raw = _strip_credentials(repo.strip())
    if not raw:
        return None

    # Handle scp-like forms: git@github.com:owner/repo.git
    if raw.startswith("git@") and ":" in raw:
        host_part, path_part = raw.split(":", 1)
        if "@" not in host_part:
            return None
        host = host_part.split("@", 1)[1].strip().lower()
        path = path_part.strip().strip("/").lower()
        if path.endswith(".git"):
            path = path[:-4]
        if not host or not path:
            return None
        return f"{host}/{path}"

    parsed = urlparse(raw)
    if not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    path = parsed.path.strip("/").lower()
    if path.endswith(".git"):
        path = path[:-4]
    if not path:
        return host
    return f"{host}/{path}"


def _is_official_app_repo(remote_url: str | None) -> bool:
    if not remote_url:
        return False
    return _canonical_repo_id(remote_url) == APP_REPO_CANONICAL


def _best_python() -> str:
    return shutil.which("python3") or sys.executable or "python3"


def _set_origin_head(path: Path) -> None:
    cmd = ["git", "-C", str(path), "remote", "set-head", "origin", "--auto"]
    rendered = " ".join(_redact_arg(item) for item in cmd)
    _print(f"$ {rendered}")
    subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _default_remote_branch(path: Path) -> str:
    try:
        value = _capture(["git", "-C", str(path), "symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    except RuntimeError:
        return "main"
    prefix = "origin/"
    if not value.startswith(prefix):
        return "main"
    branch = value[len(prefix) :].strip()
    return branch or "main"


def _current_branch(path: Path) -> str | None:
    try:
        value = _capture(["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"])
    except RuntimeError:
        return None
    return value or None


def _working_tree_is_clean(path: Path) -> bool:
    status = _capture(["git", "-C", str(path), "status", "--porcelain"])
    return not status.strip()


def _can_fast_forward(path: Path, target_ref: str) -> bool:
    cmd = ["git", "-C", str(path), "merge-base", "--is-ancestor", "HEAD", target_ref]
    rendered = " ".join(_redact_arg(item) for item in cmd)
    _print(f"$ {rendered}")
    proc = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    stderr = (proc.stderr or "").strip()
    raise SystemExit(stderr or f"Failed command: {rendered}")


def _preserve_local_files(path: Path, relpaths: tuple[str, ...]) -> dict[str, bytes]:
    preserved: dict[str, bytes] = {}
    for relpath in relpaths:
        candidate = path / relpath
        if candidate.exists() and candidate.is_file():
            preserved[relpath] = candidate.read_bytes()
    return preserved


def _restore_local_files(path: Path, preserved: dict[str, bytes]) -> None:
    for relpath, content in preserved.items():
        candidate = path / relpath
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_bytes(content)


def _bootstrap_git_repo_from_download(
    *,
    app_root: Path,
    dry_run: bool,
    check: bool,
) -> tuple[bool, bool]:
    if check:
        _print(
            "[CHECK][OUTDATED] App workspace has no .git metadata. "
            f"Would initialize git and align to {APP_REPO_URL}."
        )
        return False, False
    if dry_run:
        _print(
            "[dry-run] app workspace has no .git metadata; "
            f"would initialize git and align to {APP_REPO_URL}"
        )
        return False, False

    preserved = _preserve_local_files(app_root, APP_BOOTSTRAP_PRESERVE_FILES)
    _run(["git", "-C", str(app_root), "init"])
    if _origin_url(app_root):
        _run(["git", "-C", str(app_root), "remote", "set-url", "origin", APP_REPO_URL])
    else:
        _run(["git", "-C", str(app_root), "remote", "add", "origin", APP_REPO_URL])
    _run(["git", "-C", str(app_root), "fetch", "--tags", "--prune", "origin"])
    _set_origin_head(app_root)
    default_branch = _default_remote_branch(app_root)
    target_ref = f"origin/{default_branch}"
    if _resolve_commit(app_root, target_ref) is None:
        raise SystemExit(f"Unable to resolve app target ref: {target_ref}")
    _run(
        [
            "git",
            "-C",
            str(app_root),
            "checkout",
            "--force",
            "-B",
            default_branch,
            target_ref,
        ]
    )
    _restore_local_files(app_root, preserved)
    _print(
        "App workspace conversion completed: initialized git metadata and aligned "
        f"to {target_ref}."
    )
    return True, True


def _self_update_app_repo(
    *,
    app_root: Path,
    dry_run: bool,
    check: bool,
) -> tuple[bool, bool]:
    if not _is_git_repo(app_root):
        return _bootstrap_git_repo_from_download(
            app_root=app_root,
            dry_run=dry_run,
            check=check,
        )

    origin = _origin_url(app_root)
    if not origin:
        _print("App repo self-update skipped: no origin remote configured.")
        return True, False
    if not _is_official_app_repo(origin):
        _print(
            "App repo self-update skipped: origin is not the official chadwin-agent repo "
            f"({origin})."
        )
        return True, False

    if dry_run:
        _print(
            "[dry-run] would check app repo origin and fast-forward the default branch "
            "when safe."
        )
        return True, False

    _run(["git", "-C", str(app_root), "fetch", "--tags", "--prune", "origin"])
    _set_origin_head(app_root)
    default_branch = _default_remote_branch(app_root)
    target_ref = f"origin/{default_branch}"

    local_commit = _resolve_commit(app_root, "HEAD")
    target_commit = _resolve_commit(app_root, target_ref)
    if local_commit is None or target_commit is None:
        raise SystemExit(
            "Unable to resolve app repository commits "
            f"(local={local_commit}, target={target_ref})."
        )

    if local_commit == target_commit:
        _print(f"App repo self-update: up to date ({local_commit[:7]}).")
        return True, False

    _print(
        f"App repo update available: local={local_commit[:7]} target={target_commit[:7]} "
        f"({target_ref})."
    )
    if check:
        _print("[CHECK][OUTDATED] App repo is behind remote default branch.")
        return False, False

    current_branch = _current_branch(app_root)
    if not current_branch or current_branch == "HEAD":
        _print("App repo self-update skipped: detached HEAD.")
        return False, False
    if current_branch != default_branch:
        _print(
            f"App repo self-update skipped: current branch is {current_branch}, "
            f"default branch is {default_branch}."
        )
        return False, False
    if not _working_tree_is_clean(app_root):
        _print("App repo self-update skipped: working tree has local changes.")
        return False, False
    if not _can_fast_forward(app_root, target_ref):
        _print("App repo self-update skipped: local branch has diverged from remote.")
        return False, False

    _run(["git", "-C", str(app_root), "pull", "--ff-only", "origin", default_branch])
    _print(
        "App repo self-update completed: fast-forwarded "
        f"{current_branch} to {target_ref}."
    )
    return True, True


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


def _validate_edgar_identity_format(identity: str) -> None:
    normalized = identity.strip()
    if EDGAR_IDENTITY_RE.match(normalized):
        return
    raise SystemExit(
        "Invalid EDGAR identity format. Expected: `Full Name <email@example.com>`."
    )


def _require_bundled_skills() -> None:
    missing: list[str] = []
    for skill_name in sorted(BUNDLED_SKILL_NAMES):
        skill_root = BUNDLED_SKILLS_ROOT / skill_name
        if not (skill_root / "SKILL.md").exists():
            missing.append(str(skill_root))
    if missing:
        raise SystemExit(
            "Missing bundled required skills. Expected SKILL.md at: "
            + ", ".join(missing)
        )


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


def _resolve_runtime_skills_dirs(
    *,
    runtime_target: str,
    codex_skills_dir: Path,
    claude_skills_dir: Path,
) -> dict[str, Path]:
    targets: dict[str, Path] = {}
    if runtime_target in {"both", "codex"}:
        targets["codex"] = codex_skills_dir
    if runtime_target in {"both", "claude"}:
        targets["claude"] = claude_skills_dir
    return targets


def _sync_project_skills(
    *,
    setup_skill_root: Path,
    py: Path,
    env: dict[str, str],
    app_root: Path,
    dry_run: bool,
    check: bool,
) -> None:
    sync_script = setup_skill_root / "scripts" / "sync_project_skills.py"
    cmd = [str(py), str(sync_script)]
    if check:
        cmd.append("--check")

    if dry_run:
        _print(f"[dry-run] would run: {' '.join(cmd)}")
        return

    if not sync_script.exists():
        raise SystemExit(f"sync_project_skills.py not found at {sync_script}")
    _run(cmd, env=env, cwd=app_root)


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
            "Install/update core external skills from bundled chadwin-setup "
            "assets/skills.lock.json and then run "
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
        "--skip-self-update",
        action="store_true",
        help=(
            "Skip app workspace self-update. By default setup checks for app updates, "
            "fast-forwards git clones, and initializes git metadata for downloaded copies."
        ),
    )
    parser.add_argument(
        "--runtime-target",
        choices=("both", "codex", "claude"),
        default="both",
        help="Install/check external skills for one or both runtime targets.",
    )
    parser.add_argument(
        "--codex-skills-dir",
        default=os.getenv("CHADWIN_CODEX_SKILLS_DIR", str(Path.home() / ".codex" / "skills")),
        help="Codex skills directory (default: $CHADWIN_CODEX_SKILLS_DIR or ~/.codex/skills)",
    )
    parser.add_argument(
        "--claude-skills-dir",
        default=os.getenv("CHADWIN_CLAUDE_SKILLS_DIR", str(Path.home() / ".claude" / "skills")),
        help="Claude skills directory (default: $CHADWIN_CLAUDE_SKILLS_DIR or ~/.claude/skills)",
    )
    parser.add_argument(
        "--edgar-identity",
        help=(
            "Optional SEC identity string (for example: 'Full Name <email@example.com>'). "
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

    app_root = Path(args.app_root).expanduser().resolve()

    _ensure_tool("git")
    _ensure_tool("python3")

    app_repo_current = True
    app_repo_updated = False
    if args.skip_self_update:
        _print("App repo self-update skipped via --skip-self-update.")
    else:
        app_repo_current, app_repo_updated = _self_update_app_repo(
            app_root=app_root,
            dry_run=args.dry_run,
            check=args.check,
        )
        if app_repo_updated and not args.check and not args.dry_run:
            _print("App repo changed during self-update; restarting setup with latest code.")
            python = _best_python()
            cmd = [python, str(SCRIPT_PATH), *sys.argv[1:]]
            rendered = " ".join(_redact_arg(item) for item in cmd)
            _print(f"$ {rendered}")
            os.execv(python, cmd)

    _require_bundled_skills()

    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    codex_skills_dir = Path(args.codex_skills_dir).expanduser().resolve()
    claude_skills_dir = Path(args.claude_skills_dir).expanduser().resolve()
    runtime_skills_dirs = _resolve_runtime_skills_dirs(
        runtime_target=args.runtime_target,
        codex_skills_dir=codex_skills_dir,
        claude_skills_dir=claude_skills_dir,
    )

    specs, deprecated = _parse_manifest(manifest_path)
    bundled_in_manifest = sorted(spec.name for spec in specs if spec.name in BUNDLED_SKILL_NAMES)
    if bundled_in_manifest:
        raise SystemExit(
            "Manifest must list external core skills only. "
            f"Remove bundled skills from {manifest_path}: {', '.join(bundled_in_manifest)}."
        )
    _print(f"Manifest: {manifest_path}")
    _print(f"Mode: {'latest (origin/HEAD)' if args.latest else 'manifest refs'}")
    _print(
        "Runtime targets: "
        + ", ".join(f"{name}={path}" for name, path in runtime_skills_dirs.items())
    )
    _print(f"Core external skills: {', '.join(spec.name for spec in specs)}")
    _print(
        "Ownership: bundled chadwin-setup owns core external skill install/update, shared "
        "data-root bootstrap, and data-contract validation."
    )
    floating = [spec for spec in specs if _is_floating_ref(spec.ref)]
    if floating and not args.latest:
        floating_non_main = [spec.name for spec in floating if spec.ref.lower() != "main"]
        if floating_non_main:
            _print(
                "WARNING: floating refs detected in manifest outside `main` "
                f"({', '.join(floating_non_main)}). Prefer `main` for default latest sync "
                "or pinned tags/SHAs for release snapshots."
            )
        else:
            _print(
                "Info: manifest refs are floating `main`; setup will sync each skill to "
                "latest `origin/main`."
            )
    if deprecated:
        _print(f"Deprecated (not installed): {', '.join(deprecated)}")

    env = dict(os.environ)
    env["CHADWIN_APP_ROOT"] = str(app_root)
    env["CHADWIN_CODEX_SKILLS_DIR"] = str(codex_skills_dir)
    env["CHADWIN_CLAUDE_SKILLS_DIR"] = str(claude_skills_dir)
    env["CHADWIN_SKILLS_DIR"] = str(next(iter(runtime_skills_dirs.values())))

    if args.edgar_identity and args.edgar_identity.strip():
        normalized_identity = args.edgar_identity.strip()
        _validate_edgar_identity_format(normalized_identity)
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
            "`Full Name <email@example.com>` and write that value to `.env`."
        )

    token = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")

    if args.check:
        all_current = app_repo_current
        for runtime_name, skills_dir in runtime_skills_dirs.items():
            _print(f"Checking target [{runtime_name}] at {skills_dir}")
            for spec in specs:
                is_current, detail = _check_skill(
                    skills_dir=skills_dir,
                    spec=spec,
                    token=token,
                    latest=args.latest,
                )
                if is_current:
                    _print(f"[{runtime_name}][OK] {spec.name}: {detail}")
                else:
                    _print(f"[{runtime_name}][OUTDATED] {spec.name}: {detail}")
                    all_current = False
        _sync_project_skills(
            setup_skill_root=SETUP_SKILL_ROOT,
            py=Path(_best_python()),
            env=env,
            app_root=app_root,
            dry_run=False,
            check=True,
        )
        if all_current:
            _print("App repo and selected runtime skill targets are up to date.")
            return 0
        _print(
            "App repo and/or one or more selected runtime skill targets are not aligned "
            "with expected refs."
        )
        return 2

    venv_dir = app_root / ".venv"
    if args.dry_run:
        _print(f"[dry-run] would ensure venv: {venv_dir}")
        py = venv_dir / "bin" / "python"
    else:
        py = _ensure_venv(venv_dir)

    for runtime_name, skills_dir in runtime_skills_dirs.items():
        _print(f"Syncing target [{runtime_name}] at {skills_dir}")
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
                    "Installed skill "
                    f"{spec.name} is invalid for target [{runtime_name}]: "
                    f"SKILL.md not found at {resolved_root}"
                )

    _sync_project_skills(
        setup_skill_root=SETUP_SKILL_ROOT,
        py=py if not args.dry_run else Path(_best_python()),
        env=env,
        app_root=app_root,
        dry_run=args.dry_run,
        check=False,
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
