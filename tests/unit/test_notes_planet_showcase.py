from __future__ import annotations

import asyncio
from typing import Any, Callable, cast

from core.demo.notes_planet_showcase import run_notes_planet_showcase
from core.tools import tasks_tool


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
        stored = dict(payload)
        stored.setdefault("note_id", self._note_id)
        self._bucket.append(stored)


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
    def __init__(self):
        self._notes: list[dict[str, Any]] = []

    def collection(self, name: str):
        if name == "notes":
            return _FakeCollection(self._notes)
        return _FakeCollection([])


class _FakeConnector:
    def __init__(self, db: _FakeDB):
        self.is_connected = True
        self._db = db


def _set_connector(connector: Any) -> None:
    setter = cast(Callable[[Any], None], getattr(tasks_tool, "set_firebase_connector"))
    setter(connector)


def test_notes_planet_showcase_success_path() -> None:
    async def _run() -> None:
        emitted: list[tuple[str, dict[str, Any]]] = []

        async def _emit(event_type: str, payload: dict[str, Any]) -> None:
            emitted.append((event_type, payload))

        _set_connector(_FakeConnector(_FakeDB()))
        result = await run_notes_planet_showcase(
            emit=_emit,
            query="fallback path",
        )
        assert result["status"] == "ok"
        assert result["used_fallback"] is False
        assert result["recall"]["status"] == "success"
        assert result["workspace"]["focused_app_id"] == "planet-notes"
        event_types = [event_type for event_type, _ in emitted]
        assert "workspace_state" in event_types
        assert "task_pulse" in event_types
        assert "task_timeline_item" in event_types

    asyncio.run(_run())


def test_notes_planet_showcase_fallback_path() -> None:
    async def _run() -> None:
        emitted: list[tuple[str, dict[str, Any]]] = []

        async def _emit(event_type: str, payload: dict[str, Any]) -> None:
            emitted.append((event_type, payload))

        _set_connector(None)
        result = await run_notes_planet_showcase(
            emit=_emit,
            query="fallback path",
        )
        assert result["status"] == "ok"
        assert result["used_fallback"] is True
        assert result["recall"]["status"] == "fallback"
        assert result["workspace"]["count"] == 1

    asyncio.run(_run())
