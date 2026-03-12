import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.infra.transport.gateway import AetherGateway

    from .facade import GeminiLiveSession

from google.genai import types

from core.ai.agents.proactive import VisionPulseAgent
from core.audio.state import audio_state

logger = logging.getLogger(__name__)

class SensoryManager:
    """
    Orchestrates proactive perception (Vision Pulse) and acoustic empathy (Backchanneling).
    Extracted from GeminiLiveSession to reduce focal complexity.
    """
    def __init__(self, session: "GeminiLiveSession", gateway: "AetherGateway"):
        self.session = session
        self.gateway = gateway
        self.vision_pulse = VisionPulseAgent()
        self.running = False

    async def start_loops(self, session_handle: Any):
        """Start sensory loops concurrently."""
        self.running = True
        await asyncio.gather(
            self._proactive_vision_loop(session_handle),
            self._backchannel_loop(session_handle)
        )

    def stop(self):
        self.running = False

    async def _proactive_vision_loop(self, session_handle: Any) -> None:
        """Periodically captures screenshots and injects them into the Gemini stream."""
        logger.info("Vision Pulse loop active (Proactive Perception enabled)")
        while self.running and self.session._running:
            try:
                image_bytes = await self.vision_pulse.capture_pulse()
                if image_bytes and self.vision_pulse.should_pulse():
                    logger.info("📸 Sending Proactive Vision Pulse to Gemini.")
                    await session_handle.send_realtime_input(
                        video=types.Blob(data=image_bytes, mime_type="image/jpeg")
                    )
                    self.vision_pulse.record_pulse()

                    if self.gateway:
                        asyncio.create_task(
                            self.gateway.broadcast(
                                "vision_pulse",
                                {
                                    "status": "captured",
                                    "timestamp": datetime.now().isoformat(),
                                },
                            )
                        )
            except Exception as e:
                logger.debug("Vision pulse cycle failed: %s", e)
                await asyncio.sleep(2.0)
            await asyncio.sleep(1.0)

    async def _backchannel_loop(self, session_handle: Any) -> None:
        """Monitors Silence Architecture signals for empathetic backchanneling."""
        logger.info("Backchannel loop active (Acoustic Empathy enabled)")
        thinking_streak = 0
        while self.running and self.session._running:
            await asyncio.sleep(0.5)
            if audio_state.is_playing:
                thinking_streak = 0
                continue

            stype = audio_state.silence_type
            if stype in ("thinking", "breathing"):
                thinking_streak += 1
                if thinking_streak >= 10:  # ~5 seconds
                    logger.info("🧠 Empathy Trigger: User is thinking. Sending backchannel cue.")
                    try:
                        await session_handle.send_realtime_input(
                            text="[User is thinking/silent - consider a brief backchannel affirmative]"
                        )
                        thinking_streak = 0
                    except Exception as e:
                        logger.debug("Backchannel send failed: %s", e)
            else:
                thinking_streak = 0
