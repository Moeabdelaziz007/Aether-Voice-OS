"""
Tests for AetherRegistry hot-loading.
"""

import asyncio
from pathlib import Path
import pytest
import shutil
from unittest.mock import AsyncMock

from core.services.registry import AetherRegistry

@pytest.mark.asyncio
async def test_aether_registry_hot_loading(tmp_path):
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()
    
    on_change_mock = AsyncMock()
    
    registry = AetherRegistry(packages_dir=str(packages_dir), on_change=on_change_mock)
    registry.scan()
    registry.start_watcher()
    
    try:
        pkg_dir = packages_dir / "TestAgent"
        pkg_dir.mkdir()
        manifest_file = pkg_dir / "manifest.json"
        
        manifest_content = '{"name": "TestAgent", "client_id": "test_agent_v1", "version": "1.0.0", "description": "Test", "expertise": {"test": 1.0}, "persona": "Direct Tester"}'
        manifest_file.write_text(manifest_content)
        
        # Wait for watchdog and delay logic
        await asyncio.sleep(1.0)
        
        on_change_mock.assert_called()
        args, kwargs = on_change_mock.call_args
        assert args[0] in ["TestAgent", "manifest.json"]
        
        pkg = registry.get("TestAgent")
        assert pkg is not None
        assert pkg.manifest.name == "TestAgent"
        
    finally:
        registry.stop_watcher()
        shutil.rmtree(packages_dir, ignore_errors=True)
