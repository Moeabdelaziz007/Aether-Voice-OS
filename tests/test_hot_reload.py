import asyncio
import json

import pytest

from core.identity.registry import AetherRegistry


@pytest.mark.asyncio
async def test_registry_hot_reload(tmp_path):
    """Verify that adding a package directory is detected by the registry."""
    pkg_dir = tmp_path / "packages"
    pkg_dir.mkdir()

    reloaded_event = asyncio.Event()
    changed_pkg_name = None

    def on_change(name, pkg):
        nonlocal changed_pkg_name
        changed_pkg_name = name
        reloaded_event.set()

    registry = AetherRegistry(str(pkg_dir), on_change=on_change)
    registry.start_watcher()

    try:
        # 1. Create a mock package
        test_pkg = pkg_dir / "test_agent"
        test_pkg.mkdir()

        manifest = {
            "name": "test_agent",
            "version": "1.0.0",
            "persona": "Test persona",
            "voice_id": "Puck",
            "language": "en-US",
            "capabilities": ["text.output"],
        }

        manifest_file = test_pkg / "manifest.json"
        manifest_file.write_text(json.dumps(manifest))

        # 2. Wait for discovery
        try:
            await asyncio.wait_for(reloaded_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            pytest.fail("Registry did not detect new package after 5 seconds")

        assert changed_pkg_name == "test_agent"
        assert registry.count == 1
        assert registry.get("test_agent").manifest.version == "1.0.0"

        # 3. Update the package
        reloaded_event.clear()
        manifest["version"] = "1.1.0"
        manifest_file.write_text(json.dumps(manifest))

        await asyncio.wait_for(reloaded_event.wait(), timeout=5.0)
        assert registry.get("test_agent").manifest.version == "1.1.0"

        print("\n✨ Hot-Reloading: Verified (FS changes propagated to registry)")

    finally:
        registry.stop_watcher()
