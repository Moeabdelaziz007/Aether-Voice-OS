"""
Aether Voice OS — Paralinguistic Analytics Engine.

Analyzes non-verbal cues in audio (pitch, rate, variance) to detect user
sentiment and engagement. This forms the fitness feedback for the Genetic Optimizer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


@dataclass
class ParalinguisticFeatures:
    """Core audio features for affective computing."""

    pitch_estimate: float  # Fundamental frequency estimate
    speech_rate: float  # Syllables/words per second estimate based on energy peaks
    rms_variance: float  # Energy variability (monotone vs expressive)
    spectral_centroid: float  # "Brightness" of voice (breathiness vs sharpness)
    engagement_score: float  # Unified 0.0 - 1.0 metric
    zen_mode: bool = False  # Flag for deep focus (typing/silence)


class ParalinguisticAnalyzer:
    """
    Analyzes PCM audio chunks to extract emotive signifiers.
    Implementation focuses on sub-5ms processing for zero-friction.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._history_pitch: list[float] = []
        self._history_rate: list[float] = []
        self._history_transients: list[int] = []  # Count of high-freq transients
        self._window_size = 20  # Last 2 seconds of interaction (more reactive)
        self._zen_threshold = 0.7  # Sentiment/Transience threshold for Zen

    def _detect_transients(self, pcm_chunk: NDArray[np.int16]) -> int:
        """Detect sharp high-frequency spikes (typing clicks)."""
        if len(pcm_chunk) < 64:
            return 0

        # High-pass filter approximation (simple difference)
        diff = np.diff(pcm_chunk.astype(np.float32))
        std = np.std(diff)

        # Count values that are N times the standard deviation (spikes)
        threshold = std * 5
        peaks = np.where(np.abs(diff) > threshold)[0]

        # Cluster peaks to avoid counting the same spike multiple times
        if len(peaks) < 2:
            return len(peaks)

        cluster_count = 1
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i - 1] > 100:  # 100 samples min gap (~6ms)
                cluster_count += 1
        return cluster_count

    def _estimate_pitch(self, pcm_chunk: NDArray[np.int16]) -> float:
        """Estimate fundamental frequency (F0) using autocorrelation."""
        if len(pcm_chunk) < 64:
            return 0.0

        # Normalize and remove DC offset
        audio = pcm_chunk.astype(np.float32)
        audio -= np.mean(audio)

        # Autocorrelation (Time-domain F0 estimation)
        corr = np.correlate(audio, audio, mode="full")
        corr = corr[len(corr) // 2 :]

        # Find first zero crossing
        d = np.diff(corr)
        crossings = np.where(d > 0)[0]
        if len(crossings) == 0:
            return 0.0

        # Find peak after first zero crossing
        peak = np.argmax(corr[crossings[0] :]) + crossings[0]

        if peak == 0:
            return 0.0

        f0 = self.sample_rate / peak

        # Standard human speech range filter (50Hz - 500Hz)
        if 50 <= f0 <= 500:
            return float(f0)
        return 0.0

    def _estimate_rate(self, pcm_chunk: NDArray[np.int16]) -> float:
        """Estimate speech rate via envelope peak counting."""
        if len(pcm_chunk) < 512:
            return 0.0

        # 1. Rectify and Smooth (Envelope Follower)
        abs_signal = np.abs(pcm_chunk.astype(np.float32) / 32768.0)

        # Simple moving average for smoothing (window size ~30ms)
        window = int(self.sample_rate * 0.03)
        if window < 1:
            window = 1
        envelope = np.convolve(abs_signal, np.ones(window) / window, mode="same")

        # 2. Peak Detection on envelope (Counting "Syllables")
        # Find local maxima above a noise threshold
        threshold = np.mean(envelope) * 1.5
        peaks = 0
        for i in range(1, len(envelope) - 1):
            if (
                envelope[i] > threshold
                and envelope[i] > envelope[i - 1]
                and envelope[i] > envelope[i + 1]
            ):
                peaks += 1

        # 3. Normalize to Syllables per Second
        duration_sec = len(pcm_chunk) / self.sample_rate
        rate = peaks / duration_sec if duration_sec > 0 else 0.0

        return float(rate)

    def analyze(
        self, pcm_chunk: NDArray[np.int16], current_rms: float
    ) -> ParalinguisticFeatures:
        """Full spectral-temporal emotive analysis."""
        if len(pcm_chunk) == 0:
            return ParalinguisticFeatures(0, 0, 0, 0, 0.5)

        # 1. Pitch
        pitch = self._estimate_pitch(pcm_chunk)
        if pitch > 0:
            self._history_pitch.append(pitch)
            if len(self._history_pitch) > self._window_size:
                self._history_pitch.pop(0)

        # 2. Rate
        rate = self._estimate_rate(pcm_chunk)
        if rate > 0:
            self._history_rate.append(rate)
            if len(self._history_rate) > self._window_size:
                self._history_rate.pop(0)

        # 3. Focus: Transient Detection (Keyboard clicks)
        transients = self._detect_transients(pcm_chunk)
        self._history_transients.append(transients)
        if len(self._history_transients) > self._window_size:
            self._history_transients.pop(0)

        # 4. RMS Variance (Expressiveness)
        # Higher variance usually means more emotive speech
        rms_var = (
            float(np.var(self._history_pitch)) if len(self._history_pitch) > 5 else 0.0
        )

        # 5. Spectral Centroid (Rough Brightness)
        fft = np.fft.rfft(pcm_chunk.astype(np.float32) / 32768.0)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(pcm_chunk), 1.0 / self.sample_rate)
        centroid = float(np.sum(magnitudes * freqs) / (np.sum(magnitudes) + 1e-10))

        # 6. Engagement Logic (Neuro-Darwinism Scoring)
        # - Good: High Centroid, high Pitch, expressiveness (Variance)
        # - Bad: Monotone, Low Pitch (lethargy), Low Centroid (dullness)
        base_engagement = 0.5

        # Affective Weights
        if pitch > 180:
            base_engagement += 0.1  # Interested
        if centroid > 2500:
            base_engagement += 0.1  # Bright/Alert
        if rms_var > 100:
            base_engagement += 0.1  # Expressive
        if rate > 4.0:
            base_engagement += 0.05  # Energetic pace

        engagement = max(0.0, min(1.0, base_engagement))

        # 7. Zen Mode Detection (Neural Shield)
        # logic: high concentration detected if we see typing cadence and low speech
        avg_transience = (
            np.mean(self._history_transients) if self._history_transients else 0
        )
        is_zen = False
        if current_rms < 0.05:  # Low background noise (silence)
            # 0.25 means average 2.5 spikes/sec (Relaxed coding pace)
            if avg_transience > 0.25:
                is_zen = True

        return ParalinguisticFeatures(
            pitch_estimate=pitch,
            speech_rate=rate,
            rms_variance=rms_var,
            spectral_centroid=centroid,
            engagement_score=engagement,
            zen_mode=is_zen,
        )
