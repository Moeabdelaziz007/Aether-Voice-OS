"""
Aether Voice OS — Package Model.

Defines the .ath package structure with Pydantic validation
and SHA256 integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from core.utils.errors import ManifestValidationError, PackageCorruptError

logger = logging.getLogger(__name__)


class SoulManifest(BaseModel):
    """
    The soul of an Aether agent — defines identity, voice, and capabilities.

    Loaded from manifest.json inside a .ath package directory.
    """

    name: str = Field(..., min_length=1, max_length=64)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    persona: str = Field(..., min_length=1, description="Agent personality description")
    voice_id: str = Field("Puck", description="Gemini voice name")
    language: str = Field("ar-EG", description="Primary language (BCP-47)")
    capabilities: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    memory_tags: list[str] = Field(
        default_factory=list,
        description="Memory namespaces this agent is optimized for",
    )
    expertise: dict[str, float] = Field(
        default_factory=dict,
        description="Domain-specific expertise scores (0.0 to 1.0)",
    )
    author: Optional[str] = None
    checksum: Optional[str] = Field(None, description="SHA256 of the package contents")

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, v: list[str]) -> list[str]:
        """Ensure only known capabilities are declared."""
        known = {
            "audio.input",
            "audio.output",
            "text.input",
            "text.output",
            "tool.execute",
            "memory.read",
            "memory.write",
            "ui.render",
            "network.http",
        }
        unknown = set(v) - known
        if unknown:
            logger.warning("Unknown capabilities declared: %s", unknown)
        return v


class AthPackage:
    """
    Represents a loaded .ath agent package.

    A package is a directory containing:
      manifest.json   — Agent identity and capabilities
      prompts/        — System prompt templates
      tools/          — Custom tool definitions
    """

    def __init__(self, path: Path, manifest: SoulManifest) -> None:
        self.path = path
        self.manifest = manifest

    @classmethod
    def load(cls, package_dir: Path) -> AthPackage:
        """
        Load and validate a .ath package from a directory.

        Raises:
            ManifestValidationError: If manifest.json is invalid.
            PackageCorruptError: If checksum verification fails.
        """
        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise ManifestValidationError(
                f"No manifest.json found in {package_dir}",
                context={"path": str(package_dir)},
            )

        try:
            raw = manifest_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestValidationError(
                f"Invalid manifest.json: {exc}",
                cause=exc,
                context={"path": str(manifest_path)},
            ) from exc

        try:
            manifest = SoulManifest(**data)
        except Exception as exc:
            raise ManifestValidationError(
                f"Manifest validation failed: {exc}",
                cause=exc,
                context={"path": str(manifest_path), "data": data},
            ) from exc

        package = cls(package_dir, manifest)

        # Verify integrity if checksum is provided
        if manifest.checksum:
            actual = package.compute_checksum()
            if actual != manifest.checksum:
                raise PackageCorruptError(
                    f"Checksum mismatch for {manifest.name}: "
                    f"expected={manifest.checksum}, actual={actual}",
                    context={
                        "package": manifest.name,
                        "expected": manifest.checksum,
                        "actual": actual,
                    },
                )

        logger.info("Loaded package: %s v%s", manifest.name, manifest.version)
        return package

    def compute_checksum(self) -> str:
        """
        Compute SHA256 checksum of all package files (excluding manifest.json).

        Files are sorted alphabetically for deterministic output.
        """
        hasher = hashlib.sha256()
        files = sorted(
            f for f in self.path.rglob("*") if f.is_file() and f.name != "manifest.json"
        )
        for file_path in files:
            hasher.update(file_path.read_bytes())
        return hasher.hexdigest()

    def __repr__(self) -> str:
        return f"AthPackage({self.manifest.name} v{self.manifest.version})"
