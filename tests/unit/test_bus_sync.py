"""
Unit tests for Aether Global State Bus and Synchronization.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from core.transport.bus import GlobalBus
from core.transport.session_state import SessionStateManager, SessionState

@pytest.mark.asyncio
async def test_bus_publish_subscribe():
    """Verify that GlobalBus can publish and receive messages via mock Redis."""
    with patch("redis.asyncio.Redis") as mock_redis:
        mock_instance = mock_redis.return_value
        mock_instance.ping = AsyncMock()
        mock_instance.publish = AsyncMock(return_value=1)
        mock_instance.close = AsyncMock()
        
        # Mock pubsub as an async object
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_instance.pubsub.return_value = mock_pubsub
        
        bus = GlobalBus()
        await bus.connect()
        
        # Test Publish
        await bus.publish("test_channel", {"hello": "world"})
        mock_instance.publish.assert_called_once()
        
        # Test Subscribe (internal callback routing)
        callback_called = asyncio.Event()
        async def test_callback(data):
            assert data["hello"] == "world"
            callback_called.set()
            
        await bus.subscribe("test_channel", test_callback)
        
        # Manually trigger the callback logic (simulating _listen_loop)
        full_channel = f"aether:pubsub:test_channel"
        for cb in bus._subscriptions[full_channel]:
            if asyncio.iscoroutinefunction(cb):
                await cb({"hello": "world"})
            else:
                cb({"hello": "world"})
        
        assert callback_called.is_set()
        
        await bus.disconnect()

@pytest.mark.asyncio
async def test_session_state_global_sync():
    """Verify that SessionStateManager publishes to the bus on transition."""
    mock_bus = AsyncMock(spec=GlobalBus)
    
    manager = SessionStateManager(bus=mock_bus)
    
    # Trigger local transition
    success = await manager.transition_to(SessionState.CONNECTED, reason="Unit test")
    
    assert success is True
    # Verify it published to the bus
    mock_bus.publish.assert_called_once()
    args = mock_bus.publish.call_args[0]
    assert args[0] == "state_change"
    assert args[1]["state"] == "CONNECTED"

@pytest.mark.asyncio
async def test_session_state_remote_update():
    """Verify that SessionStateManager updates local state when bus receives change."""
    mock_bus = AsyncMock(spec=GlobalBus)
    
    # Capture the callback registered by manager
    subscribed_channel = None
    callback = None
    
    async def mock_subscribe(chan, cb):
        nonlocal subscribed_channel, callback
        subscribed_channel = chan
        callback = cb
        
    mock_bus.subscribe.side_effect = mock_subscribe
    
    manager = SessionStateManager(bus=mock_bus)
    # Wait for background task to call subscribe
    await asyncio.sleep(0.1) 
    
    assert subscribed_channel == "state_change"
    assert callback is not None
    
    # Simulate a message from another node
    await callback({"state": "ERROR", "reason": "Remote Failure", "node_id": "node_2"})
    
    # Verify local state updated
    assert manager.state == SessionState.ERROR
