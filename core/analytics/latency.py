import bisect
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from core.infra import telemetry

logger = logging.getLogger(__name__)

DEFAULT_STAGES = ("capture", "encode", "send", "model", "receive", "playback")
_OVERFLOW_TAG = "__other__"


@dataclass
class _Centroid:
    mean: float
    weight: int = 1


class _TDigestSketch:
    """A compact t-digest-like sketch with bounded centroid count."""

    def __init__(self, max_centroids: int = 200):
        self.max_centroids = max(20, max_centroids)
        self._centroids: List[_Centroid] = []
        self.count = 0

    def add(self, value: float) -> None:
        self.count += 1
        if not self._centroids:
            self._centroids.append(_Centroid(mean=value, weight=1))
            return

        means = [c.mean for c in self._centroids]
        idx = bisect.bisect_left(means, value)

        # Merge into nearest centroid when possible to keep memory bounded.
        nearest_idx = None
        if idx == 0:
            nearest_idx = 0
        elif idx == len(self._centroids):
            nearest_idx = len(self._centroids) - 1
        else:
            left = self._centroids[idx - 1]
            right = self._centroids[idx]
            nearest_idx = (
                idx - 1 if abs(left.mean - value) <= abs(right.mean - value) else idx
            )

        nearest = self._centroids[nearest_idx]
        merge_threshold = max(2, self.count // self.max_centroids)
        if nearest.weight < merge_threshold:
            new_weight = nearest.weight + 1
            nearest.mean = ((nearest.mean * nearest.weight) + value) / new_weight
            nearest.weight = new_weight
        else:
            self._centroids.insert(idx, _Centroid(mean=value, weight=1))

        if len(self._centroids) > self.max_centroids:
            self._compress()

    def quantile(self, q: float) -> float:
        if not self._centroids:
            return 0.0
        q = min(1.0, max(0.0, q))
        target = q * self.count
        cumulative = 0
        for centroid in self._centroids:
            cumulative += centroid.weight
            if cumulative >= target:
                return centroid.mean
        return self._centroids[-1].mean

    def _compress(self) -> None:
        if len(self._centroids) <= self.max_centroids:
            return

        compressed: List[_Centroid] = []
        batch = max(2, len(self._centroids) // self.max_centroids)
        i = 0
        while i < len(self._centroids):
            chunk = self._centroids[i : i + batch]
            total_weight = sum(c.weight for c in chunk)
            weighted_mean = sum(c.mean * c.weight for c in chunk) / total_weight
            compressed.append(_Centroid(mean=weighted_mean, weight=total_weight))
            i += batch
        self._centroids = compressed[: self.max_centroids]


@dataclass
class _MetricState:
    sketch: _TDigestSketch
    total_ms: float = 0.0
    count: int = 0

    def add(self, latency_ms: float) -> None:
        self.sketch.add(latency_ms)
        self.total_ms += latency_ms
        self.count += 1

    def to_metrics(self) -> Dict[str, float]:
        if self.count == 0:
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0}
        return {
            "p50": self.sketch.quantile(0.50),
            "p95": self.sketch.quantile(0.95),
            "p99": self.sketch.quantile(0.99),
            "avg": self.total_ms / self.count,
            "count": self.count,
        }


class LatencyOptimizer:
    """Streaming latency tracker with bounded memory and dimensional tags."""

    def __init__(
        self,
        max_centroids: int = 200,
        max_dimension_values: int = 100,
        max_series: int = 1_000,
        register_telemetry_flush: bool = True,
    ):
        self._max_centroids = max_centroids
        self._max_dimension_values = max_dimension_values
        self._max_series = max_series

        self._global = _MetricState(sketch=_TDigestSketch(max_centroids=max_centroids))
        self._stage = {
            stage: _MetricState(sketch=_TDigestSketch(max_centroids=max_centroids))
            for stage in DEFAULT_STAGES
        }
        self._dimension_seen: Dict[str, set[str]] = {
            "session": set(),
            "stage": set(DEFAULT_STAGES),
            "model": set(),
            "region": set(),
        }
        self._series: Dict[Tuple[str, str, str, str], _MetricState] = {}

        if register_telemetry_flush:
            telemetry.register_flushable("latency", self.flush)

    def _normalize_tag(self, dimension: str, value: Optional[str]) -> str:
        normalized = value or "unknown"
        seen = self._dimension_seen[dimension]
        if normalized in seen:
            return normalized

        if len(seen) >= self._max_dimension_values:
            return _OVERFLOW_TAG

        seen.add(normalized)
        return normalized

    def _series_key(
        self,
        session: Optional[str],
        stage: Optional[str],
        model: Optional[str],
        region: Optional[str],
    ) -> Tuple[str, str, str, str]:
        s_session = self._normalize_tag("session", session)
        s_stage = self._normalize_tag("stage", stage)
        s_model = self._normalize_tag("model", model)
        s_region = self._normalize_tag("region", region)

        key = (s_session, s_stage, s_model, s_region)
        if key in self._series:
            return key

        overflow_key = (_OVERFLOW_TAG, _OVERFLOW_TAG, _OVERFLOW_TAG, _OVERFLOW_TAG)
        non_overflow_limit = max(1, self._max_series - 1)
        if len(self._series) >= non_overflow_limit:
            return overflow_key
        return key

    def record_latency(
        self,
        latency_ms: float,
        session: Optional[str] = None,
        stage: Optional[str] = None,
        model: Optional[str] = None,
        region: Optional[str] = None,
    ):
        if not telemetry.should_sample():
            return

        self._global.add(latency_ms)

        normalized_stage = self._normalize_tag("stage", stage)
        if normalized_stage in self._stage:
            self._stage[normalized_stage].add(latency_ms)

        key = self._series_key(session, normalized_stage, model, region)
        state = self._series.get(key)
        if state is None:
            state = _MetricState(
                sketch=_TDigestSketch(max_centroids=self._max_centroids)
            )
            self._series[key] = state
        state.add(latency_ms)

        telemetry.maybe_flush_metrics()

    def get_metrics(self) -> dict:
        metrics = self._global.to_metrics()
        metrics["stage_breakdown"] = {
            stage: state.to_metrics() for stage, state in self._stage.items()
        }
        return metrics

    def flush(self) -> Dict[str, Any]:
        snapshot = self.get_metrics()
        snapshot["active_series"] = len(self._series)
        snapshot["dimension_cardinality"] = {
            dim: len(values) for dim, values in self._dimension_seen.items()
        }

        logger.info(
            "Latency Metrics over %s events: Avg=%.1fms, P50=%.1fms, P95=%.1fms, P99=%.1fms",
            snapshot["count"],
            snapshot["avg"],
            snapshot["p50"],
            snapshot["p95"],
            snapshot["p99"],
        )
        return snapshot

    def log_metrics(self):
        self.flush()
