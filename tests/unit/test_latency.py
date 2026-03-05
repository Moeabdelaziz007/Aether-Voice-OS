from core.analytics.latency import LatencyOptimizer


def test_empty_latencies():
    optimizer = LatencyOptimizer()
    metrics = optimizer.get_metrics()
    assert metrics == {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0}


def test_single_latency():
    optimizer = LatencyOptimizer()
    optimizer.record_latency(100.0)
    metrics = optimizer.get_metrics()
    assert metrics == {
        "p50": 100.0,
        "p95": 100.0,
        "p99": 100.0,
        "avg": 100.0,
        "count": 1,
    }


def test_multiple_latencies():
    optimizer = LatencyOptimizer()
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    for lat in latencies:
        optimizer.record_latency(lat)

    metrics = optimizer.get_metrics()

    assert metrics["count"] == 10
    assert metrics["avg"] == 55.0

    # Int(10 * 0.5) = 5 -> sorted_lats[5] = 60.0
    assert metrics["p50"] == 60.0
    # Int(10 * 0.95) = 9 -> sorted_lats[9] = 100.0
    assert metrics["p95"] == 100.0
    # Int(10 * 0.99) = 9 -> sorted_lats[9] = 100.0
    assert metrics["p99"] == 100.0


def test_log_metrics(caplog):
    import logging

    with caplog.at_level(logging.INFO):
        optimizer = LatencyOptimizer()
        optimizer.record_latency(50.0)
        optimizer.log_metrics()

        expected_log = (
            "Latency Metrics over 1 events: "
            "Avg=50.0ms, P50=50.0ms, P95=50.0ms, P99=50.0ms"
        )
        assert expected_log in caplog.text


def test_log_metrics_empty(caplog):
    import logging

    with caplog.at_level(logging.INFO):
        optimizer = LatencyOptimizer()
        optimizer.log_metrics()

        expected_log = (
            "Latency Metrics over 0 events: Avg=0.0ms, P50=0.0ms, P95=0.0ms, P99=0.0ms"
        )
        assert expected_log in caplog.text
