import json
from pathlib import Path

import pytest

from core.services.registry import AetherRegistry


@pytest.fixture
def registry(tmp_path):
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()
    return AetherRegistry(str(packages_dir))

def create_package(packages_dir, name, client_id=None, public_key=None):
    pkg_dir = packages_dir / name
    pkg_dir.mkdir()
    manifest = {
        "name": name,
        "version": "1.0.0",
        "persona": f"Persona of {name}",
        "voice_id": "Puck",
        "language": "en-US",
    }
    if client_id:
        manifest["id"] = client_id
    if public_key:
        manifest["public_key"] = public_key

    (pkg_dir / "manifest.json").write_text(json.dumps(manifest))
    return pkg_dir

def test_get_package_by_client_id_optimized(registry, tmp_path):
    packages_dir = Path(registry._dir)

    # Create two packages
    create_package(packages_dir, "pkg1", client_id="client1", public_key="pub1")
    create_package(packages_dir, "pkg2", client_id="client2", public_key="pub2")

    registry.scan()
    registry.get("pkg1") # Trigger lazy load
    registry.get("pkg2") # Trigger lazy load

    # Test lookup by client_id
    assert registry.get_package_by_client_id("client1").manifest.name == "pkg1"
    assert registry.get_package_by_client_id("client2").manifest.name == "pkg2"

    # Test lookup by public_key
    assert registry.get_package_by_client_id("pub1").manifest.name == "pkg1"
    assert registry.get_package_by_client_id("pub2").manifest.name == "pkg2"

    # Test non-existent
    assert registry.get_package_by_client_id("nonexistent") is None

def test_get_package_by_client_id_after_reload(registry, tmp_path):
    packages_dir = Path(registry._dir)
    pkg_dir = create_package(packages_dir, "pkg1", client_id="old_client")

    registry.scan()
    registry.get("pkg1")

    assert registry.get_package_by_client_id("old_client").manifest.name == "pkg1"

    # Update package manifest
    manifest = {
        "name": "pkg1",
        "version": "1.1.0",
        "persona": "Updated persona",
        "id": "new_client"
    }
    (pkg_dir / "manifest.json").write_text(json.dumps(manifest))

    # Manually trigger reload
    registry.load_package(pkg_dir)

    assert registry.get_package_by_client_id("new_client").manifest.name == "pkg1"
    # Verify that the old key is invalidated after rebuild
    assert registry.get_package_by_client_id("old_client") is None
