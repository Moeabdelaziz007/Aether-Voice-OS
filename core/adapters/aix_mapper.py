from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

REQUIRED_AIX_FIELDS = ("meta.id", "meta.name", "persona.role")


def _deep_get(payload: dict[str, Any], dotted_key: str) -> Any:
    current: Any = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def validate_minimum_aix(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key in REQUIRED_AIX_FIELDS:
        value = _deep_get(payload, key)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(key)
    return missing


def canonical_bytes_for_checksum(payload: dict[str, Any]) -> bytes:
    normalized = deepcopy(payload)
    security = normalized.get("security")
    if isinstance(security, dict):
        checksum = security.get("checksum")
        if isinstance(checksum, dict):
            checksum.pop("value", None)
    encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return encoded


def generate_checksum_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes_for_checksum(payload)).hexdigest()


def verify_checksum(payload: dict[str, Any]) -> tuple[bool, str]:
    security = payload.get("security", {})
    checksum_info = security.get("checksum", {}) if isinstance(security, dict) else {}
    expected = checksum_info.get("value") if isinstance(checksum_info, dict) else None
    if not expected:
        return True, "checksum_not_provided"
    calculated = generate_checksum_sha256(payload)
    status = "checksum_valid" if calculated == expected else "checksum_mismatch"
    return calculated == expected, status


def aix_to_planet_profile(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("meta", {})
    persona = payload.get("persona", {})
    skills = payload.get("skills", [])
    security = payload.get("security", {})
    network = payload.get("network", {})
    requirements = payload.get("requirements", {})

    enabled_capabilities: list[str] = []
    if isinstance(skills, list):
        for skill in skills:
            if isinstance(skill, dict) and skill.get("enabled", True):
                name = str(skill.get("name", "")).strip()
                if name:
                    enabled_capabilities.append(name)

    profile = {
        "planet_id": str(meta.get("id", "")),
        "display_name": str(meta.get("name", "Unnamed Planet")),
        "profile_version": str(meta.get("version", "0.1")),
        "persona": {
            "role": str(persona.get("role", "assistant")),
            "tone": str(persona.get("tone", "neutral")),
            "instructions": str(persona.get("instructions", "")),
        },
        "capabilities": enabled_capabilities,
        "mcp_endpoints": payload.get("mcp", {}).get("servers", []) if isinstance(payload.get("mcp"), dict) else [],
        "tool_bindings": payload.get("tools", []),
        "memory": payload.get("memory", {}),
        "integrity": {
            "checksum": (security.get("checksum", {}) if isinstance(security, dict) else {}),
            "signature": (security.get("signature", {}) if isinstance(security, dict) else {}),
        },
        "runtime_requirements": requirements,
        "policy_overlay": {"allowed_domains": network.get("allowed_domains", []) if isinstance(network, dict) else []},
        "raw_aix": payload,
    }
    return profile


def planet_profile_to_aix(profile: dict[str, Any], fmt_version: str = "0.1") -> dict[str, Any]:
    payload: dict[str, Any] = {
        "meta": {
            "version": str(profile.get("profile_version", fmt_version)),
            "id": str(profile.get("planet_id", "")),
            "name": str(profile.get("display_name", "Unnamed Planet")),
        },
        "persona": {
            "role": profile.get("persona", {}).get("role", "assistant"),
            "tone": profile.get("persona", {}).get("tone", "neutral"),
            "instructions": profile.get("persona", {}).get("instructions", ""),
        },
        "skills": [
            {"name": name, "enabled": True}
            for name in profile.get("capabilities", [])
            if isinstance(name, str) and name.strip()
        ],
        "tools": profile.get("tool_bindings", []),
        "mcp": {"servers": profile.get("mcp_endpoints", [])},
        "memory": profile.get("memory", {}),
        "requirements": profile.get("runtime_requirements", {}),
        "network": {"allowed_domains": profile.get("policy_overlay", {}).get("allowed_domains", [])},
        "security": {
            "checksum": {"algorithm": "sha256", "value": ""},
            "signature": profile.get("integrity", {}).get("signature", {}),
        },
    }
    payload["security"]["checksum"]["value"] = generate_checksum_sha256(payload)
    return payload
