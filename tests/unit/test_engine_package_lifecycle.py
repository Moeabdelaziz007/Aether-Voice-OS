from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

import sys
import types

# Minimal stubs so core.engine can be imported in test environments
# without Google ADK/GenAI packages installed.
try:
    from google.adk.runners import InMemoryRunner as _InMemoryRunner  # noqa: F401
    from google.genai import types as _genai_types  # noqa: F401
except ModuleNotFoundError:
    google_mod = types.ModuleType("google")
    adk_mod = types.ModuleType("google.adk")
    runners_mod = types.ModuleType("google.adk.runners")
    genai_mod = types.ModuleType("google.genai")
    types_mod = types.ModuleType("google.genai.types")

    class _DummyInMemoryRunner:
        def __init__(self, *args, **kwargs):
            pass

    runners_mod.InMemoryRunner = _DummyInMemoryRunner
    genai_mod.types = types_mod

    sys.modules.setdefault("google", google_mod)
    sys.modules["google.adk"] = adk_mod
    sys.modules["google.adk.runners"] = runners_mod
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.genai.types"] = types_mod

from core.engine import AetherEngine


@pytest.mark.asyncio
async def test_on_package_change_initial_register_tracks_tools(caplog):
    caplog.set_level(logging.INFO)
    engine = AetherEngine.__new__(AetherEngine)
    engine._router = Mock()
    engine._router.names = []
    engine._package_tools = {}

    module = SimpleNamespace()

    def register_module(_module):
        assert _module is module
        engine._router.names = ["alpha", "beta"]

    engine._router.register_module.side_effect = register_module

    package = SimpleNamespace(manifest=SimpleNamespace(tools=["my_module"]))

    with patch("core.engine.importlib.import_module", return_value=module):
        await engine._on_package_change("pkg", package)

    assert engine._package_tools["pkg"] == {"alpha", "beta"}
    assert engine._router.un_register.call_count == 0
    assert any("Package tool added: package=pkg tool=alpha" in r.message for r in caplog.records)
    assert any("Package tool added: package=pkg tool=beta" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_on_package_change_reload_replaces_previous_tools(caplog):
    caplog.set_level(logging.INFO)
    engine = AetherEngine.__new__(AetherEngine)
    engine._router = Mock()
    engine._router.names = ["stale_tool", "keep_outside"]
    engine._package_tools = {"pkg": {"stale_tool"}}

    module = SimpleNamespace()

    def register_module(_module):
        assert _module is module
        engine._router.names = ["fresh_tool", "keep_outside"]

    engine._router.register_module.side_effect = register_module

    package = SimpleNamespace(manifest=SimpleNamespace(tools=["core.tools.fresh"]))

    with patch("core.engine.importlib.import_module", return_value=module):
        await engine._on_package_change("pkg", package)

    engine._router.un_register.assert_called_once_with("stale_tool")
    assert engine._package_tools["pkg"] == {"fresh_tool"}
    assert any("Package tool removed: package=pkg tool=stale_tool" in r.message for r in caplog.records)
    assert any("Package tool added: package=pkg tool=fresh_tool" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_on_package_change_unload_cleans_up_and_clears_bookkeeping(caplog):
    caplog.set_level(logging.INFO)
    engine = AetherEngine.__new__(AetherEngine)
    engine._router = Mock()
    engine._package_tools = {"pkg": {"tool_b", "tool_a"}}

    await engine._on_package_change("pkg", None)

    removed = [call.args[0] for call in engine._router.un_register.call_args_list]
    assert removed == ["tool_a", "tool_b"]
    assert "pkg" not in engine._package_tools
    assert any("Package tool removed: package=pkg tool=tool_a" in r.message for r in caplog.records)
    assert any("Package tool removed: package=pkg tool=tool_b" in r.message for r in caplog.records)
