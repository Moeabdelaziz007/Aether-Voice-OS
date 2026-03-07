from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, cast

SUPPORTED_FORMATS = {"json", "toml", "yaml", "yml"}


def detect_format(file_path: str) -> str:
    ext = Path(file_path).suffix.lower().lstrip(".")
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported AIX format: {ext}")
    return ext


def parse_aix_text(content: str, fmt: str) -> dict[str, Any]:
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported AIX format: {fmt}")

    if fmt == "json":
        parsed: Any = json.loads(content)
    elif fmt == "toml":
        import tomllib

        parsed = tomllib.loads(content)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise ValueError(
                "YAML parsing requires PyYAML, which is not installed."
            ) from exc
        parsed = yaml.safe_load(content)

    if not isinstance(parsed, dict):
        raise ValueError("AIX payload must be an object at the root.")
    parsed_map = cast(Mapping[str, Any], parsed)
    return dict(parsed_map)


def parse_aix_file(file_path: str) -> dict[str, Any]:
    fmt = detect_format(file_path)
    content = Path(file_path).read_text(encoding="utf-8")
    return parse_aix_text(content, fmt)


def dump_aix_text(payload: dict[str, Any], fmt: str) -> str:
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt}")

    if fmt == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)

    if fmt == "toml":
        raise ValueError("TOML export is not available in v0.1 without tomli-w.")

    try:
        import yaml
    except ImportError as exc:
        raise ValueError(
            "YAML export requires PyYAML, which is not installed."
        ) from exc
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
