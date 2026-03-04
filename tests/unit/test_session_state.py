import pytest
import asyncio
from datetime import datetime
from core.infra.transport.session_state import SessionStateManager, SessionState, SessionMetadata

def test_create_snapshot_with_metadata():
    manager = SessionStateManager()

    # Setup some test state
    metadata = SessionMetadata(
        session_id="test_session_123",
        soul_name="TestSoul",
        message_count=5,
        handoff_count=1,
        error_count=0
    )

    async def run_test():
        # Transition to update internal state and metadata
        await manager.transition_to(SessionState.CONNECTED, metadata=metadata)

        # Create the snapshot
        return await manager.create_snapshot()

    snapshot = asyncio.run(run_test())

    # Verify the snapshot contents
    assert snapshot["state"] == "CONNECTED"
    assert snapshot["consecutive_errors"] == 0
    assert "timestamp" in snapshot

    # Verify metadata serialization
    assert snapshot["metadata"] is not None
    assert snapshot["metadata"]["session_id"] == "test_session_123"
    assert snapshot["metadata"]["soul_name"] == "TestSoul"
    assert snapshot["metadata"]["message_count"] == 5
    assert snapshot["metadata"]["handoff_count"] == 1
    assert snapshot["metadata"]["error_count"] == 0
    assert "started_at" in snapshot["metadata"]
    assert "last_activity" in snapshot["metadata"]

def test_create_snapshot_without_metadata():
    manager = SessionStateManager()

    # Default initial state has no metadata
    assert manager.state == SessionState.INITIALIZING
    assert manager.metadata is None

    async def run_test():
        # Create the snapshot
        return await manager.create_snapshot()

    snapshot = asyncio.run(run_test())

    # Verify the snapshot contents
    assert snapshot["state"] == "INITIALIZING"
    assert snapshot["metadata"] is None
    assert snapshot["consecutive_errors"] == 0
    assert "timestamp" in snapshot

def test_create_snapshot_with_errors():
    manager = SessionStateManager()

    # Setup some test state with errors
    metadata = SessionMetadata(
        session_id="test_session_error",
        soul_name="TestSoul",
    )

    async def run_test():
        await manager.transition_to(SessionState.CONNECTED, metadata=metadata)
        await manager.transition_to(SessionState.ERROR)

        # Create the snapshot
        return await manager.create_snapshot()

    snapshot = asyncio.run(run_test())

    # Verify the snapshot contents
    assert snapshot["state"] == "ERROR"
    assert snapshot["consecutive_errors"] == 1
    assert snapshot["metadata"]["error_count"] == 1
    assert "timestamp" in snapshot
