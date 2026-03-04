"""
Aether Voice OS — SRE Watchdog Real Integration Tests.
"""

import asyncio
import logging

import pytest

from core.infra.transport.bus import GlobalBus
from core.services.watchdog import SREWatchdog
import sys
from unittest.mock import MagicMock, AsyncMock, patch
sys.modules['mss'] = MagicMock()
sys.modules['mss.tools'] = MagicMock()
import core.tools.healing_tool


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


@pytest.mark.asyncio
@patch("core.services.watchdog.FirebaseConnector", create=True)
@patch("core.services.watchdog.diagnose_and_repair", create=True)
async def test_watchdog_system_failure_flow(mock_diagnose, mock_firebase_cls):
    """Verify SREWatchdog handles timeout errors and invokes autonomous repair."""
    # Setup mocks
    mock_bus = AsyncMock(spec=GlobalBus)
    mock_firebase = mock_firebase_cls.return_value
    mock_firebase.log_repair_event = AsyncMock()

    mock_diagnose.return_value = {"status": "success", "message": "Repaired correctly"}

    watchdog = SREWatchdog(node_id="test-node", bus=mock_bus)

    # Directly invoke the system failure protocol (simulating log match)
    await watchdog._heal_system_failure()

    # 1. Verify diagnosing state logged to Firebase
    mock_firebase.log_repair_event.assert_any_call(
        filepath="system",
        diagnosis="Timeout/Connection error detected. Initiating autonomous repair.",
        status="diagnosing"
    )

    # 2. Verify diagnosing state sent to frontend
    mock_bus.publish.assert_any_call(
        "frontend_events",
        {"type": "repair_state", "status": "diagnosing", "message": "Initiating autonomous repair...", "log": "Timeout/Connection error detected."}
    )

    # 3. Verify diagnose_and_repair was called
    mock_diagnose.assert_called_once()

    # 4. Verify applied state logged to Firebase
    mock_firebase.log_repair_event.assert_any_call(
        filepath="system",
        diagnosis="Repaired correctly",
        status="applied"
    )

    # 5. Verify applied state sent to frontend
    mock_bus.publish.assert_any_call(
        "frontend_events",
        {"type": "repair_state", "status": "applied", "message": "Autonomous repair applied.", "log": "Repaired correctly"}
    )
