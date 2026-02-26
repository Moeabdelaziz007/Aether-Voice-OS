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

import numpy as np
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
            # Local release build
            os.path.join(base_dir, "aether-cortex", "target", "release", "libaether_cortex.dylib"),
            # Local debug build
            os.path.join(base_dir, "aether-cortex", "target", "debug", "libaether_cortex.dylib"),
        ]
        
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
    print(f"🧬 Aether Brain: Synapse Layer (Rust) Active at {getattr(aether_cortex, '__file__', 'compiled')}")
    _RUST_BACKEND = True
    _BACKEND_NAME = f"aether-cortex v{aether_cortex.__version__} (Rust)"
    logger.info("⚡ Neural DSP backend: %s", _BACKEND_NAME)
else:
    print("⚠️ Aether Brain: Falling back to Neural Simulation (NumPy)")
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
    """
    Pre-allocated circular buffer for PCM int16 audio.

    O(1) writes, O(n) reads (memcpy). Fixed memory footprint.
    Used for windowed analysis without the O(n²) cost of
    np.concatenate on every chunk.
    """

    def __init__(self, capacity_samples: int) -> None:
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
        return self._capacity

    def write(self, data: NDArray[np.int16]) -> None:
        """
        Append samples to the ring buffer.

        If data exceeds remaining capacity, the oldest samples
        are overwritten (circular behavior).
        """
        n = len(data)
        if n == 0:
            return

        if n >= self._capacity:
            # Data larger than buffer — keep only the last `capacity` samples
            self._buf[:] = data[-self._capacity:]
            self._write_pos = 0
            self._count = self._capacity
            return

        # How many fit before wrapping?
        space_before_wrap = self._capacity - self._write_pos
        if n <= space_before_wrap:
            self._buf[self._write_pos:self._write_pos + n] = data
        else:
            # Wrap around
            self._buf[self._write_pos:] = data[:space_before_wrap]
            self._buf[:n - space_before_wrap] = data[space_before_wrap:]

        self._write_pos = (self._write_pos + n) % self._capacity
        self._count = min(self._count + n, self._capacity)

    def read_last(self, n: int) -> NDArray[np.int16]:
        """
        Read the last `n` samples from the buffer (newest data).

        Returns a contiguous copy (safe to use after further writes).
        """
        n = min(n, self._count)
        if n == 0:
            return np.array([], dtype=np.int16)

        start = (self._write_pos - n) % self._capacity
        if start + n <= self._capacity:
            return self._buf[start:start + n].copy()
        else:
            # Wraps around
            tail = self._buf[start:]
            head = self._buf[:n - len(tail)]
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
    """
    Find the nearest zero-crossing point for click-free audio cuts.

    Used during barge-in to find the cleanest point to cut
    the outgoing audio, avoiding audible pops/clicks.

    Returns the sample index of the first zero-crossing found,
    or len(pcm_data) if none found within the lookahead window.
    """
    # ── Rust (Axon) dispatch ──
    if _RUST_BACKEND:
        return aether_cortex.find_zero_crossing(
            pcm_data, sample_rate, max_lookahead_ms
        )

    # ── NumPy fallback ──
    if len(pcm_data) < 2:
        return len(pcm_data)

    audio = pcm_data.astype(np.float32)
    lookahead = int(sample_rate * max_lookahead_ms / 1000)
    limit = min(len(audio) - 1, lookahead)

    signs = np.sign(audio[:limit + 1])
    crossings = np.where(signs[:-1] * signs[1:] <= 0)[0]

    if len(crossings) > 0:
        return int(crossings[0]) + 1

    return len(pcm_data)


@dataclass(frozen=True)
class HyperVADResult:
    """Refined VAD result with dual-threshold triggers."""
    is_soft: bool   # User is breathing/thinking (Backchannel trigger)
    is_hard: bool   # User is speaking clearly (Interrupt/Vision trigger)
    energy_rms: float
    sample_count: int


class AdaptiveVAD:
    """
    HyperVAD: Tracks environmental noise statistics (mu, sigma) 
    to dynamically calculate Soft and Hard thresholds.
    """

    def __init__(
        self, 
        window_size_sec: float = 5.0, 
        sample_rate: int = 16_000,
        min_threshold: float = 0.01,
        max_threshold: float = 0.2,
    ) -> None:
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        
        # Track energy history for statistical noise floor estimation
        self._history_size = int(window_size_sec / 0.1) # 100ms blocks
        self._history: list[float] = []
        self._mu = min_threshold
        self._sigma = 0.001

    def update(self, current_rms: float) -> tuple[float, float]:
        """
        Update noise statistics and return (soft_threshold, hard_threshold).
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
        return {"mu": self._mu, "sigma": self._sigma}


from enum import Enum

class SilenceType(Enum):
    VOID = "void"           # Absolute silence, no human presence
    BREATHING = "breathing" # Oscillatory micro-RMS, likely user thinking
    THINKING = "thinking"   # Sustained low-RMS, indicates cognitive load


class SilentAnalyzer:
    """
    Analyzes silence periods to detect human cognitive presence.
    Uses Zero-Crossing Rate (ZCR) and RMS variance to find 'breathing' patterns.
    """
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._history_rms: list[float] = []
        self._history_zcr: list[float] = []
        self._window_size = 20 # 2 seconds at 100ms chunks

    def classify(self, pcm_chunk: NDArray[np.int16], current_rms: float) -> SilenceType:
        """Classify the type of silence in the current chunk."""
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
    """
    RMS energy-based Voice Activity Detection with Hyper-Singularity Logic.

    Args:
        pcm_chunk: Raw PCM int16 audio samples.
        threshold: RMS energy threshold (used if adaptive_engine is None).
        adaptive_engine: Optional AdaptiveVAD instance for dynamic thresholding.

    Returns:
        HyperVADResult with dual-trigger flags, energy level, and sample count.
    """
    # ── Rust (Synapse) dispatch ──
    # Note: Rust backend currently returns a dict. We adapt it.
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
            is_soft = is_hard # No soft distinction without adaptive engine
            
        return HyperVADResult(
            is_soft=is_soft,
            is_hard=is_hard,
            energy_rms=energy_rms,
            sample_count=int(result["sample_count"]),
        )

    # ── NumPy fallback ──
    if len(pcm_chunk) == 0:
        return HyperVADResult(is_soft=False, is_hard=False, energy_rms=0.0, sample_count=0)

    normalized = pcm_chunk.astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(normalized ** 2)))
    
    is_soft = False
    is_hard = False
    
    if adaptive_engine:
        soft_thr, hard_thr = adaptive_engine.update(rms)
        is_soft = rms > soft_thr
        is_hard = rms > hard_thr
    else:
        is_hard = rms > threshold
        is_soft = is_hard

    return HyperVADResult(
        is_soft=is_soft,
        is_hard=is_hard,
        energy_rms=rms,
        sample_count=len(pcm_chunk),
    )
