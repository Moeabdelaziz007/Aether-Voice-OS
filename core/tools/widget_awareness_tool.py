from __future__ import annotations

import logging
from typing import Any

from core.infra.transport.bus import GlobalBus

logger = logging.getLogger(__name__)


async def get_active_widgets(**kwargs: Any) -> dict[str, Any]:
    """
    Retrieves the list of active widgets currently displayed in the Aether Dashboard.
    This provides 'Neural Workspace Awareness' to the AI.
    """
    bus = GlobalBus()  # Uses default connection params
    connected = await bus.connect()

    if not connected:
        return {
            "status": "error",
            "message": "Global Bus connection failed. Cannot retrieve workspace state.",
            "active_widgets": [],
        }

    try:
        # Get the active session ID first
        active_session_id = await bus.get_state("active_session_id")
        if not active_session_id:
            return {
                "status": "ok",
                "message": "No active session found in state bus.",
                "active_widgets": [],
            }

        # Get the session metadata
        session_state = await bus.get_state(f"session:{active_session_id}")
        if not session_state or "metadata" not in session_state:
            return {
                "status": "ok",
                "message": "Session state found but metadata is missing.",
                "active_widgets": [],
            }

        widgets = session_state["metadata"].get("active_widgets", [])

        return {
            "status": "ok",
            "active_widgets": widgets,
            "session_id": active_session_id,
            "timestamp": session_state["metadata"].get("last_activity"),
        }
    finally:
        await bus.disconnect()


def get_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_active_widgets",
            "description": "Get the list of active UI widgets/tools currently visible on the user's "
                           "dashboard. Use this to understand the visual context of the workspace.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "handler": get_active_widgets,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        }
    ]
