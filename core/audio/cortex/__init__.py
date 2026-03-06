import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    # Attempt to import the compiled Rust module
    from .aether_cortex import (
        CochlearBuffer as RustCochlearBuffer,
    )
    from .aether_cortex import (
        energy_vad as rust_energy_vad,
    )
    from .aether_cortex import (
        find_zero_crossing as rust_find_zero_crossing,
    )
    from .aether_cortex import (
        spectral_denoise as rust_spectral_denoise,
    )

    HAS_RUST_CORTEX = True
    logger.info("✦ Aether Cortex: Rust acceleration ARMED.")
except ImportError as e:
    HAS_RUST_CORTEX = False
    logger.warning(
        f"✧ Aether Cortex: Rust acceleration not found ({e}). "
        "Falling back to NumPy (Performance degraded)."
    )
    import traceback
    logger.debug(traceback.format_exc())


class CochlearBuffer:
    """Python wrapper for Rust CochlearBuffer (ring buffer)."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.use_rust = HAS_RUST_CORTEX
        if HAS_RUST_CORTEX:
            self._rust_buf = RustCochlearBuffer(capacity)
        else:
            # Fallback to simple numpy ring buffer
            self._buf = np.zeros(capacity, dtype=np.int16)
            self._write_pos = 0
            self._count = 0

    def write(self, data: np.ndarray) -> None:
        """Write PCM samples to the buffer."""
        if self.use_rust:
            self._rust_buf.write(data.tolist())
        else:
            data = np.asarray(data, dtype=np.int16)
            n = len(data)
            if n >= self.capacity:
                self._buf[:] = data[-self.capacity :]
                self._write_pos = 0
                self._count = self.capacity
            else:
                for i, s in enumerate(data):
                    pos = (self._write_pos + i) % self.capacity
                    self._buf[pos] = s
                self._write_pos = (self._write_pos + n) % self.capacity
                self._count = min(self._count + n, self.capacity)

    def read_last(self, n: int) -> np.ndarray:
        """Read the last n samples."""
        if self.use_rust:
            return np.array(self._rust_buf.read_last(n), dtype=np.int16)
        else:
            n = min(n, self._count)
            if n == 0:
                return np.array([], dtype=np.int16)
            start = (self._write_pos - n) % self.capacity
            if start + n <= self.capacity:
                return self._buf[start : start + n].copy()
            else:
                return np.concatenate(
                    [self._buf[start:], self._buf[: n - (self.capacity - start)]]
                )

    def clear(self) -> None:
        """Clear the buffer."""
        if self.use_rust:
            self._rust_buf.clear()
        else:
            self._write_pos = 0
            self._count = 0

    @property
    def count(self) -> int:
        """Number of samples in buffer."""
        if self.use_rust:
            return self._rust_buf.count()
        return self._count


def energy_vad(audio: np.ndarray, threshold: float = 0.01) -> bool:
    """Rust-accelerated energy VAD."""
    if HAS_RUST_CORTEX:
        return rust_energy_vad(audio, threshold)
    # Fallback to numpy
    energy = np.sqrt(np.mean(audio**2))
    return energy > threshold


def find_zero_crossing(audio: np.ndarray) -> int:
    """Rust-accelerated zero-crossing detection."""
    if HAS_RUST_CORTEX:
        return rust_find_zero_crossing(audio)
    # Fallback to numpy
    return np.nonzero(np.diff(np.sign(audio)))[0].shape[0]


def spectral_denoise(audio: np.ndarray, noise_floor: float = 0.02) -> dict:
    """Rust-accelerated spectral denoising.

    Returns dict with 'samples', 'noise_level', 'gate_active', 'sample_count'.
    """
    if HAS_RUST_CORTEX:
        # Rust expects int16, returns dict
        return rust_spectral_denoise(audio, noise_floor)
    # Fallback to numpy (simple gate)
    audio_int16 = np.asarray(audio, dtype=np.int16)
    energy = np.sqrt(np.mean(audio_int16.astype(np.float32) ** 2)) / 32768.0
    gate_active = energy < noise_floor
    if gate_active:
        gain = (energy / noise_floor) ** 2 if noise_floor > 0 else 0
        samples = (audio_int16.astype(np.float32) * gain).astype(np.int16)
    else:
        samples = audio_int16.copy()
    return {
        "samples": samples,
        "noise_level": float(energy),
        "gate_active": gate_active,
        "sample_count": len(audio_int16),
    }
