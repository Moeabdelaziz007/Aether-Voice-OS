"""
Aether Voice OS — Global State Bus Real Integration Tests.
"""

import asyncio

import pytest

from core.infra.transport.bus import GlobalBus
from core.infra.transport.session_state import SessionState, SessionStateManager


@pytest.mark.asyncio
async def test_bus_publish_subscribe_real():
    """Verify that GlobalBus can publish and receive messages via REAL Redis."""
    bus = GlobalBus()
    if not await bus.connect():
        pytest.skip("Redis not available for real tests")

    try:
        callback_called = asyncio.Event()
        received_data = None

        async def test_callback(data):
            nonlocal received_data
            received_data = data
            callback_called.set()

        await bus.subscribe("real_test_channel", test_callback)

        # Small sleep to ensure subscription is active in Redis
        await asyncio.sleep(0.1)

        test_payload = {"hello": "real_world", "timestamp": "now"}
        await bus.publish("real_test_channel", test_payload)

        await asyncio.wait_for(callback_called.wait(), timeout=2.0)
        assert received_data == test_payload

    finally:
        await bus.disconnect()


@pytest.mark.asyncio
async def test_session_state_global_sync_real():
    """Verify that SessionStateManager correctly syncs state across instances via real Redis."""
    bus_a = GlobalBus(prefix="aether_test:")
    bus_b = GlobalBus(prefix="aether_test:")

    if not await bus_a.connect() or not await bus_b.connect():
        pytest.skip("Redis not available")

    try:
        manager_a = SessionStateManager(bus=bus_a)
        manager_b = SessionStateManager(bus=bus_b)

        # Wait for subscriptions to settle
        await asyncio.sleep(0.2)

        # Transition A -> Updates B?
        await manager_a.transition_to(SessionState.CONNECTED, reason="Sync Test")

        # Wait for propagation
        reached = await manager_b.wait_for_state([SessionState.CONNECTED], timeout=2.0)
        assert reached is True
        assert manager_b.state == SessionState.CONNECTED

    finally:
        await bus_a.disconnect()
        await bus_b.disconnect()
