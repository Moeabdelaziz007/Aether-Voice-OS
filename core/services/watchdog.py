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

from core.audio.state import audio_state
from core.infra.cloud.firebase.interface import FirebaseConnector
from core.infra.transport.bus import GlobalBus
from core.tools.healing_tool import diagnose_and_repair

logger = logging.getLogger(__name__)


class WatchdogLogHandler(logging.Handler):
    """
    Custom logging handler that intercepts errors and alerts the Watchdog.
    """

    def __init__(self, callback: Callable[[logging.LogRecord], None]):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord):
        # Prevent recursive monitoring: ignore logs from this module
        # or SREWatchdog itself
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
        firebase_connector: Optional[Any] = None,
        audio_manager: Optional[Any] = None,
    ):
        self._node_id = node_id
        self._bus = bus
        self._gateway = gateway
        self._firebase = firebase_connector or FirebaseConnector()
        self._audio_manager = audio_manager

        self._is_running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._log_handler = WatchdogLogHandler(self._on_log_error)

        # Healing Registry: Pattern -> Action
        self._healing_registry: Dict[str, Callable] = {}
        self._register_default_patterns()

    def _register_default_patterns(self):
        """Register default failure patterns."""
        self._healing_registry.update({
            r"Redis.*connection.*failed": self._heal_bus_failure,
            r"timeout.*error": self._heal_system_failure,
            r"connection.*error": self._heal_system_failure,
            r"Audio device.*disconnected": self._recover_audio_device,
            r"AEC.*diverged": self._reset_aec,
            r"Queue.*overflow.*100": self._throttle_audio,
        })

        # Failure counts for throttling
        self._failure_counts: Dict[str, int] = {}
        self._last_alert_time: Dict[str, float] = {}

    def start(self):
        """Hook into system logging and start the watchdog loop."""
        # Capture the active event loop for thread-safe cross-thread calls
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.get_event_loop()

        # Use deep hook to catch logs from all modules
        logging.getLogger().addHandler(self._log_handler)
        self._is_running = True
        self._loop_task = self._loop.create_task(self._watchdog_loop())
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
        # Non-blocking, cross-thread safe processing
        if getattr(self, "_loop", None) and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._process_failure(message))
            )

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

    async def log_audio_metrics(self, metrics: dict):
        """Log audio metrics to Firebase for analysis"""
        if not self._firebase.is_connected:
            return

        try:
            await self._firebase.log_event("audio_telemetry", {
                "timestamp": datetime.now().isoformat(),
                "rms": metrics.get("rms"),
                "aec_erle": metrics.get("aec_erle"),
                "aec_converged": metrics.get("aec_converged"),
                "queue_drops": getattr(audio_state, "capture_queue_drops", 0),
            })
        except Exception as e:
            logger.error("Failed to log audio metrics: %s", e)

    # --- Healing Protocols ---

    async def _recover_audio_device(self, error_msg: str = ""):
        """Recover from audio device disconnection"""
        logger.warning("Audio device lost, attempting recovery...")

        # 1. Notify frontend
        if self._gateway:
            await self._gateway.broadcast("system_failure", {
                "event": "audio_device_lost",
                "state": "diagnosing",
            })

        # 2. Try to reinitialize
        try:
            if self._audio_manager:
                await self._audio_manager.restart()
                if self._gateway:
                    await self._gateway.broadcast("system_failure", {
                        "event": "audio_device_lost",
                        "state": "applied",
                    })
        except Exception as e:
            if self._gateway:
                await self._gateway.broadcast("system_failure", {
                    "event": "audio_device_lost",
                    "state": "failed",
                    "message": str(e),
                })

    async def _reset_aec(self, error_msg: str = ""):
        """Reset AEC when it diverges"""
        logger.warning("AEC divergence detected, resetting filter...")

        if self._audio_manager:
            self._audio_manager.reset_aec()

    async def _throttle_audio(self, error_msg: str = ""):
        """Throttle audio when queue overflows"""
        logger.warning("Queue overflow detected, throttling audio...")
        if self._gateway:
            await self._gateway.broadcast("system_failure", {
                "event": "queue_overflow",
                "state": "throttling",
            })

    async def _heal_bus_failure(self):
        """Protocol: Redis/Bus connection recovery."""
        if self._bus:
            logger.info("🛠️ [HEAL] Attempting to reconnect Global State Bus...")
            await self._bus.disconnect()
            await asyncio.sleep(2)
            await self._bus.connect()

    async def _heal_system_failure(self):
        """Protocol: Timeout/connection error recovery via autonomous diagnosis."""
        logger.info("🛠️ [HEAL] Initiating autonomous diagnosis for system failure...")

        # Log diagnosing state
        await self._firebase.log_repair_event(
            filepath="system",
            diagnosis="Timeout/Connection error detected. Initiating repair.",
            status="diagnosing",
        )

        # Signal front-end about the repair state
        if self._bus:
            await self._bus.publish(
                "frontend_events",
                {
                    "type": "repair_state",
                    "status": "diagnosing",
                    "message": "Initiating autonomous repair...",
                    "log": "Timeout/Connection error detected.",
                },
            )

        try:
            # Trigger grounded diagnosis
            diagnosis_result = await diagnose_and_repair()

            # Log successful application/diagnosis
            await self._firebase.log_repair_event(
                filepath="system",
                diagnosis=str(diagnosis_result.get("message", "Repair proposed")),
                status="applied",
            )

            # Signal front-end about the repair state
            if self._bus:
                await self._bus.publish(
                    "frontend_events",
                    {
                        "type": "repair_state",
                        "status": "applied",
                        "message": "Autonomous repair applied.",
                        "log": str(diagnosis_result.get("message", "")),
                    },
                )

        except Exception as e:
            logger.error("Error during autonomous repair: %s", e)
            await self._firebase.log_repair_event(
                filepath="system",
                diagnosis=f"Failed to apply repair: {e}",
                status="failed",
            )
            if self._bus:
                await self._bus.publish(
                    "frontend_events",
                    {
                        "type": "repair_state",
                        "status": "failed",
                        "message": f"Repair failed: {e}",
                        "log": f"Error: {e}",
                    },
                )
