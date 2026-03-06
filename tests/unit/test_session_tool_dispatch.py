from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.ai.session.tool_dispatch import handle_tool_call


class _Router:
    async def dispatch(self, fc):
        return {"result": f"ok-{fc.name}"}


@pytest.mark.asyncio
async def test_tool_dispatch_sends_response():
    gateway = SimpleNamespace(broadcast=AsyncMock(), metrics={})
    facade = SimpleNamespace(
        _tool_router=_Router(),
        _scheduler=None,
        _gateway=gateway,
        _on_tool_call=None,
        _active_handoffs={},
    )
    session = SimpleNamespace(send_tool_response=AsyncMock(), send_realtime_input=AsyncMock())
    tool_call = SimpleNamespace(function_calls=[SimpleNamespace(name="tool_a", args={})])

    await handle_tool_call(facade, session, tool_call)

    session.send_tool_response.assert_awaited_once()
