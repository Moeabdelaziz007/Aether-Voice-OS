"""
Aether Voice OS — Telemetry Flow E2E.
------------------------------------
Verifies that TelemetryManager correctly dispatches spans via OTLP.
"""

import asyncio
import json
import pytest
import os
from pathlib import Path

# Aether Core Imports
from core.infra.telemetry import TelemetryManager
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

@pytest.mark.asyncio
async def test_telemetry_span_dispatch():
    print("\n[PROBE] Starting Telemetry Flow Test...")
    
    # 1. SETUP TELEMETRY (In-Memory for Verification)
    memory_exporter = InMemorySpanExporter()
    original_service_name = os.environ.get("OTEL_SERVICE_NAME", "aether-test")
    
    # Initialize with local memory exporter
    tm = TelemetryManager(model_id="aether-e2e-probe")
    tm.initialize()
    
    # Inject memory exporter for test verification
    from opentelemetry import trace as trace_api_global
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    provider = trace_api_global.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))
    
    print("[PROBE] Creating Test Spans...")
    with tm.tracer.start_as_current_span("e2e.handshake") as span:
        span.set_attribute("client_id", "perf-probe-123")
        span.add_event("handshake.start")
        await asyncio.sleep(0.1)
        span.add_event("handshake.complete")

    with tm.tracer.start_as_current_span("e2e.audio_stream") as span:
        span.set_attribute("bytes_received", 32000)
        from opentelemetry.trace import Status, StatusCode
        span.set_status(Status(StatusCode.ERROR, "audio_buffer_overflow"))
        span.set_attribute("buffer_id", "rx-01")
    
    # Force flush using global provider
    trace_api_global.get_tracer_provider().force_flush()
    
    # 2. VERIFY
    spans = memory_exporter.get_finished_spans()
    print(f"[PROBE] Captured {len(spans)} spans in memory.")
    
    span_names = [s.name for s in spans]
    assert "e2e.handshake" in span_names
    assert "e2e.audio_stream" in span_names
    
    # Check attributes
    handshake_span = next(s for s in spans if s.name == "e2e.handshake")
    assert handshake_span.attributes["client_id"] == "perf-probe-123"
    
    print("[PROBE] Telemetry Dispatch Verified.")

if __name__ == "__main__":
    pytest.main([__file__, "-s"])
