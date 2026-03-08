"""
Aether Voice OS — Unit Tests for Session State Manager.
"""

from datetime import datetime

import pytest

from core.infra.transport.session_state import (
    SessionMetadata,
    SessionState,
    SessionStateManager,
)


@pytest.mark.asyncio
async def test_create_snapshot_without_metadata():
    """Verify create_snapshot returns expected default structure without metadata."""
    manager = SessionStateManager()

    snapshot = await manager.create_snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot["state"] == SessionState.INITIALIZING.name
    assert snapshot["metadata"] is None
    assert snapshot["consecutive_errors"] == 0

    # Verify timestamp is a valid ISO format string
    assert "timestamp" in snapshot
    try:
        datetime.fromisoformat(snapshot["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not a valid ISO format string")


@pytest.mark.asyncio
async def test_create_snapshot_with_metadata():
    """Verify create_snapshot serializes metadata correctly when present."""
    manager = SessionStateManager()

    metadata = SessionMetadata(
        session_id="test-123",
        soul_name="test-soul",
        message_count=5,
        handoff_count=1,
        error_count=2,
        active_widgets=["widget1", "widget2"]
    )

    # Transition to a non-initial state and set metadata
    success = await manager.transition_to(SessionState.CONNECTED, "Test connection", metadata)
    assert success is True

    # Simulate some errors
    await manager.transition_to(SessionState.ERROR, "Simulated error")

    snapshot = await manager.create_snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot["state"] == SessionState.ERROR.name

    # Verify metadata serialization
    assert isinstance(snapshot["metadata"], dict)
    assert snapshot["metadata"]["session_id"] == "test-123"
    assert snapshot["metadata"]["soul_name"] == "test-soul"
    assert snapshot["metadata"]["message_count"] == 5
    assert snapshot["metadata"]["handoff_count"] == 1
    # Note: Transitioning to ERROR increments the metadata error_count as well
    assert snapshot["metadata"]["error_count"] == 3
    assert snapshot["metadata"]["active_widgets"] == ["widget1", "widget2"]

    # Error count inside manager vs metadata
    assert snapshot["consecutive_errors"] == 1

    # Verify timestamp is a valid ISO format string
    assert "timestamp" in snapshot
    try:
        datetime.fromisoformat(snapshot["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not a valid ISO format string")
