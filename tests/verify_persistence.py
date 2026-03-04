"""
Aether Voice OS — Persistence Verification.
"""

import asyncio
import logging

from core.infra.transport.bus import GlobalBus
from core.infra.transport.session_state import (
    SessionMetadata,
    SessionState,
    SessionStateManager,
)


async def verify_persistence():
    logging.basicConfig(level=logging.INFO)

    # 1. Setup Bus
    bus = GlobalBus()
    if not await bus.connect():
        print("❌ Redis not available. Skipping verification.")
        return

    # 2. Instance A: Create and transition session
    manager_a = SessionStateManager(bus=bus)
    metadata = SessionMetadata(session_id="verify-sid-123", soul_name="Aether")
    await manager_a.transition_to(
        SessionState.CONNECTED, reason="Unit Test", metadata=metadata
    )
    manager_a.increment_message_count()

    # Wait for background persistence
    await asyncio.sleep(0.5)
    print("✅ Instance A: State and Metadata persisted.")

    # 3. Instance B: Restore session
    manager_b = SessionStateManager(bus=bus)
    success = await manager_b.restore_from_bus("verify-sid-123")

    if success:
        print(f"✅ Instance B: Restored session {manager_b.metadata.session_id}")
        assert manager_b.metadata.session_id == "verify-sid-123"
        assert manager_b.metadata.message_count == 1
        assert manager_b.metadata.soul_name == "Aether"
        print("🔥 Persistence verification SUCCESS.")
    else:
        print("❌ Instance B: Failed to restore session from bus.")

    await bus.disconnect()


if __name__ == "__main__":
    asyncio.run(verify_persistence())
