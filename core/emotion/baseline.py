import logging
import time
from collections import deque
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmotionBaselineManager:
    """
    Manages a dynamic acoustic baseline for a specific user session.
    Collects metrics over a designated calibration period (e.g., first 30s)
    to normalize frustration scoring.
    """

    def __init__(self, calibration_duration_seconds: int = 30):
        self._calibration_duration = calibration_duration_seconds
        self._start_time = time.time()
        self._is_calibrated = False
        self._metrics_history = deque(maxlen=300)  # Roughly 30 seconds at 10Hz

        # Baselines
        self._baseline_rms = 0.0
        self._baseline_pitch_variance = 0.0
        self._baseline_silence_ratio = 0.0

        logger.info(
            "🧠 EmotionBaselineManager: Started calibration window (%ds)",
            self._calibration_duration,
        )

    @property
    def is_calibrated(self) -> bool:
        if (
            not self._is_calibrated
            and (time.time() - self._start_time) >= self._calibration_duration
        ):
            self._finalize_calibration()
        return self._is_calibrated

    def record_acoustic_state(
        self, rms: float, is_speaking: bool, pitch_variance: float = 0.0
    ):
        """Records a snapshot of the acoustic state during the calibration window."""
        if self._is_calibrated:
            return

        self._metrics_history.append(
            {"rms": rms, "is_speaking": is_speaking, "pitch_variance": pitch_variance}
        )

    def _finalize_calibration(self):
        """Calculates the averages and sets the baseline."""
        if not self._metrics_history:
            logger.warning("🧠 Baseline: Not enough data points. Using defaults.")
            self._is_calibrated = True
            return

        total_rms = sum(m["rms"] for m in self._metrics_history)
        speaking_frames = sum(1 for m in self._metrics_history if m["is_speaking"])
        total_pitch_var = sum(m["pitch_variance"] for m in self._metrics_history)

        count = len(self._metrics_history)

        self._baseline_rms = total_rms / count
        self._baseline_silence_ratio = 1.0 - (speaking_frames / count)
        self._baseline_pitch_variance = total_pitch_var / count

        self._is_calibrated = True
        logger.info(
            "🧠 EmotionBaselineManager: Calibration Complete. "
            "Base RMS: %.4f | Base Silence Ratio: %.2f",
            self._baseline_rms,
            self._baseline_silence_ratio,
        )

    def get_baselines(self) -> Dict[str, float]:
        """Returns the calculated baselines, or defaults if not ready."""
        if not self.is_calibrated:
            return {"rms": 0.01, "silence_ratio": 0.5, "pitch_variance": 0.0}

        return {
            "rms": self._baseline_rms,
            "silence_ratio": self._baseline_silence_ratio,
            "pitch_variance": self._baseline_pitch_variance,
        }
