"""
Aether Voice OS — SRE Watchdog (Autonomy Layer).

Provides proactive system monitoring, log-based failure detection,
and autonomous healing triggers using the Global State Bus.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from core.infra.transport.bus import GlobalBus

logger = logging.getLogger(__name__)


class WatchdogLogHandler(logging.Handler):
    """
    Custom logging handler that intercepts errors and alerts the Watchdog.
    """

    def __init__(self, callback: Callable[[logging.LogRecord], None]):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord):
        # Prevent recursive monitoring: ignore logs from this module or SREWatchdog itself
        if record.name == __name__ or "watchdog" in record.name.lower():
            return
        if record.levelno >= logging.ERROR:
            self._callback(record)


class SREWatchdog:
    """
    Autonomous SRE Watchdog for AetherOS.

    Monitors system vitals and logs, publishes alerts to the Global Bus,
    and executes healing protocols.
    """

    def __init__(
        self,
        node_id: str,
        bus: Optional[GlobalBus] = None,
        gateway: Optional[Any] = None,
    ):
        self._node_id = node_id
        self._bus = bus
        self._gateway = gateway
        self._is_running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._log_handler = WatchdogLogHandler(self._on_log_error)

        # Healing Registry: Pattern -> Action
        self._healing_registry: Dict[str, Callable] = {
            r"Gemini.*timeout": self._heal_gemini_timeout,
            r"Redis.*connection.*failed": self._heal_bus_failure,
            r"Audio.*capture.*error": self._heal_audio_failure,
        }

        # Failure counts for throttling
        self._failure_counts: Dict[str, int] = {}
        self._last_alert_time: Dict[str, float] = {}

    def start(self):
        """Hook into system logging and start the watchdog loop."""
        # Use deep hook to catch logs from all modules
        logging.getLogger().addHandler(self._log_handler)
        self._is_running = True
        self._loop_task = asyncio.create_task(self._watchdog_loop())
        logger.info("✦ SRE Watchdog [Autonomy] initialized on Node: %s", self._node_id)

    def stop(self):
        """Graceful shutdown."""
        self._is_running = False
        if self._loop_task:
            self._loop_task.cancel()
        logging.getLogger().removeHandler(self._log_handler)

    async def _watchdog_loop(self):
        """Periodic health checks beyond log monitoring."""
        while self._is_running:
            try:
                # Check system metrics (simulated for now)
                await self._check_vitals()
                await asyncio.sleep(10.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("SRE Watchdog loop error: %s", e)

    async def _check_vitals(self):
        """Simulate vitals check and publish to bus."""
        if self._bus and self._bus.is_connected:
            await self._bus.publish(
                "system_health",
                {
                    "node_id": self._node_id,
                    "status": "HEALTHY",
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def _on_log_error(self, record: logging.LogRecord):
        """Called whenever an ERROR or higher is logged."""
        message = record.getMessage()
        # Non-blocking processing
        asyncio.create_task(self._process_failure(message))

    async def _process_failure(self, message: str):
        """Analyze failure and trigger healing if a pattern matches."""

        for pattern, action in self._healing_registry.items():
            if re.search(pattern, message, re.IGNORECASE):
                # Throttle check (prevent spamming alerts for same pattern)
                now = datetime.now().timestamp()
                last_time = self._last_alert_time.get(pattern, 0)
                if now - last_time < 5.0:  # 5s cooldown per pattern
                    return

                self._last_alert_time[pattern] = now
                logger.warning(
                    "🚨 SRE Watchdog detected critical pattern: '%s'", pattern
                )

                # Signal global health alert
                if self._bus:
                    await self._bus.publish(
                        "health_alerts",
                        {
                            "node_id": self._node_id,
                            "severity": "CRITICAL",
                            "pattern": pattern,
                            "message": message[:200],  # Truncate message
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

                # Trigger autonomous healing
                try:
                    logger.info("🛠️ Watchdog: Executing healing action for %s", pattern)
                    result = action()
                    if asyncio.iscoroutine(result):
                        await result
                    logger.info("✅ Watchdog: Healing action complete for %s", pattern)
                except Exception as e:
                    logger.error(
                        "Failed to execute healing action for %s: %s", pattern, e
                    )
                return

    # --- Healing Protocols ---

    async def _heal_gemini_timeout(self):
        """Protocol: Gemini session timeout recovery."""
        if self._gateway:
            logger.info("🛠️ [HEAL] Triggering proactive session reset...")
            # We assume AetherGateway has a trigger_reconnection or similar
            if hasattr(self._gateway, "restart"):
                await self._gateway.restart(
                    reason="Proactive SRE Recovery (Gemini Timeout)"
                )

    async def _heal_bus_failure(self):
        """Protocol: Redis/Bus connection recovery."""
        if self._bus:
            logger.info("🛠️ [HEAL] Attempting to reconnect Global State Bus...")
            await self._bus.disconnect()
            await asyncio.sleep(2)
            await self._bus.connect()

    async def _heal_audio_failure(self):
        """Protocol: Audio device recovery."""
        logger.info("🛠️ [HEAL] Signaling audio layer reset...")
        # In a real system, this might restart the capture task.
        pass
