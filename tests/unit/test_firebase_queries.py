from datetime import datetime

import pytest

from core.infra.cloud.firebase import queries as queries_module
from core.infra.cloud.firebase.queries import Queries, _recent_sessions_cache


class _DummyDoc:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    def to_dict(self):
        return self._data


class _DummyQuery:
    def __init__(self, docs):
        self._docs = docs

    def where(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def get(self):
        return self._docs


class _DummyDB:
    def __init__(self, docs):
        self._docs = docs

    def collection(self, _name):
        return _DummyQuery(self._docs)


class _FirestoreStub:
    class Query:
        DESCENDING = "DESC"

    def __init__(self, docs):
        self._docs = docs

    def client(self):
        return _DummyDB(self._docs)


@pytest.mark.asyncio
async def test_get_recent_sessions_returns_empty_for_no_docs(monkeypatch):
    _recent_sessions_cache.clear()
    monkeypatch.setattr(queries_module, "firestore", _FirestoreStub([]))

    queries = Queries()
    result = await queries.get_recent_sessions("user-1", limit=3)

    assert result == []
    assert "user-1_3" in _recent_sessions_cache


@pytest.mark.asyncio
async def test_get_recent_sessions_parses_valid_docs_with_missing_optional_fields(
    monkeypatch,
):
    _recent_sessions_cache.clear()
    docs = [
        _DummyDoc(
            "sess-1",
            {
                "user_id": "user-1",
                "start_time": datetime(2024, 1, 1),
            },
        )
    ]
    monkeypatch.setattr(queries_module, "firestore", _FirestoreStub(docs))

    queries = Queries()
    result = await queries.get_recent_sessions("user-1", limit=1)

    assert len(result) == 1
    assert result[0].session_id == "sess-1"
    assert result[0].user_id == "user-1"
    assert result[0].emotion_events == []
    assert result[0].code_insights == []
