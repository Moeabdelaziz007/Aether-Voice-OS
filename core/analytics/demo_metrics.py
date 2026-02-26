import logging
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


class DemoMetrics:
    """
    Captures high-fidelity metrics to demonstrate technical performance to judges.
    Focuses on 'Sigh-to-Intervention' latency and emotional accuracy.
    """

    def __init__(self):
        self._metrics = {
            "detection_latency": [],  # ms
            "emotion_accuracy": [],  # boolean list
            "total_interventions": 0,
        }
        self.start_times = {}

    def start_timer(self, span_id: str):
        self.start_times[span_id] = datetime.now()

    def stop_timer(self, span_id: str):
        if span_id in self.start_times:
            dt = datetime.now() - self.start_times.pop(span_id)
            latency_ms = dt.total_seconds() * 1000
            self._metrics["detection_latency"].append(latency_ms)
            self._metrics["total_interventions"] += 1

    def record_accuracy(self, was_correct: bool):
        self._metrics["emotion_accuracy"].append(1 if was_correct else 0)

    def report(self) -> dict:
        """Returns JSON report for the Dashboard."""
        latencies = self._metrics["detection_latency"]
        accuracy = self._metrics["emotion_accuracy"]

        return {
            "avg_latency_ms": float(np.mean(latencies)) if latencies else 0.0,
            "min_latency_ms": float(np.min(latencies)) if latencies else 0.0,
            "accuracy_percent": (
                (sum(accuracy) / len(accuracy) * 100) if accuracy else 100.0
            ),
            "total_interventions": self._metrics["total_interventions"],
            "timestamp": datetime.now().isoformat(),
        }
