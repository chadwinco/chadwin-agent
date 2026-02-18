#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from data_paths import detect_repo_root
from edgar_fetch import ensure_edgar_identity, filing_markdown
from loaders import _require_pandas

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


def _default_base_dir() -> Path:
    return detect_repo_root(Path(__file__).resolve())


def _helper_take(iterable: Iterable[Any], count: int) -> list[Any]:
    if count <= 0:
        return []
    items: list[Any] = []
    for idx, item in enumerate(iterable):
        if idx >= count:
            break
        items.append(item)
    return items


def _helper_first(iterable: Iterable[Any], default: Any = None) -> Any:
    for item in iterable:
        return item
    return default


def _helper_filing_markdown(
    filing: Any,
    include_attachments: bool = False,
    attachment_form: Optional[str] = None,
) -> str:
    attachment_forms = {attachment_form} if attachment_form else None
    return filing_markdown(
        filing,
        include_attachments=include_attachments,
        attachment_forms=attachment_forms,
    )


def _build_namespace() -> dict[str, Any]:
    import edgar  # type: ignore

    return {
        "edgar": edgar,
        "py": {
            "list": list,
            "len": len,
            "sorted": sorted,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "sum": sum,
            "min": min,
            "max": max,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
        },
        "helpers": {
            "take": _helper_take,
            "first": _helper_first,
            "filing_markdown": _helper_filing_markdown,
        },
    }


def _type_name(value: Any) -> str:
    return f"{value.__class__.__module__}.{value.__class__.__name__}"


def _optional_pandas():
    try:
        return _require_pandas()
    except Exception:
        return None


def _to_json_ready(
    value: Any,
    *,
    max_depth: int = 8,
    max_items: int = 2000,
    _depth: int = 0,
    _seen: Optional[set[int]] = None,
) -> Any:
    if _seen is None:
        _seen = set()

    if _depth > max_depth:
        return {
            "__truncated__": True,
            "__type__": _type_name(value),
            "__repr__": repr(value),
        }

    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return {"__base64__": base64.b64encode(value).decode("ascii")}

    if isinstance(value, Mapping):
        obj_id = id(value)
        if obj_id in _seen:
            return {"__recursive__": True, "__type__": _type_name(value)}
        _seen.add(obj_id)
        items = list(value.items())
        limited = items[:max_items]
        out = {
            str(k): _to_json_ready(
                v,
                max_depth=max_depth,
                max_items=max_items,
                _depth=_depth + 1,
                _seen=_seen,
            )
            for k, v in limited
        }
        if len(items) > max_items:
            out["__truncated_items__"] = len(items) - max_items
        _seen.remove(obj_id)
        return out

    if isinstance(value, (list, tuple, set)):
        obj_id = id(value)
        if obj_id in _seen:
            return {"__recursive__": True, "__type__": _type_name(value)}
        _seen.add(obj_id)
        items = list(value)
        limited = items[:max_items]
        out = [
            _to_json_ready(
                item,
                max_depth=max_depth,
                max_items=max_items,
                _depth=_depth + 1,
                _seen=_seen,
            )
            for item in limited
        ]
        if len(items) > max_items:
            out.append({"__truncated_items__": len(items) - max_items})
        _seen.remove(obj_id)
        return out

    pd = _optional_pandas()
    if pd is not None:
        if isinstance(value, pd.DataFrame):
            records = value.to_dict(orient="records")
            return _to_json_ready(
                records,
                max_depth=max_depth,
                max_items=max_items,
                _depth=_depth + 1,
                _seen=_seen,
            )
        if isinstance(value, pd.Series):
            as_dict = value.to_dict()
            return _to_json_ready(
                as_dict,
                max_depth=max_depth,
                max_items=max_items,
                _depth=_depth + 1,
                _seen=_seen,
            )

    if is_dataclass(value):
        return _to_json_ready(
            asdict(value),
            max_depth=max_depth,
            max_items=max_items,
            _depth=_depth + 1,
            _seen=_seen,
        )

    for method_name in ("to_dict", "model_dump"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                payload = method()
                return _to_json_ready(
                    payload,
                    max_depth=max_depth,
                    max_items=max_items,
                    _depth=_depth + 1,
                    _seen=_seen,
                )
            except Exception:
                continue

    for method_name in ("to_pandas", "to_dataframe"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                payload = method()
                return _to_json_ready(
                    payload,
                    max_depth=max_depth,
                    max_items=max_items,
                    _depth=_depth + 1,
                    _seen=_seen,
                )
            except Exception:
                continue

    try:
        raw = {
            key: val
            for key, val in vars(value).items()
            if not str(key).startswith("_")
        }
    except Exception:
        raw = {}

    if raw:
        return {
            "__type__": _type_name(value),
            "fields": _to_json_ready(
                raw,
                max_depth=max_depth,
                max_items=max_items,
                _depth=_depth + 1,
                _seen=_seen,
            ),
        }

    return {"__type__": _type_name(value), "__repr__": repr(value)}


def _to_dataframe(value: Any, *, kwargs: Optional[dict[str, Any]] = None):
    pd = _require_pandas()
    options = kwargs or {}

    if isinstance(value, pd.DataFrame):
        return value.copy()

    if isinstance(value, pd.Series):
        return value.to_frame().transpose()

    for method_name in ("to_pandas", "to_dataframe"):
        method = getattr(value, method_name, None)
        if not callable(method):
            continue
        try:
            frame = method(**options)
        except TypeError:
            frame = method()
        if isinstance(frame, pd.DataFrame):
            return frame
        if isinstance(frame, pd.Series):
            return frame.to_frame().transpose()

    if isinstance(value, Mapping):
        return pd.DataFrame([dict(value)])

    if isinstance(value, (list, tuple, set)):
        items = list(value)
        if not items:
            return pd.DataFrame()
        if all(isinstance(item, Mapping) for item in items):
            return pd.DataFrame(items)
        normalized = [
            _to_json_ready(item, max_depth=4, max_items=200)
            for item in items
        ]
        if all(isinstance(item, Mapping) for item in normalized):
            return pd.DataFrame(normalized)
        return pd.DataFrame({"value": normalized})

    normalized = _to_json_ready(value, max_depth=4, max_items=200)
    if isinstance(normalized, Mapping):
        return pd.DataFrame([normalized])
    if isinstance(normalized, list):
        if all(isinstance(item, Mapping) for item in normalized):
            return pd.DataFrame(normalized)
        return pd.DataFrame({"value": normalized})
    return pd.DataFrame({"value": [normalized]})


def _render_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return base64.b64encode(value).decode("ascii")

    text_method = getattr(value, "text", None)
    if callable(text_method):
        try:
            rendered = text_method()
            if rendered is not None:
                return str(rendered)
        except Exception:
            pass

    return str(value)


def _render_markdown(value: Any, *, include_attachments: bool = False) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    markdown_method = getattr(value, "markdown", None)
    if callable(markdown_method):
        try:
            rendered = markdown_method()
            if rendered:
                return str(rendered)
        except Exception:
            pass

    if include_attachments:
        try:
            return _helper_filing_markdown(value, include_attachments=True)
        except Exception:
            pass

    return _render_text(value)


def _infer_format(path: Path, value: Any) -> str:
    suffix = path.suffix.lower()
    if suffix in {".json"}:
        return "json"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix in {".csv"}:
        return "csv"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix in {".txt", ".log", ".xml"}:
        return "text"
    if isinstance(value, str):
        return "text"
    return "json"


def _resolve_output_path(path_value: str, output_root: Optional[Path], base_dir: Path) -> Path:
    candidate = Path(path_value).expanduser()
    if candidate.is_absolute():
        return candidate
    if output_root is not None:
        return (output_root / candidate).resolve()
    return (base_dir / candidate).resolve()


def _export_value(
    value: Any,
    spec: Mapping[str, Any],
    *,
    output_root: Optional[Path],
    base_dir: Path,
) -> dict[str, Any]:
    target_rel = str(spec.get("path") or "").strip()
    if not target_rel:
        raise ValueError("Export spec requires a non-empty 'path'.")

    target = _resolve_output_path(target_rel, output_root=output_root, base_dir=base_dir)
    target.parent.mkdir(parents=True, exist_ok=True)

    fmt = str(spec.get("format") or "").strip().lower()
    if not fmt or fmt == "auto":
        fmt = _infer_format(target, value)

    if fmt == "json":
        payload = _to_json_ready(
            value,
            max_depth=int(spec.get("max_depth", 8)),
            max_items=int(spec.get("max_items", 2000)),
        )
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    elif fmt == "yaml":
        if yaml is None:
            raise RuntimeError("YAML export requested but pyyaml is not installed.")
        payload = _to_json_ready(
            value,
            max_depth=int(spec.get("max_depth", 8)),
            max_items=int(spec.get("max_items", 2000)),
        )
        target.write_text(yaml.safe_dump(payload, sort_keys=False))
    elif fmt == "csv":
        frame_kwargs = spec.get("dataframe_kwargs")
        if frame_kwargs is not None and not isinstance(frame_kwargs, Mapping):
            raise ValueError("dataframe_kwargs must be an object when provided.")
        frame = _to_dataframe(value, kwargs=dict(frame_kwargs or {}))
        frame.to_csv(target, index=bool(spec.get("index", False)))
    elif fmt == "markdown":
        include_attachments = bool(spec.get("include_attachments", False))
        target.write_text(_render_markdown(value, include_attachments=include_attachments))
    elif fmt == "text":
        target.write_text(_render_text(value))
    elif fmt == "bytes":
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, str):
            data = value.encode("utf-8")
        else:
            raise ValueError("bytes export requires a bytes or string value.")
        target.write_bytes(data)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

    return {"path": str(target), "format": fmt}


def _summarize_value(value: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"type": _type_name(value)}
    try:
        summary["len"] = len(value)  # type: ignore[arg-type]
    except Exception:
        pass
    if value is None:
        summary["state"] = "none"
        return summary
    if isinstance(value, str):
        summary["chars"] = len(value)
        preview = value.strip().replace("\n", " ")
        summary["preview"] = preview[:140]
    return summary


def _split_path(path: str) -> list[str]:
    value = path.strip()
    if not value:
        raise ValueError("Empty path is not allowed.")

    parts: list[str] = []
    current: list[str] = []
    bracket_depth = 0
    for ch in value:
        if ch == "." and bracket_depth == 0:
            part = "".join(current).strip()
            if not part:
                raise ValueError(f"Invalid path segment in {path!r}.")
            parts.append(part)
            current = []
            continue
        if ch == "[":
            bracket_depth += 1
        elif ch == "]":
            bracket_depth -= 1
            if bracket_depth < 0:
                raise ValueError(f"Unbalanced brackets in path {path!r}.")
        current.append(ch)

    if bracket_depth != 0:
        raise ValueError(f"Unbalanced brackets in path {path!r}.")

    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


_SEGMENT_PATTERN = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)?(?P<indexes>(\[[^\]]+\])*)$")
_INDEX_PATTERN = re.compile(r"\[([^\]]+)\]")


def _parse_segment(segment: str) -> tuple[Optional[str], list[str]]:
    match = _SEGMENT_PATTERN.match(segment.strip())
    if not match:
        raise ValueError(f"Invalid path segment {segment!r}.")
    name = match.group("name")
    indexes = _INDEX_PATTERN.findall(match.group("indexes") or "")
    return name, indexes


def _parse_index(token: str) -> Any:
    raw = token.strip()
    if not raw:
        raise ValueError("Empty index token is not allowed.")
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
        return raw[1:-1]
    if raw.lstrip("-").isdigit():
        return int(raw)
    return raw


def _resolve_from_object(obj: Any, segment: str) -> Any:
    name, indexes = _parse_segment(segment)
    current = obj

    if name:
        if isinstance(current, Mapping) and name in current:
            current = current[name]
        else:
            current = getattr(current, name)

    for token in indexes:
        key = _parse_index(token)
        current = current[key]
    return current


def _resolve_path(path: str, refs: Mapping[str, Any]) -> Any:
    segments = _split_path(path)
    first_name, first_indexes = _parse_segment(segments[0])
    if not first_name:
        raise ValueError(f"Path {path!r} must start with a reference name.")
    if first_name not in refs:
        available = ", ".join(sorted(refs.keys()))
        raise KeyError(f"Unknown reference '{first_name}'. Available: {available}")

    current = refs[first_name]
    for token in first_indexes:
        key = _parse_index(token)
        current = current[key]

    for segment in segments[1:]:
        current = _resolve_from_object(current, segment)
    return current


def _resolve_value(
    value: Any,
    refs: Mapping[str, Any],
    variables: Mapping[str, Any],
) -> Any:
    if isinstance(value, list):
        return [_resolve_value(item, refs, variables) for item in value]

    if isinstance(value, Mapping):
        if set(value.keys()) == {"$ref"}:
            return _resolve_path(str(value["$ref"]), refs)
        if set(value.keys()) == {"$path"}:
            return _resolve_path(str(value["$path"]), refs)
        if set(value.keys()) == {"$var"}:
            var_name = str(value["$var"])
            if var_name not in variables:
                raise KeyError(f"Unknown variable '{var_name}'.")
            return variables[var_name]
        if "$env" in value:
            env_name = str(value["$env"])
            default = value.get("default")
            return os.getenv(env_name, default)
        if set(value.keys()) == {"$literal"}:
            return value["$literal"]
        return {k: _resolve_value(v, refs, variables) for k, v in value.items()}

    return value


def _normalize_exports(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, Mapping):
        return [dict(raw)]
    if isinstance(raw, list):
        out = []
        for item in raw:
            if not isinstance(item, Mapping):
                raise ValueError("Each export spec must be an object.")
            out.append(dict(item))
        return out
    raise ValueError("Export spec must be an object or list of objects.")


def run_request(
    request: Mapping[str, Any],
    *,
    base_dir: Path,
    output_root: Optional[Path],
    identity_override: Optional[str] = None,
) -> dict[str, Any]:
    namespace = _build_namespace()
    refs: dict[str, Any] = dict(namespace)
    variables: dict[str, Any] = {}

    identity_required = bool(request.get("identity_required", True))
    request_identity = request.get("identity")
    identity_value = identity_override if identity_override is not None else request_identity

    identity_status = "skipped"
    if identity_required or identity_value:
        ensure_edgar_identity(
            str(identity_value) if identity_value is not None else None,
            base_dir=base_dir,
        )
        identity_status = "configured"

    raw_variables = request.get("variables", {})
    if raw_variables is not None:
        if not isinstance(raw_variables, Mapping):
            raise ValueError("'variables' must be an object when provided.")
        for key, val in raw_variables.items():
            variables[str(key)] = _resolve_value(val, refs, variables)

    steps = request.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("Request must include a non-empty 'steps' list.")

    step_reports: list[dict[str, Any]] = []
    all_exports: list[dict[str, Any]] = []

    for index, raw_step in enumerate(steps, start=1):
        if not isinstance(raw_step, Mapping):
            raise ValueError(f"Step {index} must be an object.")
        step = dict(raw_step)
        step_id = str(step.get("id") or f"step_{index}")
        if step_id in refs:
            raise ValueError(f"Step id '{step_id}' is already in use.")

        if "call" in step:
            callable_path = str(step["call"])
            target = _resolve_path(callable_path, refs)
            if not callable(target):
                raise TypeError(f"Resolved path '{callable_path}' is not callable.")
            raw_args = step.get("args", [])
            if raw_args is None:
                raw_args = []
            if not isinstance(raw_args, list):
                raise ValueError(f"Step '{step_id}' args must be a list.")
            raw_kwargs = step.get("kwargs", {})
            if raw_kwargs is None:
                raw_kwargs = {}
            if not isinstance(raw_kwargs, Mapping):
                raise ValueError(f"Step '{step_id}' kwargs must be an object.")

            args = [_resolve_value(arg, refs, variables) for arg in raw_args]
            kwargs = {
                str(k): _resolve_value(v, refs, variables)
                for k, v in raw_kwargs.items()
            }
            result = target(*args, **kwargs)
            operation = "call"
        elif "read" in step:
            read_path = str(step["read"])
            result = _resolve_path(read_path, refs)
            operation = "read"
        elif "value" in step:
            result = _resolve_value(step["value"], refs, variables)
            operation = "value"
        else:
            raise ValueError(
                f"Step '{step_id}' must include one of: call, read, value."
            )

        refs[step_id] = result

        step_exports: list[dict[str, Any]] = []
        for export_spec in _normalize_exports(step.get("save")):
            export_info = _export_value(
                result,
                export_spec,
                output_root=output_root,
                base_dir=base_dir,
            )
            export_info["step_id"] = step_id
            step_exports.append(export_info)
            all_exports.append(export_info)

        step_reports.append(
            {
                "id": step_id,
                "operation": operation,
                "summary": _summarize_value(result),
                "exports": step_exports,
            }
        )

    for output_spec in _normalize_exports(request.get("outputs")):
        ref_path = str(output_spec.get("ref") or "").strip()
        if not ref_path:
            raise ValueError("Each output spec requires a non-empty 'ref'.")
        value = _resolve_path(ref_path, refs)
        spec_without_ref = {k: v for k, v in output_spec.items() if k != "ref"}
        export_info = _export_value(
            value,
            spec_without_ref,
            output_root=output_root,
            base_dir=base_dir,
        )
        export_info["ref"] = ref_path
        all_exports.append(export_info)

    return {
        "ok": True,
        "identity_status": identity_status,
        "steps": step_reports,
        "exports": all_exports,
        "available_refs": sorted(refs.keys()),
    }


def _load_request(request_file: Optional[str], request_json: Optional[str]) -> dict[str, Any]:
    if bool(request_file) == bool(request_json):
        raise ValueError("Provide exactly one of --request-file or --request-json.")

    if request_json:
        payload = json.loads(request_json)
        if not isinstance(payload, Mapping):
            raise ValueError("Request JSON must evaluate to an object.")
        return dict(payload)

    assert request_file is not None
    path = Path(request_file).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Request file not found: {path}")

    text = path.read_text()
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("YAML request file provided but pyyaml is not installed.")
        payload = yaml.safe_load(text)
    else:
        payload = json.loads(text)

    if not isinstance(payload, Mapping):
        raise ValueError(f"Request file {path} did not parse to an object.")
    return dict(payload)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generic edgartools wrapper for agentic workflows. "
            "Runs declarative read/call steps and exports selected artifacts."
        )
    )
    parser.add_argument(
        "--request-file",
        help="Path to JSON or YAML request document.",
    )
    parser.add_argument(
        "--request-json",
        help="Inline JSON request document.",
    )
    parser.add_argument(
        "--identity",
        help="Optional EDGAR identity override (Name email@domain.com).",
    )
    parser.add_argument(
        "--output-root",
        help=(
            "Optional base directory for relative export paths. "
            "Defaults to repo root when omitted."
        ),
    )
    parser.add_argument(
        "--base-dir",
        default=str(_default_base_dir()),
        help="Repository base directory used for identity loading and relative defaults.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    base_dir = Path(args.base_dir).resolve()
    output_root = Path(args.output_root).expanduser().resolve() if args.output_root else base_dir

    try:
        request = _load_request(args.request_file, args.request_json)
        result = run_request(
            request,
            base_dir=base_dir,
            output_root=output_root,
            identity_override=args.identity,
        )
    except Exception as exc:
        error_payload = {"ok": False, "error": str(exc)}
        print(json.dumps(error_payload, indent=2 if args.pretty else None))
        return 1

    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
