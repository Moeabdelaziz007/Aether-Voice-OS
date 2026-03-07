from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

_mirror_event_emitter: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None
_voyager_state: dict[str, Any] = {
    "current_url": "",
    "last_selector": "",
    "last_action": "",
    "interaction_count": 0,
    "updated_at": "",
}

_ACTION_TO_EVENT = {
    "open_url": "navigation",
    "click": "click",
    "type": "typing",
    "scroll": "scroll",
    "capture_frame": "capture",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_mirror_event_emitter(
    emitter: Callable[[str, dict[str, Any]], Awaitable[None]] | None,
) -> None:
    global _mirror_event_emitter
    _mirror_event_emitter = emitter


def _normalize_action(action: str) -> str:
    normalized = (action or "").strip().lower()
    return normalized if normalized in _ACTION_TO_EVENT else ""


async def voyager_browser_control(
    action: str,
    url: str = "",
    selector: str = "",
    text: str = "",
    x: float | None = None,
    y: float | None = None,
    galaxy_id: str = "Genesis",
    **kwargs: Any,
) -> dict[str, Any]:
    normalized_action = _normalize_action(action)
    if not normalized_action:
        return {"status": "error", "message": "unsupported_action"}
    if normalized_action == "open_url" and not url.strip():
        return {"status": "error", "message": "url_required"}
    if normalized_action in {"click", "type"} and not selector.strip():
        return {"status": "error", "message": "selector_required"}
    if normalized_action == "type" and not text:
        return {"status": "error", "message": "text_required"}

    started = time.perf_counter()
    await time_wait_for_action(normalized_action)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    if normalized_action == "open_url":
        _voyager_state["current_url"] = url
    if selector:
        _voyager_state["last_selector"] = selector
    _voyager_state["last_action"] = normalized_action
    _voyager_state["interaction_count"] = int(_voyager_state["interaction_count"]) + 1
    _voyager_state["updated_at"] = _now_iso()

    payload: dict[str, Any] = {
        "protocol_version": 1,
        "galaxy_id": galaxy_id,
        "action": normalized_action,
        "event_kind": _ACTION_TO_EVENT[normalized_action],
        "url": _voyager_state["current_url"],
        "selector": selector or _voyager_state["last_selector"],
        "text": text if normalized_action == "type" else "",
        "x": x,
        "y": y,
        "latency_ms": latency_ms,
        "timestamp": _now_iso(),
    }
    if _mirror_event_emitter:
        await _mirror_event_emitter("mirror_frame", payload)

    return {
        "status": "ok",
        "action": normalized_action,
        "latency_ms": latency_ms,
        "voyager_state": dict(_voyager_state),
        "mirror_frame": payload,
    }


async def time_wait_for_action(action: str) -> None:
    if action == "capture_frame":
        await asyncio.sleep(0.02)
        return
    if action in {"click", "type"}:
        await asyncio.sleep(0.03)
        return
    await asyncio.sleep(0.01)


async def voyager_get_state(**kwargs: Any) -> dict[str, Any]:
    return {"status": "ok", "voyager_state": dict(_voyager_state)}


def get_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "voyager_browser_control",
            "description": (
                "Browser control wrapper for Voyager actions. "
                "Actions: open_url, click, type, scroll, capture_frame."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "open_url",
                            "click",
                            "type",
                            "scroll",
                            "capture_frame",
                        ],
                    },
                    "url": {"type": "string"},
                    "selector": {"type": "string"},
                    "text": {"type": "string"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "galaxy_id": {"type": "string"},
                },
                "required": ["action"],
            },
            "handler": voyager_browser_control,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "voyager_get_state",
            "description": "Get latest Voyager browser wrapper state.",
            "parameters": {"type": "object", "properties": {}},
            "handler": voyager_get_state,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        },
    ]
