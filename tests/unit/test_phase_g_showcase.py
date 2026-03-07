from __future__ import annotations

import asyncio
from typing import Any

from core.demo.phase_g_showcase import run_phase_g_demo_script
from core.tools import tasks_tool, voyager_tool


class _FakeDoc:
    def __init__(self, payload: dict[str, Any]):
        self.id = str(payload.get("note_id", "doc"))
        self._payload = payload

    def to_dict(self) -> dict[str, Any]:
        return dict(self._payload)


class _FakeQuery:
    def __init__(self, docs: list[_FakeDoc]):
        self._docs = docs

    def where(self, field: str, op: str, value: str) -> "_FakeQuery":
        if field == "tag" and op == "==":
            return _FakeQuery(
                [doc for doc in self._docs if doc.to_dict().get("tag") == value]
            )
        return _FakeQuery(list(self._docs))

    async def stream(self):
        for doc in self._docs:
            yield doc


class _FakeDocRef:
    def __init__(self, bucket: list[dict[str, Any]], note_id: str):
        self._bucket = bucket
        self._note_id = note_id

    async def set(self, payload: dict[str, Any]) -> None:
        data = dict(payload)
        data.setdefault("note_id", self._note_id)
        self._bucket.append(data)


class _FakeCollection:
    def __init__(self, bucket: list[dict[str, Any]]):
        self._bucket = bucket

    def document(self, note_id: str) -> _FakeDocRef:
        return _FakeDocRef(self._bucket, note_id)

    def where(self, field: str, op: str, value: str) -> _FakeQuery:
        if field == "tag" and op == "==":
            return _FakeQuery(
                [_FakeDoc(note) for note in self._bucket if note.get("tag") == value]
            )
        return _FakeQuery([_FakeDoc(note) for note in self._bucket])

    async def stream(self):
        for note in self._bucket:
            yield _FakeDoc(note)


class _FakeDB:
    def __init__(self) -> None:
        self._notes: list[dict[str, Any]] = []

    def collection(self, name: str):
        if name == "notes":
            return _FakeCollection(self._notes)
        return _FakeCollection([])


class _FakeConnector:
    def __init__(self, db: _FakeDB):
        self.is_connected = True
        self._db = db


def test_phase_g_showcase_live_and_fallback_paths() -> None:
    async def _run() -> None:
        events: list[tuple[str, dict[str, Any]]] = []

        async def _emit(event_type: str, payload: dict[str, Any]) -> None:
            events.append((event_type, payload))

        tasks_tool.set_firebase_connector(_FakeConnector(_FakeDB()))
        voyager_tool.set_mirror_event_emitter(_emit)

        live = await run_phase_g_demo_script(emit=_emit, use_fallback_path=False)
        assert live["status"] == "ok"
        assert live["mode"] == "live"

        fallback = await run_phase_g_demo_script(emit=_emit, use_fallback_path=True)
        assert fallback["status"] == "ok"
        assert fallback["mode"] == "fallback"

        event_types = [event_type for event_type, _ in events]
        assert "mirror_frame" in event_types
        assert "task_timeline_item" in event_types

    asyncio.run(_run())
