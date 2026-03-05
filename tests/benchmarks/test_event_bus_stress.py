import asyncio
import time
import pytest
import json
from pathlib import Path
from core.infra.event_bus import EventBus, AudioFrameEvent, ControlEvent, TelemetryEvent

@pytest.mark.asyncio
async def test_event_bus_throughput():
    """
    Expert Benchmark: Measuring multi-lane EventBus throughput and CPU overhead.
    """
    bus = EventBus()
    processed = 0
    start_ts = time.perf_counter()
    
    async def fast_cb(event):
        nonlocal processed
        processed += 1

    # Subscribe to all tiers
    bus.subscribe(AudioFrameEvent, fast_cb)
    bus.subscribe(ControlEvent, fast_cb)
    bus.subscribe(TelemetryEvent, fast_cb)
    
    await bus.start()
    
    total_events = 20000
    publish_start = time.perf_counter()
    
    # Flood the bus
    for i in range(total_events):
        ts = time.time()
        if i % 3 == 0:
            event = AudioFrameEvent(timestamp=ts, source="bench", latency_budget=100, pcm_data=b"\x00"*640, sample_rate=16000, channels=1)
        elif i % 3 == 1:
            event = ControlEvent(timestamp=ts, source="bench", latency_budget=500, command="TEST", payload={})
        else:
            event = TelemetryEvent(timestamp=ts, source="bench", latency_budget=1000, metric_name="perf", value=float(i))
        
        await bus.publish(event)
    
    # Wait for completion
    timeout = 15.0
    wait_start = time.perf_counter()
    while processed < total_events and (time.perf_counter() - wait_start) < timeout:
        await asyncio.sleep(0.01)
    
    end_ts = time.perf_counter()
    duration = end_ts - start_ts
    eps = total_events / duration
    
    await bus.stop()
    
    metrics = {
        "benchmark": "event_bus_throughput",
        "total_events": total_events,
        "processed": processed,
        "duration_seconds": round(duration, 4),
        "events_per_second": round(eps, 2),
        "status": "success" if processed == total_events else "partial_success"
    }
    
    # Save report
    report_path = Path("tests/reports/stress_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🚀 EventBus Benchmark: {eps:.2f} EPS")
    assert eps > 1000
    assert processed == total_events
