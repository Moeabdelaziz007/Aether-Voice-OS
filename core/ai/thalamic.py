import asyncio
import logging

from core.analytics.demo_metrics import DemoMetrics
from core.audio.state import audio_state
from core.emotion.calibrator import EmotionCalibrator

logger = logging.getLogger(__name__)


class ThalamicGate:
    """
    Central routing hub for proactive interventions (Software-Defined AEC and
    Emotional Triggering).
    Monitors emotional indices (frustration) and decides when to trigger a barge-in.
    """

    def __init__(self, gemini_session):
        self._gemini_session = gemini_session
        self._calibrator = EmotionCalibrator()
        self._metrics = DemoMetrics()
        self._frustration_streak = 0
        self._running = False

    async def start(self):
        self._running = True
        logger.info("🧠 Thalamic Gate V2: Online and monitoring affective state.")
        asyncio.create_task(self._monitor_loop())

    def stop(self):
        self._running = False

    @property
    def calibrator(self) -> EmotionCalibrator:
        return self._calibrator

    @property
    def metrics(self) -> DemoMetrics:
        return self._metrics

    async def _monitor_loop(self):
        """Background loop monitoring frustration indices to trigger help."""
        while self._running:
            await asyncio.sleep(0.1)

            if audio_state.is_playing:
                self._frustration_streak = 0
                continue

            # Record acoustic state for baseline generation
            is_speaking = False
            rms = getattr(audio_state, "last_rms", 0.0)

            if hasattr(audio_state, "silence_type"):
                is_speaking = audio_state.silence_type not in ["absolute", "breathing"]

            self._calibrator.baseline_manager.record_acoustic_state(
                rms=rms, is_speaking=is_speaking
            )

            # For the demo MVP, we synthesize a frustration score based on silence
            # type and acoustic features.
            frustration_score = self._compute_frustration_score()

            if self._calibrator.should_intervene({"frustration": frustration_score}):
                self._frustration_streak += 1
                if (
                    self._frustration_streak >= 15
                ):  # ~1.5 seconds of sustained frustration
                    logger.warning(
                        "🚨 THALAMIC GATE: Proactive Intervention Triggered! "
                        "(Score: %.2f)",
                        frustration_score,
                    )
                    self._metrics.start_timer("intervention_latency")
                    await self._trigger_intervention()
                    self._frustration_streak = 0
            else:
                self._frustration_streak = max(0, self._frustration_streak - 1)

    def _compute_frustration_score(self) -> float:
        """
        Calculates a metric for 'frustration' for demo purposes based on VAD properties.
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
            await self._gemini_session.send_realtime_input(
                parts=[
                    types.Part.from_text(
                        text=(
                            "[SYSTEM: User is highly frustrated. Proactively "
                            "intervene immediately in Arabic. Read their screen/"
                            "code and offer the exact fix with deep empathy.]"
                        )
                    )
                ]
            )
            self._metrics.stop_timer("intervention_latency")
            self._metrics.record_accuracy(True)
        except Exception as e:
            logger.error("Thalamic Gate intervention failed: %s", e)
