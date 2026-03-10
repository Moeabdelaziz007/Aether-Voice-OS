from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

_workspace_event_emitter: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None
_workspace_apps: dict[str, dict[str, Any]] = {}
_focused_app_id: str | None = None


def reset_workspace_state() -> None:
    global _focused_app_id
    _workspace_apps.clear()
    _focused_app_id = None


def set_workspace_event_emitter(
    emitter: Callable[[str, dict[str, Any]], Awaitable[None]] | None,
) -> None:
    global _workspace_event_emitter
    _workspace_event_emitter = emitter


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _emit_workspace_state(action: str, app_id: str, galaxy_id: str) -> None:
    if not _workspace_event_emitter:
        return
    await _workspace_event_emitter(
        "workspace_state",
        {
            "protocol_version": 1,
            "workspace_galaxy": galaxy_id,
            "action": action,
            "app_id": app_id,
            "focused_app_id": _focused_app_id,
            "timestamp": _now_iso(),
        },
    )


async def materialize_app(
    app_id: str,
    app_type: str = "utility",
    x: float = 0.0,
    y: float = 0.0,
    galaxy_id: str = "Genesis",
    **kwargs: Any,
) -> dict[str, Any]:
    if not app_id.strip():
        return {"status": "error", "message": "app_id_required"}

    _workspace_apps[app_id] = {
        "app_id": app_id,
        "app_type": app_type,
        "position": {"x": float(x), "y": float(y)},
        "is_materialized": True,
        "is_collapsed": False,
        "updated_at": _now_iso(),
    }
    await _emit_workspace_state("materialize_app", app_id, galaxy_id)
    return {"status": "ok", "action": "materialize_app", "app": _workspace_apps[app_id]}


async def focus_app(
    app_id: str,
    galaxy_id: str = "Genesis",
    **kwargs: Any,
) -> dict[str, Any]:
    global _focused_app_id

    app = _workspace_apps.get(app_id)
    if not app:
        return {"status": "error", "message": f"app_not_found: {app_id}"}
    _focused_app_id = app_id
    app["updated_at"] = _now_iso()
    await _emit_workspace_state("focus_app", app_id, galaxy_id)
    return {"status": "ok", "action": "focus_app", "focused_app_id": _focused_app_id}


async def move_app(
    app_id: str,
    x: float,
    y: float,
    galaxy_id: str = "Genesis",
    **kwargs: Any,
) -> dict[str, Any]:
    app = _workspace_apps.get(app_id)
    if not app:
        return {"status": "error", "message": f"app_not_found: {app_id}"}
    app["position"] = {"x": float(x), "y": float(y)}
    app["updated_at"] = _now_iso()
    await _emit_workspace_state("move_app", app_id, galaxy_id)
    return {"status": "ok", "action": "move_app", "app": app}


async def collapse_app(
    app_id: str,
    galaxy_id: str = "Genesis",
    **kwargs: Any,
) -> dict[str, Any]:
    app = _workspace_apps.get(app_id)
    if not app:
        return {"status": "error", "message": f"app_not_found: {app_id}"}
    app["is_collapsed"] = True
    app["updated_at"] = _now_iso()
    await _emit_workspace_state("collapse_app", app_id, galaxy_id)
    return {"status": "ok", "action": "collapse_app", "app": app}


async def list_workspace_apps(galaxy_id: str = "Genesis", **kwargs: Any) -> dict[str, Any]:
    return {
        "status": "ok",
        "galaxy_id": galaxy_id,
        "focused_app_id": _focused_app_id,
        "count": len(_workspace_apps),
        "apps": list(_workspace_apps.values()),
    }


def get_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "materialize_app",
            "description": "Materialize an app into the active workspace galaxy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {"type": "string"},
                    "app_type": {"type": "string"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "galaxy_id": {"type": "string"},
                },
                "required": ["app_id"],
            },
            "handler": materialize_app,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "focus_app",
            "description": "Focus an existing workspace app by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {"type": "string"},
                    "galaxy_id": {"type": "string"},
                },
                "required": ["app_id"],
            },
            "handler": focus_app,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "move_app",
            "description": "Move an existing app to a new orbital position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {"type": "string"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "galaxy_id": {"type": "string"},
                },
                "required": ["app_id", "x", "y"],
            },
            "handler": move_app,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "collapse_app",
            "description": "Collapse an app panel in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {"type": "string"},
                    "galaxy_id": {"type": "string"},
                },
                "required": ["app_id"],
            },
            "handler": collapse_app,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "list_workspace_apps",
            "description": "List all materialized apps in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "galaxy_id": {"type": "string"},
                },
            },
            "handler": list_workspace_apps,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        },
    ]
