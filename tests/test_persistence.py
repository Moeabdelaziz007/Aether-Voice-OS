"""
Aether Voice OS — Session State Persistence Real Integration Tests.
"""

import asyncio
import pytest
from core.transport.bus import GlobalBus
from core.transport.session_state import SessionStateManager, SessionMetadata, SessionState

@pytest.mark.asyncio
async def test_persistence_real_redis():
    """Verify that SessionStateManager correctly persists to and restores from REAL Redis."""
    bus = GlobalBus(prefix="aether_test_persist:")
    if not await bus.connect():
        pytest.skip("Redis not available")
        
    try:
        # Instance A: Save
        manager_a = SessionStateManager(bus=bus)
        session_id = f"test-real-{asyncio.get_event_loop().time()}"
        metadata = SessionMetadata(session_id=session_id, soul_name="AetherReal")
        
        await manager_a.transition_to(SessionState.CONNECTED, reason="Real Persistence Test", metadata=metadata)
        manager_a.increment_message_count()
        
        # Wait for background persistence (increment_message_count uses a task)
        await asyncio.sleep(0.2)
        
        # Instance B: Restore
        manager_b = SessionStateManager(bus=bus)
        success = await manager_b.restore_from_bus(session_id)
        
        assert success is True
        assert manager_b.metadata.session_id == session_id
        assert manager_b.metadata.message_count == 1
        assert manager_b.metadata.soul_name == "AetherReal"
        
    finally:
        await bus.disconnect()
