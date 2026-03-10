import collections
import logging
from typing import Deque

import numpy as np

logger = logging.getLogger("AetherOS.VAD")

# ==========================================
# 🌌 Aether Dynamic VAD
# Intelligent Voice Activity Detection
# based on ambient noise floor tracking.
# ==========================================


class AetherVAD:
    """
    Software-defined Voice Activity Detector.
    Uses Hysteresis gating to prevent clipping and
    dynamic thresholding to adapt to room noise.
    """

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)

        # State Tracking
        self.is_voice_active = False
        self._voice_hysteresis_frames = 0
        self._silence_hysteresis_frames = 0

        # Calibration (Rolling RMS statistics)
        self._rms_history: Deque[float] = collections.deque(maxlen=100)  # 2 seconds of history
        self._noise_floor = 0.01

    def process_frame(self, pcm_data: bytes) -> bool:
        """
        Processes a single PCM frame and returns True if voice is detected.
        Implements a state machine to reduce 'choppiness'.
        """
        audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        if len(audio_np) == 0:
            return False

        rms = np.sqrt(np.mean(audio_np**2))
        self._rms_history.append(rms)

        # Re-calibrate noise floor every 2 seconds
        # We take the 20th percentile to estimate the base noise floor
        if len(self._rms_history) > 20:
            self._noise_floor = np.percentile(list(self._rms_history), 20)

        # Dynamic Thresholding
        # Voice is usually 2x to 5x higher than the noise floor
        threshold = self._noise_floor * 2.5 + 0.005

        frame_has_energy = rms > threshold

        # Hysteresis State Machine
        if frame_has_energy:
            self._voice_hysteresis_frames += 1
            self._silence_hysteresis_frames = 0

            # Require 2 consecutive energy frames to trigger 'active'
            if self._voice_hysteresis_frames >= 2:
                if not self.is_voice_active:
                    logger.debug("[VAD] 🎙 Voice Detected.")
                    self.is_voice_active = True
        else:
            self._silence_hysteresis_frames += 1
            self._voice_hysteresis_frames = 0

            # Require 15 consecutive silent frames (~300ms) to trigger 'idle'
            # This prevents sentence clipping
            if self._silence_hysteresis_frames >= 15:
                if self.is_voice_active:
                    logger.debug("[VAD] 🔇 Silence Detected.")
                    self.is_voice_active = False

        return self.is_voice_active

    def get_rms(self) -> float:
        """Returns the current frame's energy for telemetry."""
        if not self._rms_history:
            return 0.0
        return self._rms_history[-1]
