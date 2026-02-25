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


def energy_vad(
    pcm_chunk: NDArray[np.int16],
    threshold: float = 0.02,
) -> VADResult:
    """
    RMS energy-based Voice Activity Detection.

    This is a *local* VAD used for UI reactivity (waveform display,
    LED indicators). Gemini has its own server-side VAD for turn
    detection; we do NOT rely on this for conversation flow.

    Args:
        pcm_chunk: Raw PCM int16 audio samples.
        threshold: RMS energy threshold (0.0–1.0 normalized).

    Returns:
        VADResult with speech flag, energy level, and sample count.
    """
    # ── Rust (Synapse) dispatch ──
    if _RUST_BACKEND:
        result = aether_cortex.energy_vad(pcm_chunk, threshold)
        return VADResult(
            is_speech=result["is_speech"],
            energy_rms=float(result["energy_rms"]),
            sample_count=int(result["sample_count"]),
        )

    # ── NumPy fallback ──
    if len(pcm_chunk) == 0:
        return VADResult(is_speech=False, energy_rms=0.0, sample_count=0)

    normalized = pcm_chunk.astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(normalized ** 2)))

    return VADResult(
        is_speech=rms > threshold,
        energy_rms=rms,
        sample_count=len(pcm_chunk),
    )
