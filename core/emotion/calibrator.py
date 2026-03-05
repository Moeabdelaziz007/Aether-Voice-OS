import logging

import numpy as np

logger = logging.getLogger(__name__)


class EmotionCalibrator:
    """
    Learns from user feedback and interaction history to adjust
    emotion sensitivity thresholds dynamically, factoring in acoustic baselines.
    """

    def __init__(self):
        from core.emotion.baseline import EmotionBaselineManager

        self._thresholds = {"frustration": 0.85}  # Initial baseline for intervention
        self._baseline_mgr = container.get('emotionbaselinemanager')calibration_duration_seconds=30)
        self._feedback_history = []
        logger.info("🧠 EmotionCalibrator: System online (Frustration Baseline: 0.85)")

    @property
    def baseline_manager(self):
        return self._baseline_mgr

    def update_threshold(self, predicted: bool, actual: bool):
        """
        Learns from manual triggers or user corrections.
        If a manual trigger occurred (actual=True) but we had not predicted it,
        we lower the threshold to be more sensitive.
        """
        if predicted == actual:
            # Prediction was correct, tighten slightly for stability
            self._thresholds["frustration"] *= 0.98
        else:
            # Missed an intervention or had a false positive
            # If actual was True but we didn't trigger, decrease threshold
            # If actual was False but we triggered, increase threshold
            multiplier = 0.90 if actual else 1.10
            self._thresholds["frustration"] *= multiplier

        # Clamp to reasonable bounds
        self._thresholds["frustration"] = np.clip(
            self._thresholds["frustration"], 0.4, 0.95
        )
        logger.info(
            "🧠 Threshold Calibrated: frustration = %.4f",
            self._thresholds["frustration"],
        )

    def should_intervene(self, emotion_state: dict) -> bool:
        """Adaptive decision logic based on live threshold and baselines."""
        score = emotion_state.get("frustration", 0.0)

        # If still calibrating, we require a stronger signal to avoid false positives
        effective_threshold = self._thresholds["frustration"]
        if not self._baseline_mgr.is_calibrated:
            effective_threshold += 0.1  # Stricter during first 30s

        return score > effective_threshold

    @property
    def current_threshold(self) -> float:
        return self._thresholds["frustration"]
