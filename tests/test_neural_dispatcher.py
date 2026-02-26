"""
Tests for the Neural Dispatcher (ToolRouter) and tool modules.

Validates:
  - ToolRouter registration and dispatch
  - System tool functions (time, system info, timer)
  - Tasks tool functions (create, list, complete, add_note)
  - Module auto-discovery via get_tools()
  - Error handling for unknown tools
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# ─── ToolRouter Tests ────────────────────────────────────────


class TestToolRouter:
    """Tests for core.tools.router.ToolRouter."""

    def _make_router(self):
        from core.tools.router import ToolRouter

        return ToolRouter()

    def test_register_tool(self):
        router = self._make_router()
        router.register(
            name="test_fn",
            description="A test function",
            parameters={},
            handler=lambda: {"ok": True},
        )
        assert router.count == 1
        assert "test_fn" in router.names

    def test_register_module(self):
        from core.tools import system_tool

        router = self._make_router()
        router.register_module(system_tool)
        assert router.count >= 3
        assert "get_current_time" in router.names
        assert "get_system_info" in router.names
        assert "run_timer" in router.names

    def test_register_module_tasks(self):
        from core.tools import tasks_tool

        router = self._make_router()
        router.register_module(tasks_tool)
        assert router.count >= 4
        assert "create_task" in router.names
        assert "list_tasks" in router.names
        assert "complete_task" in router.names
        assert "add_note" in router.names

    def test_get_declarations(self):
        from core.tools import system_tool

        router = self._make_router()
        router.register_module(system_tool)
        declarations = router.get_declarations()
        assert len(declarations) >= 3
        names = [d.name for d in declarations]
        assert "get_current_time" in names

    @pytest.mark.asyncio
    async def test_dispatch_sync_handler(self):
        router = self._make_router()
        router.register(
            name="sync_fn",
            description="Sync test",
            parameters={},
            handler=lambda: "hello",
        )
        fc = MagicMock()
        fc.name = "sync_fn"
        fc.args = {}
        result = await router.dispatch(fc)
        assert result == {"result": "hello"}

    @pytest.mark.asyncio
    async def test_dispatch_async_handler(self):
        async def async_fn():
            return {"status": "ok"}

        router = self._make_router()
        router.register(
            name="async_fn",
            description="Async test",
            parameters={},
            handler=async_fn,
        )
        fc = MagicMock()
        fc.name = "async_fn"
        fc.args = {}
        result = await router.dispatch(fc)
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self):
        router = self._make_router()
        fc = MagicMock()
        fc.name = "nonexistent"
        fc.args = {}
        result = await router.dispatch(fc)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_dispatch_with_args(self):
        async def greet(name: str = "World"):
            return {"greeting": f"Hello, {name}!"}

        router = self._make_router()
        router.register(
            name="greet",
            description="Greet someone",
            parameters={"type": "object", "properties": {"name": {"type": "string"}}},
            handler=greet,
        )
        fc = MagicMock()
        fc.name = "greet"
        fc.args = {"name": "Aether"}
        result = await router.dispatch(fc)
        assert result == {"greeting": "Hello, Aether!"}

    @pytest.mark.asyncio
    async def test_dispatch_handler_error(self):
        async def failing_fn():
            raise ValueError("Something broke")

        router = self._make_router()
        router.register(
            name="fail",
            description="Will fail",
            parameters={},
            handler=failing_fn,
        )
        fc = MagicMock()
        fc.name = "fail"
        fc.args = {}
        result = await router.dispatch(fc)
        assert "error" in result

    def test_register_module_no_get_tools(self):
        """Module without get_tools() should be skipped."""
        router = self._make_router()
        mock_module = MagicMock(spec=[])
        mock_module.__name__ = "fake_module"
        router.register_module(mock_module)
        assert router.count == 0


# ─── System Tool Tests ───────────────────────────────────────


class TestSystemTool:
    """Tests for core.tools.system_tool functions."""

    @pytest.mark.asyncio
    async def test_get_current_time(self):
        from core.tools.system_tool import get_current_time

        result = await get_current_time()
        assert "local_time" in result
        assert "local_date" in result
        assert "utc_time" in result
        assert "unix_timestamp" in result

    @pytest.mark.asyncio
    async def test_get_system_info(self):
        from core.tools.system_tool import get_system_info

        result = await get_system_info()
        assert "os" in result
        assert "python_version" in result
        assert result["os"] in ("Darwin", "Linux", "Windows")

    @pytest.mark.asyncio
    async def test_run_timer(self):
        from core.tools.system_tool import run_timer

        result = await run_timer(minutes=5, label="Test Timer")
        assert result["status"] == "timer_set"
        assert result["duration_minutes"] == 5
        assert result["label"] == "Test Timer"

    def test_get_tools_returns_list(self):
        from core.tools.system_tool import get_tools

        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 3
        for tool in tools:
            assert "name" in tool
            assert "handler" in tool
            assert callable(tool["handler"])


# ─── Tasks Tool Tests ────────────────────────────────────────


class TestTasksTool:
    """Tests for core.tools.tasks_tool functions (without Firebase)."""

    @pytest.mark.asyncio
    async def test_create_task_no_firebase(self):
        """Creating a task without Firebase should still return success."""
        from core.tools.tasks_tool import create_task

        result = await create_task(title="Buy groceries", due="tomorrow")
        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"
        assert "task_id" in result

    @pytest.mark.asyncio
    async def test_list_tasks_no_firebase(self):
        """Listing tasks without Firebase should return unavailable."""
        from core.tools.tasks_tool import list_tasks

        result = await list_tasks()
        assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_complete_task_no_firebase(self):
        """Completing a task without Firebase should return unavailable."""
        from core.tools.tasks_tool import complete_task

        result = await complete_task(task_id="abc123")
        assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_add_note_no_firebase(self):
        """Adding a note without Firebase should still return success."""
        from core.tools.tasks_tool import add_note

        result = await add_note(content="Remember to check the mail", tag="personal")
        assert result["status"] == "saved"
        assert "note_id" in result

    def test_get_tools_returns_list(self):
        from core.tools.tasks_tool import get_tools

        tools = get_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 4
        names = [t["name"] for t in tools]
        assert "create_task" in names
        assert "list_tasks" in names
        assert "complete_task" in names
        assert "add_note" in names


# ─── Integration: Engine + Router ─────────────────────────────


class TestEngineRouterIntegration:
    """Tests that the engine correctly wires the ToolRouter."""

    def test_engine_has_router(self):
        """Engine should create a ToolRouter with tools registered."""
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            from core.engine import AetherEngine

            engine = AetherEngine()
            assert hasattr(engine, "_router")
            assert engine._router.count >= 7  # 3 system + 4 tasks

    def test_engine_router_has_system_tools(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            from core.engine import AetherEngine

            engine = AetherEngine()
            assert "get_current_time" in engine._router.names
            assert "get_system_info" in engine._router.names

    def test_engine_router_has_task_tools(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            from core.engine import AetherEngine

            engine = AetherEngine()
            assert "create_task" in engine._router.names
            assert "list_tasks" in engine._router.names
