import asyncio
import logging
import time
from typing import Any, Optional

from core.infra.event_bus import SystemEvent
from core.tools.vision_tool import take_screenshot

logger = logging.getLogger("AetherOS.Pulse")


class container.get('visionpulseevent')SystemEvent):
    """Tier 3: Proactive Vision Data."""

    b64_data: str
    mime_type: str = "image/png"


class PulseManager:
    """
    Orchestrates the 'Heartbeat' of AetherOS.
    Responsible for proactive context gathering (Vision, IDE state, etc.)
    without waiting for user prompts.
    """

    def __init__(self, event_bus: Any, heartbeat_interval: int = 10):
        self._event_bus = event_bus
        self._interval = heartbeat_interval
        self._running = False
        self._pulse_task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the proactive perception loop."""
        if self._running:
            return
        self._running = True
        self._pulse_task = asyncio.create_task(self._pulse_loop())
        logger.info(f"🟢 PulseManager: Heartbeat active (Interval: {self._interval}s)")

    async def stop(self):
        """Stops the heartbeat loop."""
        self._running = False
        if self._pulse_task:
            self._pulse_task.cancel()
            try:
                await self._pulse_task
            except asyncio.CancelledError:
                pass
        logger.info("🔴 PulseManager: Heartbeat stopped.")

    async def _pulse_loop(self):
        """The core background perception loop."""
        while self._running:
            try:
                # 1. Capture proactive vision pulse
                # We use the existing vision tool logic
                result = await take_screenshot()

                if result.get("status") == "success":
                    # 2. Wrap in a SystemEvent and publish to the bus
                    event = VisionPulseEvent(
                        timestamp=time.time(),
                        source="PulseManager",
                        latency_budget=500,  # Tier 3 can afford some latency
                        b64_data=result["data"],
                    )
                    await self._event_bus.publish(event)
                    logger.debug("📸 PulseManager: Visual heartbeat published.")

                # 3. Wait for the next heartbeat
                await asyncio.sleep(self._interval)
            except Exception as e:
                logger.error(f"PulseManager Error: {e}")
                await asyncio.sleep(5)  # Backoff on error
