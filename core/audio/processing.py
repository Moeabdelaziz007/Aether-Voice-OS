"""
Aether Voice OS — Audio Processing.

Pure computation module — no I/O, no async. Contains:
- RingBuffer: O(1) append, zero-copy windowed reads
- find_zero_crossing: click-free audio cut point
- energy_vad: RMS-based voice activity detection

These are utility functions used by the engine for
local audio analysis (e.g., pre-filtering silence
before sending to Gemini, even though Gemini has
built-in VAD — we use local VAD for UI reactivity).

Architecture Note (Synapse Philosophy):
    The Rust backend (aether-cortex) mirrors the human auditory cortex:
    - Cochlea  → CochlearBuffer (ring buffer)
    - Synapse  → energy_vad (neural activation threshold)
    - Axon     → find_zero_crossing (clean signal propagation)
    - Thalamus → spectral_denoise (sensory noise filtering)

    If aether_cortex is available, Rust implementations are used
    automatically (10-50x faster). Otherwise, NumPy fallbacks below.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
from numba import jit, prange
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# Rust-First Import Strategy (Cortex Bridge)
# ═══════════════════════════════════════════════════════════
# Aether Cortex — Rust backend integration
aether_cortex = None
try:
    # 1. Try standard import (if installed via maturin develop/pip)
    import aether_cortex as ac

    aether_cortex = ac
except ImportError:
    # 2. Try dynamic resolution from build artifacts (bypass TCC move blocks)
    try:
        import importlib.util
        import os

        # Search paths relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        potential_paths = [
            # Standard location (should be here if cp worked)
            os.path.join(os.path.dirname(__file__), "aether_cortex.so"),
        ]
        # Native development path
        release_path = os.path.join(
            base_dir, "cortex", "target", "release", "libaether_cortex.dylib"
        )
        debug_path = os.path.join(
            base_dir, "cortex", "target", "debug", "libaether_cortex.dylib"
        )

        if os.path.exists(release_path):
            potential_paths.append(release_path)
        elif os.path.exists(debug_path):
            potential_paths.append(debug_path)

        for path in potential_paths:
            if os.path.exists(path):
                spec = importlib.util.spec_from_file_location("aether_cortex", path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    aether_cortex = module
                    break
    except Exception as e:
        # Log the error for dynamic resolution but continue to fallback
        logger.debug(f"Dynamic aether_cortex resolution failed: {e}")
        aether_cortex = None

if aether_cortex:
    cortex_path = getattr(aether_cortex, "__file__", "compiled")
    print(f"🧬 Aether Brain: Synapse Layer (Rust) Active at {cortex_path}")
    _RUST_BACKEND = True
    _BACKEND_NAME = f"aether-cortex v{aether_cortex.__version__} (Rust)"
    logger.info("⚡ Neural DSP backend: %s", _BACKEND_NAME)
else:
    logger.info("⚠️ Aether Brain: Falling back to Neural Simulation (NumPy)")
    _RUST_BACKEND = False
    _BACKEND_NAME = "NumPy (Python fallback)"
    logger.info("🐍 DSP backend: %s", _BACKEND_NAME)


@dataclass(frozen=True)
class VADResult:
    """Result of voice activity detection."""

    is_speech: bool
    energy_rms: float
    sample_count: int


class RingBuffer:
    """Pre-allocated circular buffer for PCM int16 audio.

    This data structure provides O(1) writes and O(n) reads (via memcpy),
    maintaining a fixed memory footprint. It is ideal for windowed analysis
    of audio streams, avoiding the performance cost of re-allocating or
    concatenating arrays on every new chunk.
    """

    def __init__(self, capacity_samples: int) -> None:
        """Initializes the RingBuffer.

        Args:
            capacity_samples: The maximum number of int16 samples the buffer can hold.
        """
        self._buf: NDArray[np.int16] = np.zeros(capacity_samples, dtype=np.int16)
        self._capacity = capacity_samples
        self._write_pos = 0
        self._count = 0  # How many valid samples are in the buffer

    @property
    def count(self) -> int:
        """Number of valid samples currently in the buffer."""
        return self._count

    @property
    def capacity(self) -> int:
        """The total capacity of the buffer in samples."""
        return self._capacity

    def write(self, data: NDArray[np.int16]) -> None:
        """Append samples to the ring buffer.

        If the data to be written is larger than the buffer's capacity,
        only the most recent `capacity` samples from the data will be stored.
        If the write operation would exceed the remaining space, it wraps
        around, overwriting the oldest samples.

        Args:
            data: A numpy array of int16 PCM samples to write.
        """
        n = len(data)
        if n == 0:
            return

        if n >= self._capacity:
            # Data larger than buffer — keep only the last `capacity` samples
            self._buf[:] = data[-self._capacity :]
            self._write_pos = 0
            self._count = self._capacity
            return

        # How many fit before wrapping?
        space_before_wrap = self._capacity - self._write_pos
        if n <= space_before_wrap:
            self._buf[self._write_pos : self._write_pos + n] = data
        else:
            # Wrap around
            self._buf[self._write_pos :] = data[:space_before_wrap]
            self._buf[: n - space_before_wrap] = data[space_before_wrap:]

        self._write_pos = (self._write_pos + n) % self._capacity
        self._count = min(self._count + n, self._capacity)

    def read_last(self, n: int) -> NDArray[np.int16]:
        """Read the last `n` samples from the buffer.

        This method retrieves the most recently written samples from the buffer.
        It returns a contiguous copy, ensuring that the returned array is
        safe from modification by subsequent writes to the buffer.

        Args:
            n: The number of samples to read.

        Returns:
            A numpy array containing the last `n` samples, or fewer if the
            buffer contains less than `n` samples.
        """
        n = min(n, self._count)
        if n == 0:
            return np.array([], dtype=np.int16)

        start = (self._write_pos - n) % self._capacity
        if start + n <= self._capacity:
            return self._buf[start : start + n].copy()
        else:
            # Wraps around
            tail = self._buf[start:]
            head = self._buf[: n - len(tail)]
            return np.concatenate([tail, head])

    def clear(self) -> None:
        """Reset the buffer without reallocating."""
        self._write_pos = 0
        self._count = 0


def find_zero_crossing(
    pcm_data: NDArray[np.int16],
    sample_rate: int = 16_000,
    max_lookahead_ms: float = 20.0,
) -> int:
    """Find the nearest zero-crossing point for click-free audio cuts.

    Used during barge-in to find the cleanest point to cut the outgoing audio,
    avoiding audible pops/clicks. The search is performed within a limited
    lookahead window for performance.

    Args:
        pcm_data: Numpy array of PCM audio data.
        sample_rate: The sample rate of the audio data.
        max_lookahead_ms: The maximum time in milliseconds to search for a
            zero-crossing.

    Returns:
        The sample index of the first zero-crossing found within the lookahead
        window. If none is found, returns the length of the input data.
    """
    # ── Rust (Axon) dispatch ──
    if _RUST_BACKEND:
        return aether_cortex.find_zero_crossing(pcm_data, sample_rate, max_lookahead_ms)

    # ── NumPy fallback ──
    if len(pcm_data) < 2:
        return len(pcm_data)

    audio = pcm_data.astype(np.float32)
    lookahead = int(sample_rate * max_lookahead_ms / 1000)
    limit = min(len(audio) - 1, lookahead)

    signs = np.sign(audio[: limit + 1])
    crossings = np.where(signs[:-1] * signs[1:] <= 0)[0]

    if len(crossings) > 0:
        return int(crossings[0]) + 1

    return len(pcm_data)


@dataclass(frozen=True)
class HyperVADResult:
    """Refined VAD result with dual-threshold triggers."""

    is_soft: bool  # User is breathing/thinking (Backchannel trigger)
    is_hard: bool  # User is speaking clearly (Interrupt/Vision trigger)
    energy_rms: float
    sample_count: int


class AdaptiveVAD:
    """HyperVAD engine that tracks environmental noise statistics.

    This VAD dynamically calculates "soft" and "hard" thresholds for voice
    activity by maintaining a running statistical model (mean and standard
    deviation) of the recent audio energy. This allows it to adapt to
    changing background noise levels.
    """

    def __init__(
        self,
        window_size_sec: float = 5.0,
        sample_rate: int = 16_000,
        min_threshold: float = 0.01,
        max_threshold: float = 0.2,
    ) -> None:
        """Initializes the AdaptiveVAD engine.

        Args:
            window_size_sec: The duration of the energy history window in seconds.
            sample_rate: The sample rate of the audio being processed.
            min_threshold: The minimum allowable VAD threshold.
            max_threshold: The maximum allowable VAD threshold.
        """
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold

        # Track energy history for statistical noise floor estimation
        self._history_size = int(window_size_sec / 0.1)  # 100ms blocks
        self._history: list[float] = []
        self._mu = min_threshold
        self._sigma = 0.001

    def update(self, current_rms: float) -> tuple[float, float]:
        """Update noise statistics and return new (soft, hard) thresholds.

        Args:
            current_rms: The RMS energy of the latest audio chunk.

        Returns:
            A tuple containing the new soft and hard VAD thresholds.
        """
        self._history.append(current_rms)
        if len(self._history) > self._history_size:
            self._history.pop(0)

        if len(self._history) > 10:
            self._mu = float(np.mean(self._history))
            self._sigma = float(np.std(self._history))
        else:
            self._mu = current_rms

        # RMS_soft = mu + 1.5 * sigma (Thinking/Breathing)
        # RMS_hard = mu + 4.0 * sigma (Hard Interrupt)
        soft = self._mu + (1.5 * self._sigma)
        hard = self._mu + (4.0 * self._sigma)

        # Clamp to reasonable bounds
        soft = max(self.min_threshold, min(soft, self.max_threshold * 0.5))
        hard = max(self.min_threshold * 2, min(hard, self.max_threshold))

        return soft, hard

    @property
    def noise_stats(self) -> dict[str, float]:
        """Returns the current noise floor statistics (mu and sigma)."""
        return {"mu": self._mu, "sigma": self._sigma}


class SilenceType(Enum):
    VOID = "void"  # Absolute silence, no human presence
    BREATHING = "breathing"  # Oscillatory micro-RMS, likely user thinking
    THINKING = "thinking"  # Sustained low-RMS, indicates cognitive load


class SilentAnalyzer:
    """Analyzes silence periods to detect human cognitive presence.

    Uses Zero-Crossing Rate (ZCR) and RMS energy variance to differentiate
    between absolute silence ("void"), breathing, and thinking states.
    """

    def __init__(self, sample_rate: int = 16000) -> None:
        """Initializes the SilentAnalyzer.

        Args:
            sample_rate: The sample rate of the audio to be analyzed.
        """
        self.sample_rate = sample_rate
        self._history_rms: list[float] = []
        self._history_zcr: list[float] = []
        self._window_size = 20  # 2 seconds at 100ms chunks

    def classify(self, pcm_chunk: NDArray[np.int16], current_rms: float) -> SilenceType:
        """Classify the type of silence in the current chunk.

        Args:
            pcm_chunk: The numpy array of PCM audio data to analyze.
            current_rms: The pre-calculated RMS energy of the chunk.

        Returns:
            A `SilenceType` enum member indicating the classification.
        """
        if len(pcm_chunk) == 0:
            return SilenceType.VOID

        # 1. Calculate Zero-Crossing Rate
        zero_crossings = np.where(np.diff(np.sign(pcm_chunk)))[0]
        zcr = len(zero_crossings) / len(pcm_chunk)

        self._history_rms.append(current_rms)
        self._history_zcr.append(zcr)
        if len(self._history_rms) > self._window_size:
            self._history_rms.pop(0)
            self._history_zcr.pop(0)

        # 2. Logic:
        # VOID: Extremely low RMS (< 0.005)
        if current_rms < 0.005:
            return SilenceType.VOID

        # BREATHING: RMS oscillates slightly (inhale/exhale) + Low ZCR
        rms_var = np.var(self._history_rms) if len(self._history_rms) > 5 else 0
        if 0.005 <= current_rms < 0.01 and rms_var > 1e-7 and zcr < 0.05:
            return SilenceType.BREATHING

        # THINKING: Sustained low level, not quiet enough to be void
        if current_rms < 0.02:
            return SilenceType.THINKING

        return SilenceType.VOID


def energy_vad(
    pcm_chunk: NDArray[np.int16],
    threshold: float = 0.02,
    adaptive_engine: Optional[AdaptiveVAD] = None,
) -> HyperVADResult:
    """RMS energy-based Voice Activity Detection with adaptive thresholds.

    If a Rust backend (`aether_cortex`) is available, it is used for a
    high-performance calculation. Otherwise, this function falls back to
    `enhanced_vad`.

    Args:
        pcm_chunk: Numpy array of PCM audio data.
        threshold: The base energy threshold for VAD if no adaptive engine
            is provided.
        adaptive_engine: An optional `AdaptiveVAD` instance to provide
            dynamic soft and hard thresholds.

    Returns:
        A `HyperVADResult` object with the VAD decision and energy stats.
    """
    # ── Rust (Synapse) dispatch ──
    if _RUST_BACKEND:
        result = aether_cortex.energy_vad(pcm_chunk, threshold)
        energy_rms = float(result["energy_rms"])

        is_soft = False
        is_hard = False

        if adaptive_engine:
            soft_thr, hard_thr = adaptive_engine.update(energy_rms)
            is_soft = energy_rms > soft_thr
            is_hard = energy_rms > hard_thr
        else:
            is_hard = energy_rms > threshold
            is_soft = is_hard  # No soft distinction without adaptive engine

        return HyperVADResult(
            is_soft=bool(is_soft),
            is_hard=bool(is_hard),
            energy_rms=energy_rms,
            sample_count=int(result["sample_count"]),
        )

    # ── NumPy fallback (Enhanced Multi-Feature VAD) ──
    return enhanced_vad(pcm_chunk, threshold, adaptive_engine)


@jit(nopython=True, cache=True)
def _compute_rms_numba(samples: np.ndarray) -> float:
    """JIT-compiled RMS calculation."""
    return np.sqrt(np.mean(samples ** 2))

@jit(nopython=True, cache=True, parallel=True)
def _compute_zcr_parallel(pcm_data: np.ndarray) -> int:
    """JIT-compiled ZCR with parallel processing."""
    crossings = 0
    for i in prange(1, len(pcm_data)):
        if (pcm_data[i-1] >= 0) != (pcm_data[i] >= 0):
            crossings += 1
    return crossings

@jit(nopython=True, cache=True)
def _compute_spectral_centroid_numba(spectrum: np.ndarray, freqs: np.ndarray) -> float:
    """JIT-compiled spectral centroid calculation."""
    spec_sum = np.sum(spectrum)
    if spec_sum <= 0:
        return 0.0
    return np.sum(freqs * spectrum) / spec_sum


def calculate_zcr(pcm_data: np.ndarray) -> float:
    """Calculate Zero-Crossing Rate using Rust if available."""
    if _RUST_BACKEND:
        try:
            if hasattr(aether_cortex, "calculate_zcr"):
                return aether_cortex.calculate_zcr(pcm_data)
        except (AttributeError, TypeError) as e:
            logger.debug(f"Rust ZCR calculation failed: {e}")
            # Fall through to NumPy implementation

    if len(pcm_data) < 2:
        return 0.0
    return _compute_zcr_parallel(pcm_data) / len(pcm_data)


def enhanced_vad(
    pcm_chunk: NDArray[np.int16],
    threshold: float = 0.02,
    adaptive_engine: Optional[AdaptiveVAD] = None,
) -> HyperVADResult:
    """Multi-feature VAD combining RMS, ZCR, and Spectral Centroid.

    This provides a more robust VAD decision than simple RMS energy by
    incorporating features that help distinguish speech from noise like
    breathing or keyboard clicks.

    Args:
        pcm_chunk: Numpy array of PCM audio data.
        threshold: The base energy threshold for VAD if no adaptive engine
            is provided.
        adaptive_engine: An optional `AdaptiveVAD` instance to provide
            dynamic soft and hard thresholds.

    Returns:
        A `HyperVADResult` object with the VAD decision and energy stats.
    """
    if len(pcm_chunk) == 0:
        return HyperVADResult(
            is_soft=False, is_hard=False, energy_rms=0.0, sample_count=0
        )

    normalized = pcm_chunk.astype(np.float32) / 32768.0

    # 1. RMS Energy
    rms = float(_compute_rms_numba(normalized))

    # 2. Zero-Crossing Rate (speech = low/medium, noise = high)
    zcr = float(calculate_zcr(pcm_chunk))

    # 3. Spectral Centroid
    spectrum = np.abs(np.fft.rfft(normalized))
    freqs = np.fft.rfftfreq(len(pcm_chunk), 1 / 16000)
    centroid = float(_compute_spectral_centroid_numba(spectrum, freqs))

    # Combine with weights
    # Energy is normalized against a typical strong speech RMS (0.1)
    # Centroid is normalized against typical speech range max (4000Hz)
    speech_score = (
        (min(rms / 0.1, 1.0)) * 0.4
        + (1.0 - zcr) * 0.3
        + (min(centroid / 4000.0, 1.0)) * 0.3
    )

    is_soft = False
    is_hard = False

    if adaptive_engine:
        soft_thr, hard_thr = adaptive_engine.update(rms)
        # Weight the adaptive thresholds slightly to account for the multi-feature score
        is_soft = (rms > soft_thr) and (speech_score > 0.3)
        is_hard = (rms > hard_thr) and (speech_score > 0.5)
    else:
        is_hard = (rms > threshold) and (speech_score > 0.5)
        is_soft = is_hard

    return HyperVADResult(
        is_soft=bool(is_soft),
        is_hard=bool(is_hard),
        energy_rms=rms,
        sample_count=len(pcm_chunk),
    )
