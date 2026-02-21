#!/usr/bin/env python3
"""Mirror bundled project skills from .agents/skills to .claude/skills."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def _repo_root(start: Path) -> Path:
    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in [candidate, *candidate.parents]:
        if (parent / ".git").exists():
            return parent
    return start.resolve()


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_REPO_ROOT = _repo_root(SCRIPT_PATH)
DEFAULT_SOURCE_ROOT = DEFAULT_REPO_ROOT / ".agents" / "skills"
DEFAULT_TARGET_ROOT = DEFAULT_REPO_ROOT / ".claude" / "skills"


def _is_ignored(path: Path) -> bool:
    if path.name in IGNORED_NAMES:
        return True
    if path.suffix in IGNORED_SUFFIXES:
        return True
    return any(part in IGNORED_NAMES for part in path.parts)


def _iter_skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if _is_ignored(entry):
            continue
        out.append(entry)
    return out


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for candidate in root.rglob("*"):
        if _is_ignored(candidate):
            continue
        if candidate.is_file():
            files.append(candidate)
    return sorted(files, key=lambda p: str(p))


def _relative_file_set(root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in _iter_files(root)}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _remove_empty_dirs(root: Path) -> int:
    removed = 0
    if not root.exists():
        return removed
    for candidate in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not candidate.is_dir():
            continue
        if _is_ignored(candidate):
            continue
        try:
            candidate.rmdir()
            removed += 1
        except OSError:
            continue
    return removed


def check_sync(source_root: Path, target_root: Path) -> int:
    if not source_root.exists():
        print(f"[ERROR] Source skills root does not exist: {source_root}")
        return 2

    issues: list[str] = []
    source_skills = _iter_skill_dirs(source_root)
    target_skills = _iter_skill_dirs(target_root)
    source_skill_names = {path.name for path in source_skills}
    target_skill_names = {path.name for path in target_skills}

    for missing in sorted(source_skill_names - target_skill_names):
        issues.append(f"[MISSING SKILL] {target_root / missing}")
    for extra in sorted(target_skill_names - source_skill_names):
        issues.append(f"[EXTRA SKILL] {target_root / extra}")

    for source_skill in source_skills:
        target_skill = target_root / source_skill.name
        source_files = _relative_file_set(source_skill)
        target_files = _relative_file_set(target_skill)

        for missing_file in sorted(source_files - target_files):
            issues.append(f"[MISSING FILE] {target_skill / missing_file}")
        for extra_file in sorted(target_files - source_files):
            issues.append(f"[EXTRA FILE] {target_skill / extra_file}")
        for common_file in sorted(source_files & target_files):
            source_file = source_skill / common_file
            target_file = target_skill / common_file
            if not filecmp.cmp(source_file, target_file, shallow=False):
                issues.append(f"[CHANGED FILE] {target_file}")

    if issues:
        print("[ERROR] Skill mirror drift detected:")
        for issue in issues:
            print(f"- {issue}")
        return 2

    print(f"[OK] .claude skill mirror is in sync with source: {source_root} -> {target_root}")
    return 0


def run_sync(source_root: Path, target_root: Path) -> int:
    if not source_root.exists():
        print(f"[ERROR] Source skills root does not exist: {source_root}")
        return 2

    copied = 0
    removed_files = 0
    removed_dirs = 0

    target_root.mkdir(parents=True, exist_ok=True)

    source_skills = _iter_skill_dirs(source_root)
    source_skill_names = {path.name for path in source_skills}
    target_skill_names = {path.name for path in _iter_skill_dirs(target_root)}

    for source_skill in source_skills:
        target_skill = target_root / source_skill.name
        target_skill.mkdir(parents=True, exist_ok=True)

        source_files = _relative_file_set(source_skill)
        target_files = _relative_file_set(target_skill)

        for relpath in sorted(source_files):
            src = source_skill / relpath
            dst = target_skill / relpath
            _ensure_parent(dst)
            shutil.copy2(src, dst)
            copied += 1

        for relpath in sorted(target_files - source_files):
            stale = target_skill / relpath
            stale.unlink(missing_ok=True)
            removed_files += 1

        removed_dirs += _remove_empty_dirs(target_skill)

    for stale_skill in sorted(target_skill_names - source_skill_names):
        stale_dir = target_root / stale_skill
        shutil.rmtree(stale_dir)
        removed_dirs += 1

    print(
        "[OK] Synced project skill mirror "
        f"{source_root} -> {target_root} "
        f"(copied={copied}, removed_files={removed_files}, removed_dirs={removed_dirs})"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync bundled skills from .agents/skills to .claude/skills."
    )
    parser.add_argument(
        "--source-root",
        default=str(DEFAULT_SOURCE_ROOT),
        help="Source skills root (default: <repo>/.agents/skills).",
    )
    parser.add_argument(
        "--target-root",
        default=str(DEFAULT_TARGET_ROOT),
        help="Target skills root (default: <repo>/.claude/skills).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift without mutating files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).expanduser().resolve()
    target_root = Path(args.target_root).expanduser().resolve()
    if args.check:
        return check_sync(source_root=source_root, target_root=target_root)
    return run_sync(source_root=source_root, target_root=target_root)


if __name__ == "__main__":
    raise SystemExit(main())
