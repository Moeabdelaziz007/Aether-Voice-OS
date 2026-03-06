"""
Aether Voice OS — Cost Telemetry Verification.
"""

import logging

from core.analytics.latency import LatencyOptimizer
from core.infra.telemetry import record_usage


def test_cost_recording_logic(caplog):
    """Verify that record_usage calculates and logs cost correctly."""
    caplog.set_level(logging.INFO)

    # Simulate a session with 1M prompt tokens and 1M completion tokens
    # Prices for gemini-2.0-flash: input=$0.10/1M, output=$0.40/1M
    # Expected cost = 0.10 + 0.40 = $0.50

    record_usage(
        session_id="cost-test-123",
        prompt_tokens=1_000_000,
        completion_tokens=1_000_000,
        model="gemini-2.0-flash",
    )

    # Check logs
    assert "Estimated Cost=$0.500000" in caplog.text
    assert "Session cost-test-123" in caplog.text
    assert "Prompt=1000000" in caplog.text
    assert "Completion=1000000" in caplog.text


def test_cost_recording_pro_model(caplog):
    """Verify that cost calculation adjusts for different models (Gemini 2.0 Pro)."""
    caplog.clear()
    caplog.set_level(logging.INFO)

    # gemini-2.0-pro: input=$1.25/1M, output=$5.00/1M
    # prompt=1M, completion=1M -> cost=$6.25
    record_usage(
        session_id="cost-test-pro",
        prompt_tokens=1_000_000,
        completion_tokens=1_000_000,
        model="gemini-2.0-pro",
    )

    assert "Estimated Cost=$6.250000" in caplog.text


def test_latency_sketch_memory_growth_near_constant():
    """Ensure latency telemetry remains bounded under high event volume."""
    optimizer = LatencyOptimizer(
        max_centroids=64,
        max_dimension_values=4,
        max_series=8,
        register_telemetry_flush=False,
    )

    for i in range(200_000):
        optimizer.record_latency(
            latency_ms=float((i % 250) + 1),
            session=f"session-{i % 50}",
            stage="model",
            model=f"model-{i % 20}",
            region=f"region-{i % 10}",
        )

    # Sketch and dimensional index sizes should remain bounded by config.
    assert len(optimizer._global.sketch._centroids) <= 64
    assert len(optimizer._series) <= 8
    assert len(optimizer._dimension_seen["session"]) <= 4
    assert len(optimizer._dimension_seen["model"]) <= 4
    assert len(optimizer._dimension_seen["region"]) <= 4
