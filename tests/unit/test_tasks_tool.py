from __future__ import annotations

import pytest

from core.tools import tasks_tool


class _FakeDoc:
    def __init__(self, doc_id: str, payload: dict):
        self.id = doc_id
        self._payload = payload

    def to_dict(self) -> dict:
        return dict(self._payload)


class _FakeQuery:
    def __init__(self, docs: list[_FakeDoc]):
        self._docs = docs

    def where(self, field: str, op: str, value: str) -> "_FakeQuery":
        if field == "tag" and op == "==":
            return _FakeQuery([doc for doc in self._docs if doc.to_dict().get("tag") == value])
        return _FakeQuery(list(self._docs))

    async def stream(self):
        for doc in self._docs:
            yield doc


class _FakeDB:
    def __init__(self, docs: list[_FakeDoc]):
        self._docs = docs

    def collection(self, name: str) -> _FakeQuery:
        if name != "notes":
            return _FakeQuery([])
        return _FakeQuery(list(self._docs))


class _FakeConnector:
    def __init__(self, db: _FakeDB | None):
        self.is_connected = db is not None
        self._db = db


@pytest.fixture(autouse=True)
def _reset_firebase_connector():
    tasks_tool.set_firebase_connector(None)
    yield
    tasks_tool.set_firebase_connector(None)


@pytest.mark.asyncio
async def test_recall_notes_unavailable_without_firestore() -> None:
    tasks_tool.set_firebase_connector(None)
    result = await tasks_tool.recall_notes(query="handover fallback")
    assert result["status"] == "unavailable"


@pytest.mark.asyncio
async def test_recall_notes_returns_semantic_matches() -> None:
    docs = [
        _FakeDoc(
            "a1",
            {
                "note_id": "a1",
                "content": ("Fallback path validated after handover failure in galaxy alpha."),
                "tag": "research",
                "created_at": "2026-03-07T12:00:00+00:00",
            },
        ),
        _FakeDoc(
            "a2",
            {
                "note_id": "a2",
                "content": "Remember to buy coffee beans.",
                "tag": "general",
                "created_at": "2026-03-07T11:00:00+00:00",
            },
        ),
        _FakeDoc(
            "a3",
            {
                "note_id": "a3",
                "content": "Handover fallback script for notes planet was rehearsed.",
                "tag": "research",
                "created_at": "2026-03-07T13:00:00+00:00",
            },
        ),
    ]
    connector = _FakeConnector(_FakeDB(docs))
    tasks_tool.set_firebase_connector(connector)

    result = await tasks_tool.recall_notes(
        query="handover fallback",
        tag="research",
        limit=3,
    )
    assert result["status"] == "success"
    assert result["count"] == 2
    assert result["notes"][0]["note_id"] == "a3"
    assert result["notes"][1]["note_id"] == "a1"


def test_tasks_tool_registers_recall_notes() -> None:
    tool_names = [tool["name"] for tool in tasks_tool.get_tools()]
    assert "recall_notes" in tool_names
