from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from core.engine import AetherEngine


class _GatewayRecorder:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    async def broadcast(self, msg_type: str, payload: dict[str, Any]) -> None:
        self.events.append((msg_type, payload))


def test_handover_emits_cinematic_events() -> None:
    async def _run() -> None:
        engine = object.__new__(AetherEngine)
        gateway = _GatewayRecorder()
        setattr(engine, "_gateway", gateway)

        tasks: list[asyncio.Task[Any]] = []

        def _run_background_task(
            coro: Coroutine[Any, Any, Any], name: str | None = None
        ) -> asyncio.Task[Any]:
            task = asyncio.create_task(coro, name=name)
            tasks.append(task)
            return task

        setattr(engine, "_run_background_task", _run_background_task)
        handover_fn = getattr(engine, "_on_agent_handover")
        handover_fn("Architect", "Debugger", "Validate architecture")
        await asyncio.gather(*tasks)

        event_types = [event_type for event_type, _ in gateway.events]
        assert "neural_event" in event_types
        assert "workspace_state" in event_types
        assert "avatar_state" in event_types
        assert "task_pulse" in event_types
        assert "task_timeline_item" in event_types

        by_type = {event_type: payload for event_type, payload in gateway.events}
        assert by_type["task_pulse"]["phase"] == "COMPLETED"
        assert by_type["task_pulse"]["protocol_version"] == 1
        assert by_type["workspace_state"]["protocol_version"] == 1
        assert by_type["avatar_state"]["protocol_version"] == 1
        assert by_type["task_timeline_item"]["protocol_version"] == 1

    asyncio.run(_run())


def test_handover_without_gateway_does_not_crash() -> None:
    engine = object.__new__(AetherEngine)
    setattr(engine, "_gateway", None)
    def _run_background_task(
        coro: Coroutine[Any, Any, Any], name: str | None = None
    ) -> asyncio.Task[Any]:
        return asyncio.create_task(coro, name=name)

    setattr(engine, "_run_background_task", _run_background_task)
    handover_fn = getattr(engine, "_on_agent_handover")
    handover_fn("Architect", "Debugger", "No-op")
