from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from core.tools import tasks_tool, workspace_tool

EmitFn = Callable[[str, dict[str, Any]], Awaitable[None]]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_notes_planet_showcase(
    emit: EmitFn,
    galaxy_id: str = "Genesis",
    query: str = "fallback path",
) -> dict[str, Any]:
    workspace_tool.reset_workspace_state()
    workspace_tool.set_workspace_event_emitter(emit)

    await emit(
        "task_pulse",
        {
            "protocol_version": 1,
            "task_id": "showcase-notes-planet",
            "phase": "EXECUTING",
            "action": "notes_planet_showcase_start",
            "vibe": "focused",
            "thought": "Initializing Notes Planet showcase flow.",
            "intensity": 0.7,
            "timestamp": _now_iso(),
        },
    )

    await workspace_tool.materialize_app(
        app_id="planet-notes",
        app_type="notes",
        x=130,
        y=10,
        galaxy_id=galaxy_id,
    )
    await workspace_tool.focus_app(app_id="planet-notes", galaxy_id=galaxy_id)
    await tasks_tool.add_note(
        content="Fallback path validated for Notes Planet showcase.",
        tag="showcase",
    )
    await tasks_tool.add_note(
        content=(
            "Mission timeline highlight: semantic recall can recover intent context."
        ),
        tag="showcase",
    )

    recall = await tasks_tool.recall_notes(query=query, tag="showcase", limit=3)
    used_fallback = recall.get("status") != "success"
    fallback_payload: dict[str, Any] | None = None
    if used_fallback:
        fallback_payload = {
            "status": "fallback",
            "notes": [
                {
                    "content": "Fallback path validated for Notes Planet showcase.",
                    "tag": "showcase",
                    "score": 0.2,
                }
            ],
            "message": "Recall unavailable; injected deterministic fallback result.",
        }

    final_recall = fallback_payload if fallback_payload else recall

    await emit(
        "task_timeline_item",
        {
            "protocol_version": 1,
            "task_id": "showcase-notes-planet",
            "title": "Notes Planet Recall",
            "detail": (
                "Semantic recall completed."
                if not used_fallback
                else "Semantic recall unavailable; fallback response injected."
            ),
            "status": "completed" if not used_fallback else "in-progress",
            "timestamp": _now_iso(),
        },
    )

    await emit(
        "task_pulse",
        {
            "protocol_version": 1,
            "task_id": "showcase-notes-planet",
            "phase": "COMPLETED",
            "action": "notes_planet_showcase_complete",
            "vibe": "success",
            "thought": "Notes Planet showcase flow completed.",
            "intensity": 0.86,
            "timestamp": _now_iso(),
        },
    )

    workspace_state = await workspace_tool.list_workspace_apps(galaxy_id=galaxy_id)
    return {
        "status": "ok",
        "galaxy_id": galaxy_id,
        "workspace": workspace_state,
        "recall": final_recall,
        "used_fallback": used_fallback,
    }


async def _console_emit(event_type: str, payload: dict[str, Any]) -> None:
    print(f"[{event_type}] {payload}")


def main() -> None:
    result = asyncio.run(run_notes_planet_showcase(emit=_console_emit))
    print(result)


if __name__ == "__main__":
    main()
