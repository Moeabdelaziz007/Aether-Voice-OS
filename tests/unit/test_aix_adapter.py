from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from core.adapters.aix_mapper import (
    aix_to_planet_profile,
    generate_checksum_sha256,
    planet_profile_to_aix,
    validate_minimum_aix,
    verify_checksum,
)
from core.adapters.aix_parser import dump_aix_text, parse_aix_text
from core.tools import aix_tool


def _sample_aix() -> dict[str, Any]:
    return {
        "meta": {"version": "1.0", "id": "planet-001", "name": "Codex Planet"},
        "persona": {
            "role": "architect assistant",
            "tone": "focused",
            "instructions": "Be concise and precise.",
        },
        "skills": [
            {"name": "code_review", "enabled": True},
            {"name": "draft_docs", "enabled": False},
        ],
        "network": {"allowed_domains": ["github.com"]},
        "security": {"checksum": {"algorithm": "sha256", "value": ""}},
    }


def test_parse_and_dump_json_roundtrip():
    payload = _sample_aix()
    as_text = dump_aix_text(payload, "json")
    parsed = parse_aix_text(as_text, "json")
    assert parsed["meta"]["id"] == "planet-001"
    assert parsed["persona"]["role"] == "architect assistant"


def test_validate_minimum_fields():
    payload: dict[str, Any] = {"meta": {"name": "x"}, "persona": {}}
    missing = validate_minimum_aix(payload)
    assert "meta.id" in missing
    assert "persona.role" in missing


def test_checksum_generation_and_verification():
    payload = _sample_aix()
    payload["security"]["checksum"]["value"] = generate_checksum_sha256(payload)
    ok, status = verify_checksum(payload)
    assert ok is True
    assert status == "checksum_valid"


def test_mapper_aix_to_planet():
    payload = _sample_aix()
    payload["security"]["checksum"]["value"] = generate_checksum_sha256(payload)
    profile = aix_to_planet_profile(payload)
    assert profile["planet_id"] == "planet-001"
    assert profile["display_name"] == "Codex Planet"
    assert "code_review" in profile["capabilities"]
    assert "draft_docs" not in profile["capabilities"]


def test_mapper_planet_to_aix_checksum_populated():
    profile: dict[str, Any] = {
        "planet_id": "planet-002",
        "display_name": "Voyager",
        "profile_version": "0.1",
        "persona": {"role": "browser", "tone": "calm", "instructions": "Navigate"},
        "capabilities": ["browse_web", "extract_data"],
        "policy_overlay": {"allowed_domains": ["example.com"]},
    }
    aix_payload = planet_profile_to_aix(profile)
    assert aix_payload["meta"]["id"] == "planet-002"
    assert aix_payload["security"]["checksum"]["value"]


def test_aix_tool_import_export_cycle(tmp_path: Path):
    payload = _sample_aix()
    payload["security"]["checksum"]["value"] = generate_checksum_sha256(payload)

    src_file = tmp_path / "agent.json"
    src_file.write_text(json.dumps(payload), encoding="utf-8")

    imported = asyncio.run(
        aix_tool.import_aix_profile(
            file_path=str(src_file),
            galaxy_id="gal-test",
        )
    )
    assert imported["status"] == "imported"
    assert imported["planet_id"] == "planet-001"

    out_file = tmp_path / "agent-export.json"
    exported = asyncio.run(
        aix_tool.export_aix_profile(
            planet_id="planet-001",
            output_path=str(out_file),
            format="json",
        )
    )
    assert exported["status"] == "exported"
    assert out_file.exists()
