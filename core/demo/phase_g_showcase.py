from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from core.demo.notes_planet_showcase import run_notes_planet_showcase
from core.tools import voyager_tool

EmitFn = Callable[[str, dict[str, Any]], Awaitable[None]]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_phase_g_demo_script(
    emit: EmitFn,
    galaxy_id: str = "Genesis",
    use_fallback_path: bool = False,
) -> dict[str, Any]:
    notes_result = await run_notes_planet_showcase(emit=emit, galaxy_id=galaxy_id)
    if use_fallback_path:
        fallback_payload: dict[str, Any] = {
            "protocol_version": 1,
            "galaxy_id": galaxy_id,
            "action": "capture_frame",
            "event_kind": "capture",
            "url": "about:fallback",
            "selector": "#fallback-path",
            "text": "",
            "x": 0.5,
            "y": 0.4,
            "latency_ms": 5.0,
            "timestamp": _now_iso(),
        }
        await emit("mirror_frame", fallback_payload)
        await emit(
            "task_timeline_item",
            {
                "protocol_version": 1,
                "task_id": "phase-g-showcase",
                "title": "Mirror fallback path",
                "detail": (
                    "Used deterministic fallback mirror frame for demo continuity."
                ),
                "status": "completed",
                "timestamp": _now_iso(),
            },
        )
        return {
            "status": "ok",
            "mode": "fallback",
            "notes": notes_result,
            "mirror": {"status": "fallback", "payload": fallback_payload},
        }

    mirror_open = await voyager_tool.voyager_browser_control(
        action="open_url",
        url="https://example.com",
        galaxy_id=galaxy_id,
    )
    mirror_type = await voyager_tool.voyager_browser_control(
        action="type",
        selector="#search",
        text="Aether Voyager Mirror",
        galaxy_id=galaxy_id,
    )
    mirror_click = await voyager_tool.voyager_browser_control(
        action="click",
        selector="#run",
        x=0.62,
        y=0.51,
        galaxy_id=galaxy_id,
    )
    return {
        "status": "ok",
        "mode": "live",
        "notes": notes_result,
        "mirror": {
            "open": mirror_open,
            "type": mirror_type,
            "click": mirror_click,
        },
    }


async def _console_emit(event_type: str, payload: dict[str, Any]) -> None:
    print(f"[{event_type}] {payload}")


def main() -> None:
    result = asyncio.run(run_phase_g_demo_script(emit=_console_emit))
    print(result)


if __name__ == "__main__":
    main()
