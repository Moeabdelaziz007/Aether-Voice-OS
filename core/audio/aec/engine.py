from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass

import numpy as np

from core.audio.aec.buffer import BoundedBuffer
from core.audio.aec.detectors import DelayEstimator, DoubleTalkDetector
from core.audio.aec.filters import FrequencyDomainNLMS
from core.audio.spectral import erle

logger = logging.getLogger(__name__)

@dataclass
class AECState:
    converged: bool = False
    convergence_progress: float = 0.0
    erle_db: float = 0.0
    estimated_delay_ms: float = 0.0
    double_talk_detected: bool = False
    filter_tap_energy: float = 0.0
    frames_processed: int = 0

class DynamicAEC:
    """Main AEC orchestration engine."""
    def __init__(self, sample_rate: int = 16000, frame_size: int = 256, filter_length_ms: float = 100.0, step_size: float = 0.5, convergence_threshold_db: float = 15.0) -> None:
        self.sample_rate, self.frame_size, self.convergence_threshold_db = sample_rate, frame_size, convergence_threshold_db
        filter_length = 2 ** int(np.ceil(np.log2(max(int(filter_length_ms * sample_rate / 1000), frame_size * 2))))
        filter_length = max(filter_length, 512)
        self.adaptive_filter = FrequencyDomainNLMS(filter_length=filter_length, step_size=step_size)
        self.delay_estimator = DelayEstimator(sample_rate=sample_rate)
        self.double_talk_detector = DoubleTalkDetector(sample_rate=sample_rate)
        self.block_size = filter_length
        self.far_end_ring_buffer = deque(maxlen=20)
        self.near_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.far_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.accumulated_samples = 0
        self.state = AECState()
        self.erle_history = deque(maxlen=50)
        self.convergence_frame_count = 0
        self.convergence_frames_needed = 100
        self._divergence_counter = 0
        self._divergence_threshold = 30
        self._last_erle_values = deque(maxlen=20)

    def process_frame(self, near_end: np.ndarray, far_end: np.ndarray) -> tuple[np.ndarray, AECState]:
        near_end_float = np.asarray(near_end).flatten()[:self.frame_size].astype(np.float64) / 32768.0
        far_end_float = np.asarray(far_end).flatten()[:self.frame_size].astype(np.float64) / 32768.0
        self.delay_estimator.process(far_end_float, near_end_float)
        self.far_end_ring_buffer.append(far_end_float.copy())
        self.near_end_accumulator.append(near_end_float.copy())
        self.far_end_accumulator.append(far_end_float.copy())
        self.accumulated_samples = len(self.near_end_accumulator)
        if self.accumulated_samples >= self.block_size:
            near_block, far_block = self.near_end_accumulator.pop_left(self.block_size), self.far_end_accumulator.pop_left(self.block_size)
            compensated_far_end = self._get_delayed_block(far_block, self.delay_estimator.estimated_delay_samples // self.frame_size)
            error_signal, estimated_echo = self.adaptive_filter.process(compensated_far_end, near_block)
            is_double_talk = self.double_talk_detector.update(compensated_far_end[-self.frame_size:], near_block[-self.frame_size:], error_signal[-self.frame_size:])
            current_erle = erle(near_block, error_signal, frame_size=self.block_size // 4)
            self.erle_history.append(current_erle)
            self._update_convergence(current_erle)
            self.state.erle_db, self.state.estimated_delay_ms, self.state.double_talk_detected = current_erle, self.delay_estimator.estimated_delay_ms, is_double_talk
            self.state.filter_tap_energy = self.adaptive_filter.get_filter_energy()
            output_error = error_signal[-self.frame_size:]
        else: output_error = near_end_float * 0.9
        self.state.frames_processed += 1
        return (np.clip(output_error, -1.0, 1.0) * 32767.0).astype(np.int16), self.state

    def _get_delayed_block(self, current_block: np.ndarray, delay_frames: int) -> np.ndarray:
        buffer_len = len(self.far_end_ring_buffer)
        if buffer_len == 0 or delay_frames == 0: return current_block
        result = np.zeros(self.block_size); result_idx = 0
        for i in range(delay_frames + 1):
            idx = buffer_len - 1 - delay_frames + i
            if 0 <= idx < buffer_len:
                frame = self.far_end_ring_buffer[idx]
                count = min(len(frame), self.block_size - result_idx)
                result[result_idx:result_idx + count] = frame[:count]
                result_idx += count
                if result_idx >= self.block_size: break
        if result_idx < self.block_size: result[result_idx:] = current_block[:self.block_size - result_idx]
        return result

    def _update_convergence(self, current_erle: float) -> None:
        if current_erle > self.convergence_threshold_db:
            self.convergence_frame_count += 1
            if self.convergence_frame_count >= self.convergence_frames_needed: self.state.converged = True
        else: self.convergence_frame_count = max(0, self.convergence_frame_count - 1)
        self.state.convergence_progress = min(1.0, self.convergence_frame_count / self.convergence_frames_needed)
