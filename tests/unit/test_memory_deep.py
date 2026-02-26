from unittest.mock import AsyncMock, MagicMock

import pytest

from core.tools import memory_tool


# Mock the Firebase connector for tool testing
class MockFirebase:
    def __init__(self):
        self.is_connected = True
        self._db = MagicMock()
        self._session_id = "test-session"


@pytest.fixture
def mock_firebase():
    mock = MockFirebase()
    memory_tool.set_firebase_connector(mock)
    return mock


@pytest.mark.asyncio
async def test_priority_memory_logic(mock_firebase):
    """Verify that priorities and tags are correctly handled in memory storage."""
    # We mock the collection and document calls
    doc_mock = MagicMock()
    doc_mock.set = AsyncMock()
    mock_firebase._db.collection.return_value.document.return_value = doc_mock

    # 1. Test Saving with high priority and tags
    result = await memory_tool.save_memory(
        key="master_key",
        value="forbidden_knowledge",
        priority="high",
        tags=["vault", "secrets"],
    )

    assert result["status"] == "saved"
    assert result["priority"] == "high"

    # Verify the dictionary sent to Firestore
    call_args = doc_mock.set.call_args[0][0]
    assert call_args["priority"] == "high"
    assert "vault" in call_args["tags"]


@pytest.mark.asyncio
async def test_prune_logic(mock_firebase):
    """Verify that pruning hits the correct priority collection."""
    # Mock the stream of documents
    query_mock = mock_firebase._db.collection.return_value.where.return_value

    doc1 = MagicMock()
    doc1.reference.delete = AsyncMock()

    # Mocking async iterator for Firestore stream
    async def mock_stream():
        yield doc1

    query_mock.stream.return_value = mock_stream()

    result = await memory_tool.prune_memories(priority="low")

    assert result["status"] == "pruned"
    assert result["count"] == 1
    doc1.reference.delete.assert_called_once()

    # Ensure query filtered by 'low'
    mock_firebase._db.collection.return_value.where.assert_called_with(
        "priority", "==", "low"
    )


@pytest.mark.asyncio
async def test_semantic_search_mock(mock_firebase):
    """Verify tag-based search hits Firestore array_contains_any."""
    query_mock = (
        mock_firebase._db.collection.return_value.where.return_value.limit.return_value
    )

    async def empty_stream():
        if False:
            yield None

    query_mock.stream.return_value = empty_stream()

    await memory_tool.semantic_search(tags=["home", "iot"])

    # Verify Firestore query structure
    mock_firebase._db.collection.return_value.where.assert_called_with(
        "tags", "array_contains_any", ["home", "iot"]
    )
