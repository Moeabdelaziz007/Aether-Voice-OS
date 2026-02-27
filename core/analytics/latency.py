import logging
from typing import List

logger = logging.getLogger(__name__)


class LatencyOptimizer:
    """
    Tracks and optimizes system latency, focusing on p50, p95, p99 metrics.
    Essential for sub-200ms real-time audio guarantees.
    """

    def __init__(self):
        self._latencies: List[float] = []

    def record_latency(self, latency_ms: float):
        self._latencies.append(latency_ms)

    def get_metrics(self) -> dict:
        if not self._latencies:
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}

        sorted_lats = sorted(self._latencies)
        count = len(sorted_lats)

        p50 = sorted_lats[int(count * 0.50)]
        p95 = sorted_lats[int(count * 0.95)]
        p99 = sorted_lats[int(count * 0.99)]
        avg = sum(sorted_lats) / count

        return {"p50": p50, "p95": p95, "p99": p99, "avg": avg, "count": count}

    def log_metrics(self):
        metrics = self.get_metrics()
        logger.info(
            f"Latency Metrics over {metrics['count']} events: "
            f"Avg={metrics['avg']:.1f}ms, P50={metrics['p50']:.1f}ms, "
            f"P95={metrics['p95']:.1f}ms, P99={metrics['p99']:.1f}ms"
        )
