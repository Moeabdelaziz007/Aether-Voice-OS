from collections import deque

import numpy as np

from core.audio.spectral import SpectralAnalyzer, gcc_phat


class DoubleTalkDetector:
    """Double-talk detection using spectral coherence and energy ratios."""
    def __init__(self, sample_rate: int = 16000, coherence_threshold: float = 0.65, energy_ratio_threshold: float = 0.5, hangover_frames: int = 10) -> None:
        self.sample_rate = sample_rate
        self.coherence_threshold = coherence_threshold
        self.energy_ratio_threshold = energy_ratio_threshold
        self.hangover_frames = hangover_frames
        self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate)
        self.far_end_history = deque(maxlen=4)
        self.near_end_history = deque(maxlen=4)
        self.hangover_counter = 0
        self.is_double_talk = False
        self.far_end_energy = 1e-10
        self.near_end_energy = 1e-10
        self.error_energy = 1e-10
        self.energy_alpha = 0.95

    def update(self, far_end: np.ndarray, near_end: np.ndarray, error_signal: np.ndarray) -> bool:
        self.far_end_energy = self.energy_alpha * self.far_end_energy + (1 - self.energy_alpha) * np.mean(far_end**2)
        self.near_end_energy = self.energy_alpha * self.near_end_energy + (1 - self.energy_alpha) * np.mean(near_end**2)
        self.error_energy = self.energy_alpha * self.error_energy + (1 - self.energy_alpha) * np.mean(error_signal**2)
        energy_test = (self.near_end_energy / (self.far_end_energy + 1e-10)) > (1.0 + self.energy_ratio_threshold)
        residual_test = (self.error_energy / self.near_end_energy > 0.8) if self.near_end_energy > 1e-6 else False
        coherence_test = (self.spectral_analyzer.compute_coherence(far_end, near_end, n_frames=3) < self.coherence_threshold) if len(self.far_end_history) >= 3 else False
        double_talk_now = energy_test or residual_test or coherence_test
        if double_talk_now:
            self.hangover_counter = self.hangover_frames
            self.is_double_talk = True
        elif self.hangover_counter > 0:
            self.hangover_counter -= 1
            self.is_double_talk = self.hangover_counter > 0
        else:
            self.is_double_talk = False
        self.far_end_history.append(far_end.copy())
        self.near_end_history.append(near_end.copy())
        return self.is_double_talk

    def reset(self) -> None:
        self.far_end_history.clear(); self.near_end_history.clear()
        self.hangover_counter = 0; self.is_double_talk = False
        self.far_end_energy = self.near_end_energy = self.error_energy = 1e-10

class DelayEstimator:
    """Adaptive delay estimation using GCC-PHAT."""
    def __init__(self, sample_rate: int = 16000, max_delay_ms: float = 200.0, update_interval_ms: float = 500.0, smoothing_factor: float = 0.9) -> None:
        self.sample_rate = sample_rate
        self.max_delay_samples = int(max_delay_ms * sample_rate / 1000)
        self.update_interval_samples = int(update_interval_ms * sample_rate / 1000)
        self.smoothing_factor = smoothing_factor
        self.far_end_buffer, self.near_end_buffer = deque(), deque()
        self.buffer_samples = self.samples_since_update = 0
        self.estimated_delay_samples = 0
        self.estimated_delay_ms = 0.0
        self.confidence = 0.0

    def process(self, far_end_chunk: np.ndarray, near_end_chunk: np.ndarray) -> tuple[int, float]:
        self.far_end_buffer.append(far_end_chunk.copy())
        self.near_end_buffer.append(near_end_chunk.copy())
        self.buffer_samples += len(far_end_chunk)
        self.samples_since_update += len(far_end_chunk)
        if self.samples_since_update >= self.update_interval_samples:
            far_end_signal, near_end_signal = np.concatenate(list(self.far_end_buffer)), np.concatenate(list(self.near_end_buffer))
            max_size = self.max_delay_samples * 4
            if len(far_end_signal) > max_size: far_end_signal, near_end_signal = far_end_signal[-max_size:], near_end_signal[-max_size:]
            delay, confidence = gcc_phat(far_end_signal, near_end_signal, sample_rate=self.sample_rate, max_delay=self.max_delay_samples)
            if confidence > 0.3:
                self.estimated_delay_samples = int(self.smoothing_factor * self.estimated_delay_samples + (1 - self.smoothing_factor) * delay)
                self.estimated_delay_ms = self.estimated_delay_samples * 1000.0 / self.sample_rate
                self.confidence = confidence
            self.far_end_buffer.clear(); self.near_end_buffer.clear()
            self.buffer_samples = self.samples_since_update = 0
        return self.estimated_delay_samples, self.confidence

    def get_delay_compensated_far_end(self, far_end_chunk: np.ndarray) -> np.ndarray:
        return far_end_chunk

    def reset(self) -> None:
        self.far_end_buffer.clear(); self.near_end_buffer.clear()
        self.buffer_samples = self.samples_since_update = 0
        self.estimated_delay_samples = self.confidence = 0
        self.estimated_delay_ms = 0.0
