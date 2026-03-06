import collections
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger("AetherOS.JitterBuffer")

# ==========================================
# 🌌 Adaptive Jitter Buffer
# Squeezing every millisecond of latency
# while maintaining stream continuity.
# ==========================================


class AudioJitterBuffer:
    """
    Circular Jitter Buffer for PCM audio.
    Balances the trade-off between playback smoothness
    and the sub-200ms latency requirement.
    """

    def __init__(
        self, capacity_ms: int = 500, nominal_ms: int = 100, packet_size_ms: int = 20
    ):
        self.packet_size_ms = packet_size_ms
        self.capacity = int(capacity_ms / packet_size_ms)
        self.nominal = int(nominal_ms / packet_size_ms)

        self._buffer = collections.deque(maxlen=self.capacity)
        self._is_buffering = True  # Start in buffering state

    def push(self, pcm_chunk: bytes):
        """Add a new PCM packet to the queue."""
        self._buffer.append(pcm_chunk)

        # If we reached nominal depth, we can start popping
        if len(self._buffer) >= self.nominal:
            self._is_buffering = False

    def pop(self) -> Optional[bytes]:
        """Fetch the next packet for playback/processing."""
        if self._is_buffering:
            return None

        if not self._buffer:
            # Buffer starvation (Underrun)
            self._is_buffering = True  # Re-enter buffering state
            logger.debug("[JitterBuffer] 🔴 Underflow. Re-buffering...")
            return None

        return self._buffer.popleft()

    def flush(self):
        """Clear the buffer (e.g. on Barge-in)."""
        self._buffer.clear()
        self._is_buffering = True
        logger.debug("[JitterBuffer] 🌪 Buffer Flushed.")

    @property
    def level(self) -> int:
        """Current depth in packets."""
        return len(self._buffer)

    @property
    def latency_ms(self) -> int:
        """Current estimated latency contributed by the buffer."""
        return len(self._buffer) * self.packet_size_ms


class AdaptiveJitterBuffer:
    def __init__(
        self,
        target_latency_ms: float = 60.0,
        max_latency_ms: float = 200.0,
        sample_rate: int = 16000,
    ) -> None:
        self.sample_rate = sample_rate
        self.target_samples = int(target_latency_ms * sample_rate / 1000)
        self.max_samples = int(max_latency_ms * sample_rate / 1000)
        self._buffer = np.zeros(0, dtype=np.int16)

    def write(self, pcm: np.ndarray) -> None:
        if pcm.size == 0:
            return
        chunk = np.asarray(pcm, dtype=np.int16).ravel()
        self._buffer = np.concatenate([self._buffer, chunk])
        if self._buffer.size > self.max_samples:
            self._buffer = self._buffer[-self.max_samples :]

    def read(self, samples: int) -> np.ndarray:
        if samples <= 0:
            return np.zeros(0, dtype=np.int16)
        if self._buffer.size < samples:
            out = np.zeros(samples, dtype=np.int16)
            take = min(self._buffer.size, samples)
            if take:
                out[:take] = self._buffer[:take]
                self._buffer = self._buffer[take:]
            return out
        out = self._buffer[:samples].copy()
        self._buffer = self._buffer[samples:]
        return out
