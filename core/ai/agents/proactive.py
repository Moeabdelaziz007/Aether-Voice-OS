import logging
import time

logger = logging.getLogger(__name__)

from core.emotion.calibrator import EmotionCalibrator
from core.tools.vision_tool import take_screenshot


class ProactiveInterventionEngine:
    """
    Analyzes emotional state to trigger proactive voice interruptions
    if frustration exceeds thresholds.
    """

    def __init__(self, cooldown_minutes: int = 5):
        self.cooldown_seconds = cooldown_minutes * 60
        self.last_intervention_time = 0
        self.frustration_threshold = 0.75  # Scale 0.0 to 1.0
        self.calibrator = EmotionCalibrator()

    def calculate_frustration(self, valence: float, arousal: float) -> float:
        """
        Calculates frustration score.
        Updated to detect 'Resignation' (Sighs) which are Low Arousal + Negative Valence.
        Also factors in dynamic baselines.
        """
        if valence >= 0:
            return 0.0

        neg_valence = abs(valence)

        # If extremely negative, trigger regardless of arousal (Deep frustration)
        if neg_valence > 0.8:
            return neg_valence

        # Weighted: Valence is the primary driver, Arousal amplifies it.
        # (0.5 base ensures low-energy sighs are still captured)

        # Apply Baseline Normalization
        baseline = self.calibrator.baseline_manager.get_baselines()
        noise_floor = baseline.get("rms", 0.01)

        # If the arousal is just room noise, dampen the score
        if arousal < noise_floor * 2:
            arousal *= 0.5

        frustration = neg_valence * (0.5 + (arousal * 0.5))
        return min(1.0, frustration)

    def should_intervene(
        self, valence: float, arousal: float, skip_cooldown=False
    ) -> bool:
        """
        Evaluates current emotion against cooldowns to trigger intervention.
        """
        now = time.time()
        if not skip_cooldown and (
            now - self.last_intervention_time < self.cooldown_seconds
        ):
            return False

        score = self.calculate_frustration(valence, arousal)

        effective_threshold = self.calibrator.current_threshold
        if not self.calibrator.baseline_manager.is_calibrated:
            effective_threshold += 0.1  # Stricter during calibration window

        if score > effective_threshold:
            self.last_intervention_time = now
            logger.warning(f"Proactive Trigger Fired! Frustration: {score:.2f}")
            return True

        return False

    def generate_empathetic_message(self) -> str:
        return "أشعر بضيقك في هذا الجزء. هل تريد أن نلقي نظرة معاً على الكود لحلها؟"


class CodeAwareProactiveAgent:
    """
    Suggests tools to provide context-aware help during an intervention.
    """

    def __init__(self):
        pass

    async def get_investigation_tools(self) -> list[dict]:
        """
        Returns a list of tool definitions or immediate actions to perform
        when frustration is detected.
        """
        from core.tools.rag_tool import search_codebase
        from core.tools.vision_tool import take_screenshot

        return [
            {
                "tool": "search_codebase",
                "reason": "User frustration detected. Search the local codebase to pinpoint the structural issue.",
                "function": search_codebase,
            },
            {
                "tool": "take_screenshot",
                "reason": "User frustration detected. Visual context needed to diagnose the issue on their screen.",
                "function": take_screenshot,
            },
        ]
