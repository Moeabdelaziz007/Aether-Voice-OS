from unittest.mock import patch

from core.analytics.latency import DEFAULT_STAGES, LatencyOptimizer


def test_empty_latencies():
    optimizer = LatencyOptimizer(register_telemetry_flush=False)
    metrics = optimizer.get_metrics()
    assert metrics["p50"] == 0
    assert metrics["p95"] == 0
    assert metrics["p99"] == 0
    assert metrics["avg"] == 0
    assert metrics["count"] == 0
    assert set(metrics["stage_breakdown"].keys()) == set(DEFAULT_STAGES)


def test_single_latency():
    optimizer = LatencyOptimizer(register_telemetry_flush=False)
    optimizer.record_latency(100.0, stage="model")
    metrics = optimizer.get_metrics()
    assert metrics == {
        "p50": 100.0,
        "p95": 100.0,
        "p99": 100.0,
        "avg": 100.0,
        "count": 1,
        "stage_breakdown": {
            "capture": {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0},
            "encode": {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0},
            "send": {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0},
            "model": {
                "p50": 100.0,
                "p95": 100.0,
                "p99": 100.0,
                "avg": 100.0,
                "count": 1,
            },
            "receive": {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0},
            "playback": {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0},
        },
    }


def test_multiple_latencies():
    optimizer = LatencyOptimizer(register_telemetry_flush=False)
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    for lat in latencies:
        optimizer.record_latency(lat, stage="send")

    metrics = optimizer.get_metrics()

    assert metrics["count"] == 10
    assert metrics["avg"] == 55.0
    assert 40.0 <= metrics["p50"] <= 70.0
    assert 70.0 <= metrics["p95"] <= 100.0
    assert 70.0 <= metrics["p99"] <= 100.0
    assert metrics["stage_breakdown"]["send"]["count"] == 10


def test_log_metrics():
    optimizer = LatencyOptimizer(register_telemetry_flush=False)
    optimizer.record_latency(50.0)

    with patch("core.analytics.latency.logger.info") as mock_info:
        optimizer.log_metrics()
        mock_info.assert_called_once()


def test_tag_cardinality_overflow_is_bounded():
    optimizer = LatencyOptimizer(
        max_dimension_values=2,
        max_series=3,
        register_telemetry_flush=False,
    )

    for idx in range(10):
        optimizer.record_latency(
            latency_ms=idx + 1,
            session=f"s-{idx}",
            stage="capture",
            model=f"m-{idx}",
            region=f"r-{idx}",
        )

    snapshot = optimizer.flush()
    assert snapshot["active_series"] <= 3
    assert snapshot["dimension_cardinality"]["session"] <= 2
    assert snapshot["dimension_cardinality"]["model"] <= 2
    assert snapshot["dimension_cardinality"]["region"] <= 2
