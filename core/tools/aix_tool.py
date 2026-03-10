from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.adapters.aix_mapper import (
    aix_to_planet_profile,
    planet_profile_to_aix,
    validate_minimum_aix,
    verify_checksum,
)
from core.adapters.aix_parser import detect_format, dump_aix_text, parse_aix_file

_profiles: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def import_aix_profile(file_path: str, galaxy_id: str = "Genesis", **kwargs: Any) -> dict[str, Any]:
    try:
        payload = parse_aix_file(file_path)
    except Exception as exc:
        return {"status": "error", "message": f"failed_to_parse: {exc}"}

    missing = validate_minimum_aix(payload)
    if missing:
        return {
            "status": "error",
            "message": "missing_required_fields",
            "missing": missing,
        }

    checksum_ok, checksum_status = verify_checksum(payload)
    if not checksum_ok:
        return {"status": "error", "message": checksum_status}

    profile = aix_to_planet_profile(payload)
    profile["galaxy_id"] = galaxy_id
    profile["imported_at"] = _now_iso()
    _profiles[profile["planet_id"]] = profile

    return {
        "status": "imported",
        "planet_id": profile["planet_id"],
        "display_name": profile["display_name"],
        "capability_count": len(profile["capabilities"]),
        "galaxy_id": galaxy_id,
        "checksum_status": checksum_status,
    }


async def export_aix_profile(
    planet_id: str,
    output_path: str,
    format: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    profile = _profiles.get(planet_id)
    if not profile:
        return {"status": "error", "message": f"planet_not_found: {planet_id}"}

    fmt = format.lower() if format else detect_format(output_path)
    if fmt not in {"json", "toml", "yaml", "yml"}:
        return {"status": "error", "message": f"unsupported_format: {fmt}"}

    payload = planet_profile_to_aix(profile)
    try:
        text = dump_aix_text(payload, fmt)
    except Exception as exc:
        return {"status": "error", "message": f"failed_to_dump: {exc}"}

    Path(output_path).write_text(text, encoding="utf-8")

    return {
        "status": "exported",
        "planet_id": planet_id,
        "output_path": output_path,
        "format": fmt,
        "bytes": len(text.encode("utf-8")),
    }


async def list_imported_aix_profiles(**kwargs: Any) -> dict[str, Any]:
    items: list[dict[str, Any]] = [
        {
            "planet_id": p["planet_id"],
            "display_name": p["display_name"],
            "galaxy_id": p.get("galaxy_id", "Genesis"),
            "capability_count": len(p.get("capabilities", [])),
        }
        for p in _profiles.values()
    ]
    return {"status": "ok", "count": len(items), "profiles": items}


async def get_aix_profile_json(planet_id: str, **kwargs: Any) -> dict[str, Any]:
    profile = _profiles.get(planet_id)
    if not profile:
        return {"status": "error", "message": f"planet_not_found: {planet_id}"}
    return {"status": "ok", "planet_id": planet_id, "profile_json": json.dumps(profile)}


def get_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "import_aix_profile",
            "description": (
                "Import an AIX agent package file and register it as a planet profile inside a target galaxy."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to .json/.toml/.yaml AIX file",
                    },
                    "galaxy_id": {
                        "type": "string",
                        "description": "Target galaxy ID",
                    },
                },
                "required": ["file_path"],
            },
            "handler": import_aix_profile,
            "latency_tier": "p95_sub_2s",
            "idempotent": False,
        },
        {
            "name": "export_aix_profile",
            "description": ("Export an imported planet profile back to AIX format with checksum."),
            "parameters": {
                "type": "object",
                "properties": {
                    "planet_id": {"type": "string"},
                    "output_path": {"type": "string"},
                    "format": {
                        "type": "string",
                        "enum": ["json", "toml", "yaml", "yml"],
                    },
                },
                "required": ["planet_id", "output_path"],
            },
            "handler": export_aix_profile,
            "latency_tier": "p95_sub_2s",
            "idempotent": False,
        },
        {
            "name": "list_imported_aix_profiles",
            "description": "List imported AIX profiles currently registered in memory.",
            "parameters": {"type": "object", "properties": {}},
            "handler": list_imported_aix_profiles,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        },
    ]
