"""
Aether Voice OS — SRE Watchdog Real Integration Tests.
"""

import asyncio
import logging
import pytest
from core.infra.transport.bus import GlobalBus
from core.ai.monitoring.watchdog import SREWatchdog

@pytest.mark.asyncio
async def test_watchdog_real_healing():
    """Verify SREWatchdog triggers healing via real GlobalBus."""
    bus = GlobalBus(prefix="aether_test_watchdog:")
    if not await bus.connect():
        pytest.skip("Redis not available")
        
    try:
        heal_event = asyncio.Event()
        
        async def real_heal_action():
            heal_event.set()

        watchdog = SREWatchdog(node_id="real-node", bus=bus)
        # Register real action for pattern
        watchdog._healing_registry["CRITICAL_ERROR"] = real_heal_action
        watchdog.start()
        
        # Trigger real log event
        test_logger = logging.getLogger("AetherCoreEngine")
        test_logger.propagate = False
        test_logger.addHandler(watchdog._log_handler)
        
        test_logger.error("SYSTEM CRITICAL_ERROR DETECTED")
        
        await asyncio.wait_for(heal_event.wait(), timeout=3.0)
        assert heal_event.is_set(), "Healing action failed to trigger on real event"
        
    finally:
        watchdog.stop()
        await bus.disconnect()
