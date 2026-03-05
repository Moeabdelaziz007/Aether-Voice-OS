"""
Aether Voice OS — Dynamic Acoustic Echo Cancellation (AEC).

Implements real-time adaptive echo cancellation using:
- GCC-PHAT delay estimation (adaptive, not fixed)
- Frequency-domain NLMS adaptive filtering
- Double-talk detection via spectral coherence
- ERLE (Echo Return Loss Enhancement) computation
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass

import numpy as np

from core.audio.spectral import SpectralAnalyzer, erle, gcc_phat

logger = logging.getLogger(__name__)


class BoundedBuffer:
    """A thread-safe preallocated ring buffer for audio samples.

    Improvement #1 (Qodo): Replaces np.concatenate-per-frame with a
    fixed-size circular buffer, eliminating O(n) reallocation in the
    hot callback path and reducing GC pressure / glitch risk.
    """

    def __init__(self, max_samples: int):
        self.max_samples = max_samples
        self._buf = np.zeros(max_samples, dtype=np.float64)
        self._write = 0  # write pointer
        self._count = 0  # valid samples stored
        self._lock = threading.Lock()

    def append(self, data: np.ndarray):
        """Append samples; oldest samples are silently dropped when full."""
        with self._lock:
            n = len(data)
            if n == 0:
                return
            if n >= self.max_samples:
                # Larger than buffer — keep only the last max_samples
                data = data[-self.max_samples :]
                n = self.max_samples
            # Write with wrap-around
            end = self._write + n
            if end <= self.max_samples:
                self._buf[self._write : end] = data
            else:
                first = self.max_samples - self._write
                self._buf[self._write :] = data[:first]
                self._buf[: end - self.max_samples] = data[first:]
            self._write = end % self.max_samples
            self._count = min(self._count + n, self.max_samples)

    def pop_left(self, n: int) -> np.ndarray:
        """Pop n oldest samples; returns empty array if not enough data."""
        with self._lock:
            if self._count < n:
                return np.array([], dtype=np.float64)
            read_start = (self._write - self._count) % self.max_samples
            end = read_start + n
            if end <= self.max_samples:
                extracted = self._buf[read_start:end].copy()
            else:
                first = self.max_samples - read_start
                extracted = np.concatenate(
                    [self._buf[read_start:], self._buf[: n - first]]
                )
            self._count -= n
            return extracted

    def clear(self):
        with self._lock:
            self._write = 0
            self._count = 0

    def __len__(self):
        return self._count


@dataclass
class AECState:
    """State information for the AEC system."""

    converged: bool = False
    convergence_progress: float = 0.0  # 0.0 to 1.0
    erle_db: float = 0.0  # Echo Return Loss Enhancement
    estimated_delay_ms: float = 0.0  # Current estimated delay
    double_talk_detected: bool = False  # True when near-end speech detected
    filter_tap_energy: float = 0.0  # Adaptive filter energy
    frames_processed: int = 0


class FrequencyDomainNLMS:
    """Frequency-domain Normalized Least Mean Squares adaptive filter.

    Uses overlap-save method for efficient frequency-domain processing.
    """

    def __init__(
        self,
        filter_length: int = 1024,
        step_size: float = 0.5,
        regularization: float = 1e-4,
        leakage: float = 0.999,
    ) -> None:
        """Initialize frequency-domain NLMS filter.

        Args:
            filter_length: Length of adaptive filter in samples
            step_size: Learning rate (mu), typically 0.1 to 1.0
            regularization: Regularization factor to avoid division by zero
            leakage: Filter leakage factor (prevents divergence, < 1.0)
        """
        self.filter_length = filter_length
        self.step_size = step_size
        self.regularization = regularization
        self.leakage = leakage

        # FFT size for overlap-save (2x filter length)
        self.block_size = filter_length
        self.n_fft = 2 * filter_length

        # Initialize filter weights (frequency domain)
        self.W = np.zeros(self.n_fft // 2 + 1, dtype=np.complex128)

        # Input buffer for overlap-save
        self.input_buffer = np.zeros(self.n_fft)
        self.output_buffer = np.zeros(self.block_size)

        # Power estimate for normalization
        self.power_estimate = np.ones(self.n_fft // 2 + 1) * 1e-6

        # Smoothing factor for power estimate
        self.alpha = 0.9

    def process(
        self, far_end: np.ndarray, near_end: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Process one block of audio through adaptive filter.

        Args:
            far_end: Far-end signal (speaker output) - shape (block_size,)
            near_end: Near-end signal (microphone input) - shape (block_size,)

        Returns:
            Tuple of (error_signal, estimated_echo)
        """
        # Ensure correct length
        far_end = np.asarray(far_end).flatten()[: self.block_size]
        near_end = np.asarray(near_end).flatten()[: self.block_size]

        # Shift input buffer and add new far-end block
        self.input_buffer[: self.block_size] = self.input_buffer[self.block_size :]
        self.input_buffer[self.block_size :] = far_end

        # FFT of input buffer
        X = np.fft.rfft(self.input_buffer)

        # Compute filter output (frequency-domain multiplication)
        Y = self.W * X

        # IFFT to get time-domain output
        y_full = np.fft.irfft(Y)
        estimated_echo = y_full[self.block_size :]  # Take second half (overlap-save)

        # Compute error signal
        error_signal = near_end - estimated_echo

        # Compute error in frequency domain for adaptation
        error_full = np.zeros(self.n_fft)
        error_full[self.block_size :] = error_signal
        E = np.fft.rfft(error_full)

        # Update power estimate (smoothed)
        X_mag_sq = np.abs(X) ** 2
        self.power_estimate = (
            self.alpha * self.power_estimate + (1 - self.alpha) * X_mag_sq
        )

        # NLMS update with regularization
        mu = self.step_size / (self.power_estimate + self.regularization)

        # Complex gradient update
        gradient = mu * np.conj(X) * E

        # Apply leakage and update weights
        self.W = self.leakage * self.W + gradient

        return error_signal, estimated_echo

    def get_filter_energy(self) -> float:
        """Compute total energy in adaptive filter."""
        time_weights = np.fft.irfft(self.W)
        return float(np.sum(time_weights**2))

    def reset(self) -> None:
        """Reset filter state."""
        self.W = np.zeros(self.n_fft // 2 + 1, dtype=np.complex128)
        self.input_buffer = np.zeros(self.n_fft)
        self.output_buffer = np.zeros(self.block_size)
        self.power_estimate = np.ones(self.n_fft // 2 + 1) * 1e-6

    def pre_train(
        self,
        far_end_signal: np.ndarray,
        near_end_signal: np.ndarray,
        iterations: int = 3,
    ) -> float:
        """Pre-train filter with known echo signal.

        This accelerates convergence by training on a short burst
        of far-end audio before live session starts.

        Args:
            far_end_signal: Reference signal (what will be played)
            near_end_signal: Captured signal (contains echo)
            iterations: Number of training passes

        Returns:
            Final ERLE in dB (higher is better)
        """
        if len(far_end_signal) < self.block_size * 2:
            logger.warning("Pre-train signal too short")
            return 0.0

        total_erle = []
        for _ in range(iterations):
            for i in range(0, len(far_end_signal) - self.block_size, self.block_size):
                far_block = far_end_signal[i : i + self.block_size]
                near_block = near_end_signal[i : i + self.block_size]

                error, echo_est = self.process(far_block, near_block)

                # Compute ERLE for this block
                echo_power = np.mean(near_block**2)
                error_power = np.mean(error**2)
                if error_power > 1e-10:
                    block_erle = 10 * np.log10(echo_power / error_power)
                    total_erle.append(block_erle)

        avg_erle = np.mean(total_erle) if total_erle else 0.0
        logger.info(f"AEC pre-training complete: ERLE={avg_erle:.1f}dB")
        return avg_erle


class DoubleTalkDetector:
    """Double-talk detection using spectral coherence and energy ratios."""

    def __init__(
        self,
        sample_rate: int = 16000,
        coherence_threshold: float = 0.65,
        energy_ratio_threshold: float = 0.5,
        hangover_frames: int = 10,
    ) -> None:
        """Initialize double-talk detector.

        Args:
            sample_rate: Audio sample rate
            coherence_threshold: Threshold for coherence-based detection
            energy_ratio_threshold: Threshold for energy ratio detection
            hangover_frames: Number of frames to maintain detection after trigger
        """
        self.sample_rate = sample_rate
        self.coherence_threshold = coherence_threshold
        self.energy_ratio_threshold = energy_ratio_threshold
        self.hangover_frames = hangover_frames

        self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate)

        # Ring buffers for history
        self.far_end_history: deque[np.ndarray] = deque(maxlen=4)
        self.near_end_history: deque[np.ndarray] = deque(maxlen=4)

        # State
        self.hangover_counter = 0
        self.is_double_talk = False

        # Energy tracking
        self.far_end_energy = 1e-10
        self.near_end_energy = 1e-10
        self.error_energy = 1e-10

        # Smoothing factor
        self.energy_alpha = 0.95

    def update(
        self,
        far_end: np.ndarray,
        near_end: np.ndarray,
        error_signal: np.ndarray,
    ) -> bool:
        """Update double-talk detection.

        Args:
            far_end: Far-end (speaker) signal
            near_end: Near-end (microphone) signal
            error_signal: AEC error signal

        Returns:
            True if double-talk is detected
        """
        # Update energy estimates (exponential moving average)
        self.far_end_energy = self.energy_alpha * self.far_end_energy + (
            1 - self.energy_alpha
        ) * np.mean(far_end**2)
        self.near_end_energy = self.energy_alpha * self.near_end_energy + (
            1 - self.energy_alpha
        ) * np.mean(near_end**2)
        self.error_energy = self.energy_alpha * self.error_energy + (
            1 - self.energy_alpha
        ) * np.mean(error_signal**2)

        # Method 1: Energy ratio test
        # If near-end has much more energy than far-end, it's near-end speech
        energy_ratio = self.near_end_energy / (self.far_end_energy + 1e-10)
        energy_test = energy_ratio > (1.0 + self.energy_ratio_threshold)

        # Method 2: Residual energy test
        # If error is close to near-end, echo is not well-cancelled
        if self.near_end_energy > 1e-6:
            residual_ratio = self.error_energy / self.near_end_energy
            residual_test = residual_ratio > 0.8
        else:
            residual_test = False

        # Method 3: Spectral coherence (occasional check)
        coherence_test = False
        if len(self.far_end_history) >= 3:
            # Check coherence every few frames for efficiency
            coherence = self.spectral_analyzer.compute_coherence(
                far_end, near_end, n_frames=3
            )
            # Low coherence suggests different signals (double-talk)
            coherence_test = coherence < self.coherence_threshold

        # Combine tests
        double_talk_now = energy_test or residual_test or coherence_test

        # Apply hangover
        if double_talk_now:
            self.hangover_counter = self.hangover_frames
            self.is_double_talk = True
        elif self.hangover_counter > 0:
            self.hangover_counter -= 1
            self.is_double_talk = self.hangover_counter > 0
        else:
            self.is_double_talk = False

        # Update history
        self.far_end_history.append(far_end.copy())
        self.near_end_history.append(near_end.copy())

        return self.is_double_talk

    def reset(self) -> None:
        """Reset detector state."""
        self.far_end_history.clear()
        self.near_end_history.clear()
        self.hangover_counter = 0
        self.is_double_talk = False
        self.far_end_energy = 1e-10
        self.near_end_energy = 1e-10
        self.error_energy = 1e-10


class DelayEstimator:
    """Adaptive delay estimation using GCC-PHAT."""

    def __init__(
        self,
        sample_rate: int = 16000,
        max_delay_ms: float = 200.0,
        update_interval_ms: float = 500.0,
        smoothing_factor: float = 0.9,
    ) -> None:
        """Initialize delay estimator.

        Args:
            sample_rate: Audio sample rate
            max_delay_ms: Maximum expected delay in milliseconds
            update_interval_ms: How often to update estimate
            smoothing_factor: Exponential smoothing factor
        """
        self.sample_rate = sample_rate
        self.max_delay_samples = int(max_delay_ms * sample_rate / 1000)
        self.update_interval_samples = int(update_interval_ms * sample_rate / 1000)
        self.smoothing_factor = smoothing_factor

        # Buffers for delay estimation
        self.far_end_buffer: deque[np.ndarray] = deque()
        self.near_end_buffer: deque[np.ndarray] = deque()
        self.buffer_samples = 0

        # Current estimate
        self.estimated_delay_samples = 0
        self.estimated_delay_ms = 0.0
        self.confidence = 0.0

        # Samples since last update
        self.samples_since_update = 0

    def process(
        self, far_end_chunk: np.ndarray, near_end_chunk: np.ndarray
    ) -> tuple[int, float]:
        """Process audio chunks and update delay estimate.

        Args:
            far_end_chunk: Far-end audio chunk
            near_end_chunk: Near-end audio chunk

        Returns:
            Tuple of (delay_samples, confidence)
        """
        # Add to buffers
        self.far_end_buffer.append(far_end_chunk.copy())
        self.near_end_buffer.append(near_end_chunk.copy())
        self.buffer_samples += len(far_end_chunk)
        self.samples_since_update += len(far_end_chunk)

        # Check if it's time to update
        if self.samples_since_update >= self.update_interval_samples:
            # Concatenate buffers
            far_end_signal = np.concatenate(list(self.far_end_buffer))
            near_end_signal = np.concatenate(list(self.near_end_buffer))

            # Limit size for processing efficiency
            max_size = self.max_delay_samples * 4
            if len(far_end_signal) > max_size:
                far_end_signal = far_end_signal[-max_size:]
                near_end_signal = near_end_signal[-max_size:]

            # Estimate delay using GCC-PHAT
            delay, confidence = gcc_phat(
                far_end_signal,
                near_end_signal,
                sample_rate=self.sample_rate,
                max_delay=self.max_delay_samples,
            )

            # Apply smoothing if confidence is good
            if confidence > 0.3:
                smoothed_delay = int(
                    self.smoothing_factor * self.estimated_delay_samples
                    + (1 - self.smoothing_factor) * delay
                )
                self.estimated_delay_samples = smoothed_delay
                self.estimated_delay_ms = smoothed_delay * 1000.0 / self.sample_rate
                self.confidence = confidence

            # Clear buffers
            self.far_end_buffer.clear()
            self.near_end_buffer.clear()
            self.buffer_samples = 0
            self.samples_since_update = 0

        return self.estimated_delay_samples, self.confidence

    def get_delay_compensated_far_end(self, far_end_chunk: np.ndarray) -> np.ndarray:
        """Get far-end signal delayed to align with near-end.

        Args:
            far_end_chunk: Current far-end chunk

        Returns:
            Delayed far-end signal for AEC processing
        """
        # This would typically use a ring buffer for real implementation
        # For now, return as-is (actual delay compensation happens in main AEC)
        return far_end_chunk

    def reset(self) -> None:
        """Reset estimator state."""
        self.far_end_buffer.clear()
        self.near_end_buffer.clear()
        self.buffer_samples = 0
        self.samples_since_update = 0
        self.estimated_delay_samples = 0
        self.estimated_delay_ms = 0.0
        self.confidence = 0.0


class DynamicAEC:
    """Dynamic Acoustic Echo Cancellation system.

    Replaces the fixed-delay LeakageDetector with adaptive echo cancellation:
    - GCC-PHAT delay estimation (adaptive, not fixed 50ms)
    - Frequency-domain NLMS adaptive filtering
    - Double-talk detection via spectral coherence
    - ERLE (Echo Return Loss Enhancement) computation
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_size: int = 256,
        filter_length_ms: float = 100.0,
        step_size: float = 0.5,
        convergence_threshold_db: float = 15.0,
    ) -> None:
        """Initialize Dynamic AEC system.

        Args:
            sample_rate: Audio sample rate in Hz
            frame_size: Processing frame size in samples
            filter_length_ms: Adaptive filter length in milliseconds
            step_size: NLMS step size (learning rate)
            convergence_threshold_db: ERLE threshold for convergence
        """
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.convergence_threshold_db = convergence_threshold_db

        # Calculate filter length in samples - use frame_size as block size
        # for efficient processing, filter models the echo tail
        filter_length = int(filter_length_ms * sample_rate / 1000)
        # Round to nearest power of 2 for efficiency, but ensure at least frame_size
        filter_length = 2 ** int(np.ceil(np.log2(max(filter_length, frame_size * 2))))
        filter_length = max(filter_length, 512)  # Minimum 512 samples

        # Initialize components
        self.adaptive_filter = FrequencyDomainNLMS(
            filter_length=filter_length,
            step_size=step_size,
            regularization=1e-4,
            leakage=0.999,
        )

        self.delay_estimator = DelayEstimator(
            sample_rate=sample_rate,
            max_delay_ms=200.0,
            update_interval_ms=500.0,
            smoothing_factor=0.9,
        )

        self.double_talk_detector = DoubleTalkDetector(
            sample_rate=sample_rate,
            coherence_threshold=0.65,
            energy_ratio_threshold=0.5,
            hangover_frames=10,
        )

        self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate, n_fft=512)

        # Frame accumulation for block processing
        self.block_size = filter_length  # Process in filter-length blocks

        # Ring buffers for delay compensation
        self.far_end_ring_buffer: deque[np.ndarray] = deque(maxlen=20)
        self.accumulated_far_end = BoundedBuffer(
            max_samples=sample_rate * 5
        )  # 5s limit

        self.near_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.far_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.accumulated_samples = 0

        # State
        self.state = AECState()
        self.erle_history: deque[float] = deque(maxlen=50)

        # Convergence tracking
        self.convergence_frame_count = 0
        self.convergence_frames_needed = 100  # Need 100 frames above threshold

        logger.info(
            f"DynamicAEC initialized: sample_rate={sample_rate}, "
            f"filter_length={filter_length}, frame_size={frame_size}, "
            f"block_size={self.block_size}"
        )

    def process_frame(
        self,
        near_end: np.ndarray,  # Microphone input
        far_end: np.ndarray,  # Speaker output (reference)
    ) -> tuple[np.ndarray, AECState]:
        """Process one frame of audio through AEC.

        Args:
            near_end: Near-end signal (microphone) - shape (frame_size,)
            far_end: Far-end signal (speaker reference) - shape (frame_size,)

        Returns:
            Tuple of (cleaned_audio, aec_state)
        """
        # Ensure correct length
        near_end = np.asarray(near_end).flatten()[: self.frame_size]
        far_end = np.asarray(far_end).flatten()[: self.frame_size]

        # Convert to float for processing
        near_end_float = near_end.astype(np.float64) / 32768.0
        far_end_float = far_end.astype(np.float64) / 32768.0

        # Update delay estimation (using smaller chunks)
        delay_samples, delay_confidence = self.delay_estimator.process(
            far_end_float, near_end_float
        )

        # Store far-end in ring buffer for delay compensation
        self.far_end_ring_buffer.append(far_end_float.copy())

        # Accumulate frames for block processing
        self.near_end_accumulator.append(near_end_float.copy())
        self.far_end_accumulator.append(far_end_float.copy())
        self.accumulated_samples = len(self.near_end_accumulator)

        # Process when we have enough samples for a block
        if self.accumulated_samples >= self.block_size:
            # Pop exactly block_size samples
            near_block = self.near_end_accumulator.pop_left(self.block_size)
            far_block = self.far_end_accumulator.pop_left(self.block_size)

            # Get delay-compensated far-end signal
            delay_frames = (
                self.delay_estimator.estimated_delay_samples // self.frame_size
            )
            compensated_far_end = self._get_delayed_block(far_block, delay_frames)

            # Process through adaptive filter
            error_signal, estimated_echo = self.adaptive_filter.process(
                compensated_far_end, near_block
            )

            # Update double-talk detection (use last frame of block)
            is_double_talk = self.double_talk_detector.update(
                compensated_far_end[-self.frame_size :],
                near_block[-self.frame_size :],
                error_signal[-self.frame_size :],
            )

            # Compute ERLE for the block
            current_erle = erle(
                near_block, error_signal, frame_size=self.block_size // 4
            )
            self.erle_history.append(current_erle)

            # Update convergence status
            self._update_convergence(current_erle)

            # Update state
            self.state.erle_db = current_erle
            self.state.estimated_delay_ms = self.delay_estimator.estimated_delay_ms
            self.state.double_talk_detected = is_double_talk
            self.state.filter_tap_energy = self.adaptive_filter.get_filter_energy()

            # Get the last frame_size samples of error for output
            output_error = error_signal[-self.frame_size :]

            # Update accumulated_samples after popping
            self.accumulated_samples = len(self.near_end_accumulator)
        else:
            # Not enough samples yet - return near-end as-is with reduced gain
            output_error = near_end_float * 0.9  # Slight attenuation while buffering

        self.state.frames_processed += 1

        # Convert back to int16
        output_error = np.clip(output_error, -1.0, 1.0)
        cleaned_audio = (output_error * 32767.0).astype(np.int16)

        return cleaned_audio, self.state

    def _get_delayed_block(
        self, current_block: np.ndarray, delay_frames: int
    ) -> np.ndarray:
        """Get far-end block delayed by specified number of frames.

        Args:
            current_block: Current far-end block being processed
            delay_frames: Number of frames to delay

        Returns:
            Delayed far-end block
        """
        buffer_len = len(self.far_end_ring_buffer)

        if buffer_len == 0 or delay_frames == 0:
            return current_block

        # Reconstruct delayed block from ring buffer
        result = np.zeros(self.block_size)
        samples_needed = self.block_size
        result_idx = 0

        # Get frames from history, starting with oldest needed
        for i in range(delay_frames + 1):
            idx = buffer_len - 1 - delay_frames + i
            if 0 <= idx < buffer_len:
                frame = self.far_end_ring_buffer[idx]
                samples_to_copy = min(len(frame), samples_needed - result_idx)
                result[result_idx : result_idx + samples_to_copy] = frame[
                    :samples_to_copy
                ]
                result_idx += samples_to_copy
                if result_idx >= samples_needed:
                    break

        # If we didn't fill the block, use current block for remaining samples
        if result_idx < samples_needed:
            remaining = samples_needed - result_idx
            result[result_idx:] = current_block[:remaining]

        return result

    def _update_convergence(self, current_erle: float) -> None:
        """Update convergence status based on ERLE history.

        Args:
            current_erle: Current frame's ERLE value
        """
        # Check if current ERLE is above threshold
        if current_erle > self.convergence_threshold_db:
            self.convergence_frame_count += 1
        else:
            self.convergence_frame_count = max(0, self.convergence_frame_count - 2)

        # Calculate progress
        progress = min(
            1.0, self.convergence_frame_count / self.convergence_frames_needed
        )
        self.state.convergence_progress = progress

        # Mark as converged when sustained
        if progress >= 1.0:
            self.state.converged = True

    def is_user_speaking(self, mic_audio_chunk: np.ndarray) -> bool:
        """Determine if microphone audio is user speech or echo.

        Improvement #3 (Qodo): During AEC warm-up (unconverged), instead
        of blindly returning True (which leaks early echo), we use a fast
        far-end / mic energy coherence heuristic to distinguish echo from
        real speech even before the adaptive filter has converged.

        Args:
            mic_audio_chunk: Microphone audio chunk

        Returns:
            True if user is likely speaking, False if likely echo
        """
        # During double-talk, user is definitely speaking
        if self.state.double_talk_detected:
            return True

        # Post-convergence: use ERLE as primary indicator
        if self.state.converged:
            # High ERLE → echo well-cancelled → NOT user speech
            if self.state.erle_db >= 6.0:
                return False
            return True

        # === Warm-up heuristic (Improvement #3) ===
        # During unconverged state, use energy coherence:
        # If far-end is active and mic energy is similar in magnitude
        # and double_talk not flagged → likely echo, not user speech.
        mic_energy = float(np.mean(mic_audio_chunk.astype(np.float64) ** 2))
        far_energy = self.double_talk_detector.far_end_energy

        if far_energy > 1e-6:
            # High far-end energy + mic energy in the same ballpark → echo
            energy_ratio = mic_energy / (far_energy + 1e-10)
            if 0.05 < energy_ratio < 5.0:
                # Coherent → assume echo during warm-up
                return False

        # Low far-end or very different energies → unknown, assume user
        return True

    def get_state(self) -> AECState:
        """Get current AEC state."""
        return self.state

    def reset(self) -> None:
        """Reset AEC system."""
        self.adaptive_filter.reset()
        self.delay_estimator.reset()
        self.double_talk_detector.reset()
        self.spectral_analyzer.reset()
        self.far_end_ring_buffer.clear()
        self.accumulated_far_end = BoundedBuffer(max_samples=self.sample_rate * 5)
        self.near_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.far_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
        self.accumulated_samples = 0
        self.state = AECState()
        self.erle_history.clear()
        self.convergence_frame_count = 0
        logger.info("DynamicAEC reset")

    def capture_far_end(self, ai_audio_chunk: np.ndarray | bytes) -> None:
        """Capture far-end (AI/speaker) audio for reference.

        This should be called with the audio being sent to speakers.

        Args:
            ai_audio_chunk: Audio chunk being played to speakers
        """
        if isinstance(ai_audio_chunk, bytes):
            pcm = np.frombuffer(ai_audio_chunk, dtype=np.int16)
        else:
            pcm = ai_audio_chunk

        # Avoid processing pure silence
        if len(pcm) > 0 and np.max(np.abs(pcm)) >= 10:
            # Accumulate in buffer for frame-wise processing
            self.accumulated_far_end.append(pcm.astype(np.float64) / 32768.0)

            # Process in frame_size chunks
            while len(self.accumulated_far_end) >= self.frame_size:
                frame = self.accumulated_far_end.pop_left(self.frame_size)
                self.far_end_ring_buffer.append(frame)
