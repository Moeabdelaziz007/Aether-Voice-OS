from __future__ import annotations

import asyncio
from typing import Any

from core.tools import voyager_tool


def test_voyager_browser_control_emits_mirror_frame() -> None:
    async def _run() -> None:
        events: list[tuple[str, dict[str, Any]]] = []

        async def _emit(event_type: str, payload: dict[str, Any]) -> None:
            events.append((event_type, payload))

        voyager_tool.set_mirror_event_emitter(_emit)
        result = await voyager_tool.voyager_browser_control(
            action="open_url",
            url="https://example.com",
            galaxy_id="gal-voyager",
        )
        assert result["status"] == "ok"
        assert result["mirror_frame"]["event_kind"] == "navigation"
        assert result["mirror_frame"]["protocol_version"] == 1
        assert events and events[0][0] == "mirror_frame"

    asyncio.run(_run())


def test_voyager_browser_control_rejects_invalid_action() -> None:
    async def _run() -> None:
        result = await voyager_tool.voyager_browser_control(action="unknown")
        assert result["status"] == "error"
        assert result["message"] == "unsupported_action"

    asyncio.run(_run())
