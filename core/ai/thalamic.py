import asyncio
import logging

from core.audio.state import audio_state

logger = logging.getLogger(__name__)


class ThalamicGate:
    """
    Central routing hub for proactive interventions.
    Simplified V3: Removed legacy emotion/analytics dependencies.
    Monitors acoustic state to decide when to trigger a barge-in.
    """

    def __init__(self, gemini_session):
        self._gemini_session = gemini_session
        self._frustration_streak = 0
        self._running = False
        self._last_trigger_time: float = 0

    async def start(self):
        self._running = True
        logger.info("🧠 Thalamic Gate V3: Online.")
        asyncio.create_task(self._monitor_loop())

    def stop(self):
        self._running = False

    async def _monitor_loop(self):
        """Background loop monitoring acoustic indices to trigger help."""
        while self._running:
            await asyncio.sleep(0.1)

            if audio_state.is_playing:
                self._frustration_streak = 0
                continue

            # For the demo MVP, we synthesize a 'need-help' score based on silence
            # type and acoustic features.
            need_help_score = self._compute_need_help_score()

            if need_help_score > 0.6:
                self._frustration_streak += 1
                if self._frustration_streak >= 15:  # ~1.5 seconds of sustained 'need-help'
                    logger.warning("🚨 THALAMIC GATE: Proactive Intervention Triggered!")
                    self._last_trigger_time = asyncio.get_event_loop().time()
                    await self._trigger_intervention()
                    self._frustration_streak = 0
            else:
                self._frustration_streak = max(0, self._frustration_streak - 1)

    def _compute_need_help_score(self) -> float:
        """
        Calculates a metric for 'need-help' based on VAD properties.
        """
        score = 0.0
        # If user is heavily "breathing" or "sighing" loudly
        if hasattr(audio_state, "silence_type") and audio_state.silence_type in (
            "breathing",
            "sighing",
        ):
            score += 0.5

        # Correlate with RMS (loud sigh)
        if hasattr(audio_state, "last_rms"):
            if audio_state.last_rms > 0.05:
                score += 0.4

        return score

    async def _trigger_intervention(self):
        """Forces the Gemini session to speak proactively."""
        try:
            from google.genai import types

            # This triggers the prompt directly into the current Live Session
            # context window.
            if hasattr(self._gemini_session, "send_text"):
                await self._gemini_session.send_text(
                    "[SYSTEM: User needs assistance. Proactively intervene immediately. "
                    "Read their screen/code and offer the exact fix with deep empathy.]"
                )
            else:
                # Fallback to direct session injection
                await self._gemini_session._session.send_realtime_input(
                    parts=[
                        types.Part(
                            text=(
                                "[SYSTEM: User needs assistance. Proactively intervene immediately. "
                                "Read their screen/code and offer the exact fix with deep empathy.]"
                            )
                        )
                    ]
                )
        except Exception as e:
            logger.error("Thalamic Gate intervention failed: %s", e)
        finally:
            # Measure and emit latency to Gateway
            if self._last_trigger_time > 0:
                latency_ms = (asyncio.get_event_loop().time() - self._last_trigger_time) * 1000
                logger.info("⚡ Intervention Latency: %.2fms", latency_ms)

                # Proactively emit to gateway if possible
                if hasattr(self._gemini_session, "_gateway"):
                    asyncio.create_task(
                        self._gemini_session._gateway.broadcast(
                            "interrupt_latency",
                            {"ms": float(latency_ms), "ts_ms": int(asyncio.get_event_loop().time() * 1000)},
                        )
                    )
                self._last_trigger_time = 0
