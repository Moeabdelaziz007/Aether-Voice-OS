"""
Aether Voice OS — Tests for Identity System.

Tests package loading, manifest validation, and
checksum verification.
"""

import json
from pathlib import Path

import pytest

from core.identity.package import AthPackage, SoulManifest
from core.services.registry import AetherRegistry
from core.utils.errors import ManifestValidationError, PackageCorruptError


@pytest.fixture
def valid_manifest() -> dict:
    return {
        "name": "aether-test",
        "version": "1.0.0",
        "persona": "A test agent for unit testing.",
        "voice_id": "Puck",
        "language": "en-US",
        "capabilities": ["audio.input", "audio.output"],
        "tools": [],
    }


@pytest.fixture
def package_dir(tmp_path: Path, valid_manifest: dict) -> Path:
    """Create a temporary valid .ath package."""
    pkg = tmp_path / "test-pkg"
    pkg.mkdir()
    (pkg / "manifest.json").write_text(json.dumps(valid_manifest))
    (pkg / "prompts").mkdir()
    (pkg / "prompts" / "system.txt").write_text("You are a test agent.")
    return pkg


class TestSoulManifest:
    """Tests for manifest validation."""

    def test_valid_manifest(self, valid_manifest):
        m = SoulManifest(**valid_manifest)
        assert m.name == "aether-test"
        assert m.version == "1.0.0"

    def test_missing_name(self, valid_manifest):
        del valid_manifest["name"]
        with pytest.raises(Exception):
            SoulManifest(**valid_manifest)

    def test_invalid_version_format(self, valid_manifest):
        valid_manifest["version"] = "1.0"
        with pytest.raises(Exception):
            SoulManifest(**valid_manifest)

    def test_unknown_capabilities_allowed(self, valid_manifest):
        valid_manifest["capabilities"] = ["audio.input", "quantum.teleport"]
        m = SoulManifest(**valid_manifest)  # Should warn but not raise
        assert "quantum.teleport" in m.capabilities


class TestAthPackage:
    """Tests for package loading."""

    def test_load_valid_package(self, package_dir):
        pkg = AthPackage.load(package_dir)
        assert pkg.manifest.name == "aether-test"

    def test_missing_manifest(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with pytest.raises(ManifestValidationError):
            AthPackage.load(empty_dir)

    def test_corrupt_json(self, tmp_path):
        pkg = tmp_path / "corrupt"
        pkg.mkdir()
        (pkg / "manifest.json").write_text("{bad json}")
        with pytest.raises(ManifestValidationError):
            AthPackage.load(pkg)

    def test_checksum_verification_pass(self, package_dir, valid_manifest):
        # First compute the real checksum
        pkg = AthPackage.load(package_dir)
        checksum = pkg.compute_checksum()

        # Write manifest with correct checksum
        valid_manifest["checksum"] = checksum
        (package_dir / "manifest.json").write_text(json.dumps(valid_manifest))

        # Should load without error
        pkg = AthPackage.load(package_dir)
        assert pkg.manifest.checksum == checksum

    def test_checksum_verification_fail(self, package_dir, valid_manifest):
        valid_manifest["checksum"] = "0000deadbeef"
        (package_dir / "manifest.json").write_text(json.dumps(valid_manifest))

        with pytest.raises(PackageCorruptError):
            AthPackage.load(package_dir)


class TestRegistry:
    """Tests for the package registry."""

    def test_scan_empty_directory(self, tmp_path):
        registry = AetherRegistry(str(tmp_path / "nonexistent"))
        assert registry.scan() == 0

    def test_scan_loads_packages(self, package_dir):
        registry = AetherRegistry(str(package_dir.parent))
        loaded = registry.scan()
        assert loaded == 1
        assert "aether-test" in registry.list_packages()

    def test_get_package(self, package_dir):
        registry = AetherRegistry(str(package_dir.parent))
        registry.scan()
        pkg = registry.get("aether-test")
        assert pkg.manifest.name == "aether-test"

    def test_get_missing_package(self, package_dir):
        registry = AetherRegistry(str(package_dir.parent))
        registry.scan()
        from core.utils.errors import PackageNotFoundError

        with pytest.raises(PackageNotFoundError):
            registry.get("nonexistent")
