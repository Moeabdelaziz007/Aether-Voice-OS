from __future__ import annotations

import asyncio
from typing import Any

from core.tools import workspace_tool


def test_workspace_tool_materialize_focus_move_collapse() -> None:
    async def _run() -> None:
        events: list[tuple[str, dict[str, Any]]] = []

        async def _emit(event_type: str, payload: dict[str, Any]) -> None:
            events.append((event_type, payload))

        workspace_tool.reset_workspace_state()
        workspace_tool.set_workspace_event_emitter(_emit)

        materialized = await workspace_tool.materialize_app(
            app_id="notes-1",
            app_type="notes",
            x=10.0,
            y=20.0,
            galaxy_id="gal-alpha",
        )
        assert materialized["status"] == "ok"
        assert materialized["app"]["position"] == {"x": 10.0, "y": 20.0}

        focused = await workspace_tool.focus_app(
            app_id="notes-1",
            galaxy_id="gal-alpha",
        )
        assert focused["status"] == "ok"
        assert focused["focused_app_id"] == "notes-1"

        moved = await workspace_tool.move_app(
            app_id="notes-1",
            x=50.0,
            y=80.0,
            galaxy_id="gal-alpha",
        )
        assert moved["status"] == "ok"
        assert moved["app"]["position"] == {"x": 50.0, "y": 80.0}

        collapsed = await workspace_tool.collapse_app(
            app_id="notes-1",
            galaxy_id="gal-alpha",
        )
        assert collapsed["status"] == "ok"
        assert collapsed["app"]["is_collapsed"] is True

        listed = await workspace_tool.list_workspace_apps(galaxy_id="gal-alpha")
        assert listed["status"] == "ok"
        assert listed["count"] == 1
        assert listed["focused_app_id"] == "notes-1"

        event_types = [event_type for event_type, _ in events]
        assert event_types == [
            "workspace_state",
            "workspace_state",
            "workspace_state",
            "workspace_state",
        ]
        for _, payload in events:
            assert payload["protocol_version"] == 1
            assert payload["workspace_galaxy"] == "gal-alpha"

    asyncio.run(_run())


def test_workspace_tool_rejects_unknown_app() -> None:
    async def _run() -> None:
        workspace_tool.reset_workspace_state()
        workspace_tool.set_workspace_event_emitter(None)
        focused = await workspace_tool.focus_app("missing-app")
        moved = await workspace_tool.move_app("missing-app", 1.0, 2.0)
        collapsed = await workspace_tool.collapse_app("missing-app")
        assert focused["status"] == "error"
        assert moved["status"] == "error"
        assert collapsed["status"] == "error"

    asyncio.run(_run())
