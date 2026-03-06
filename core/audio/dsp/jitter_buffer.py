import collections
import logging
from typing import Optional
from dataclasses import dataclass
import time

logger = logging.getLogger("AetherOS.JitterBuffer")

# ==========================================
# 🌌 Adaptive Jitter Buffer
# Squeezing every millisecond of latency
# while maintaining stream continuity.
# ==========================================

@dataclass
class JitterStats:
    target_ms: float
    current_ms: float
    underrun_count: int
    overrun_count: int
    avg_latency_ms: float

class AudioJitterBuffer:
    """
    Adaptive Circular Jitter Buffer for PCM audio.
    Balances the trade-off between playback smoothness
    and the sub-200ms latency requirement.
    Dynamically adjusts target latency based on network conditions.
    """

    def __init__(
        self, capacity_ms: int = 500, nominal_ms: int = 100, packet_size_ms: int = 20
    ):
        self.packet_size_ms = packet_size_ms
        self.capacity = int(capacity_ms / packet_size_ms)

        # Adaptive limits
        self.min_target_ms = 20.0
        self.max_target_ms = 200.0

        self.target_latency_ms = max(self.min_target_ms, min(nominal_ms, self.max_target_ms))
        self.nominal = int(self.target_latency_ms / packet_size_ms)

        self._buffer = collections.deque(maxlen=self.capacity)
        self._is_buffering = True  # Start in buffering state

        # Stats
        self._underrun_count = 0
        self._overrun_count = 0
        self._total_latency = 0.0
        self._latency_samples = 0

        # Adaptive tracking
        self._last_arrival_time = time.time()
        self._arrival_intervals = collections.deque(maxlen=50)

    def _adapt_target(self):
        """Adjust target latency based on arrival variance (jitter)."""
        if len(self._arrival_intervals) < 10:
            return

        # Calculate jitter (variance of arrival intervals)
        mean_interval = sum(self._arrival_intervals) / len(self._arrival_intervals)
        variance = sum((x - mean_interval) ** 2 for x in self._arrival_intervals) / len(self._arrival_intervals)

        # Simple heuristic: Target latency = mean interval + 3 * std_dev (jitter margin)
        std_dev = variance ** 0.5
        ideal_target = (mean_interval + 3 * std_dev) * 1000 # Convert to ms

        # Clamp between limits
        new_target = max(self.min_target_ms, min(ideal_target, self.max_target_ms))

        # Smooth the adjustment (exponential moving average)
        self.target_latency_ms = (0.9 * self.target_latency_ms) + (0.1 * new_target)
        self.nominal = max(1, int(self.target_latency_ms / self.packet_size_ms))

    def push(self, pcm_chunk: bytes):
        """Add a new PCM packet to the queue."""
        now = time.time()
        self._arrival_intervals.append(now - self._last_arrival_time)
        self._last_arrival_time = now

        self._adapt_target()

        if len(self._buffer) >= self.capacity:
            self._overrun_count += 1

        self._buffer.append(pcm_chunk)

        # Update stats
        current_latency = len(self._buffer) * self.packet_size_ms
        self._total_latency += current_latency
        self._latency_samples += 1

        # If we reached nominal depth, we can start popping
        if len(self._buffer) >= self.nominal:
            self._is_buffering = False

    def pop(self) -> Optional[bytes]:
        """Fetch the next packet for playback/processing."""
        if self._is_buffering:
            return None

        if not self._buffer:
            # Buffer starvation (Underrun)
            self._underrun_count += 1
            self._is_buffering = True  # Re-enter buffering state
            logger.debug("[JitterBuffer] 🔴 Underflow. Re-buffering...")

            # Penalize: increase target latency slightly on underrun to prevent further ones
            self.target_latency_ms = min(self.max_target_ms, self.target_latency_ms + self.packet_size_ms)
            self.nominal = int(self.target_latency_ms / self.packet_size_ms)

            return None

        return self._buffer.popleft()

    def get_stats(self) -> JitterStats:
        """Returns current jitter buffer statistics."""
        avg_lat = (self._total_latency / self._latency_samples) if self._latency_samples > 0 else 0.0
        return JitterStats(
            target_ms=self.target_latency_ms,
            current_ms=self.latency_ms,
            underrun_count=self._underrun_count,
            overrun_count=self._overrun_count,
            avg_latency_ms=avg_lat
        )

    def flush(self):
        """Clear the buffer (e.g. on Barge-in)."""
        self._buffer.clear()
        self._is_buffering = True
        # Reset adaptive state
        self._arrival_intervals.clear()
        logger.debug("[JitterBuffer] 🌪 Buffer Flushed.")

    @property
    def level(self) -> int:
        """Current depth in packets."""
        return len(self._buffer)

    @property
    def latency_ms(self) -> float:
        """Current estimated latency contributed by the buffer."""
        return len(self._buffer) * self.packet_size_ms
