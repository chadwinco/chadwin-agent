#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parents[1]
SHARED_SRC = SHARED_DIR / "src"

if str(SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(SHARED_SRC))

from company_idea_queue import (  # noqa: E402
    TASK_FETCH_JP,
    TASK_FETCH_US,
    TASK_RESEARCH,
    append_new_ideas,
    default_base_dir,
    pick_next_company,
    read_queue_entries,
    remove_company,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Manage the shared company-ideas queue used by fetch and research skills."
        )
    )
    parser.add_argument("--base-dir", default=str(default_base_dir()))
    parser.add_argument(
        "--ideas-log",
        help="Override ideas log path (default: idea-screens/company-ideas-log.jsonl).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    pick_parser = subparsers.add_parser(
        "pick", help="Pick the next company from the queue for a task."
    )
    pick_parser.add_argument(
        "--task",
        required=True,
        choices=[
            TASK_FETCH_US,
            TASK_FETCH_JP,
            TASK_RESEARCH,
            "us",
            "jp",
            "japan",
            "research",
            "fetch_us_company_data",
            "fetch_japanese_company_data",
            "run_company_research",
        ],
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Remove a company from the queue by ticker."
    )
    remove_parser.add_argument("--ticker", required=True)

    list_parser = subparsers.add_parser(
        "list", help="Print queue entries as JSON."
    )
    list_parser.add_argument(
        "--task",
        choices=[
            TASK_FETCH_US,
            TASK_FETCH_JP,
            TASK_RESEARCH,
            "us",
            "jp",
            "japan",
            "research",
            "fetch_us_company_data",
            "fetch_japanese_company_data",
            "run_company_research",
        ],
        help="Optional task filter.",
    )

    append_parser = subparsers.add_parser(
        "append-json",
        help="Append ideas from a JSON file containing an `ideas` list.",
    )
    append_parser.add_argument("--ideas-json", required=True)
    append_parser.add_argument("--source", default="manual")
    append_parser.add_argument("--generated-at-utc")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    base_dir = Path(args.base_dir)

    if args.command == "pick":
        entry = pick_next_company(
            base_dir=base_dir,
            task=args.task,
            ideas_log=args.ideas_log,
        )
        if not entry:
            print("No matching company found in the ideas log.", file=sys.stderr)
            return 1
        print(json.dumps(entry, indent=2))
        return 0

    if args.command == "remove":
        removed = remove_company(
            base_dir=base_dir,
            ticker=args.ticker,
            ideas_log=args.ideas_log,
        )
        print(json.dumps({"ticker": args.ticker, "removed": removed}, indent=2))
        return 0

    if args.command == "list":
        entries = read_queue_entries(base_dir=base_dir, ideas_log=args.ideas_log)
        if args.task:
            entry = pick_next_company(
                base_dir=base_dir,
                task=args.task,
                ideas_log=args.ideas_log,
            )
            entries = [entry] if entry else []
        print(json.dumps({"entries": entries}, indent=2))
        return 0

    if args.command == "append-json":
        payload = json.loads(Path(args.ideas_json).read_text(encoding="utf-8"))
        ideas = payload.get("ideas", [])
        generated_at_utc = args.generated_at_utc or payload.get("generated_at_utc")
        added = append_new_ideas(
            base_dir=base_dir,
            ideas=ideas,
            source=args.source,
            generated_at_utc=generated_at_utc,
            source_output=str(args.ideas_json),
            ideas_log=args.ideas_log,
        )
        print(json.dumps({"appended": added}, indent=2))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
