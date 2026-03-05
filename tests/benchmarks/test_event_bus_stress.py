import asyncio
import time
import pytest
import json
from pathlib import Path
from core.infra.event_bus import EventBus, AudioFrameEvent, TelemetryEvent

@pytest.mark.asyncio
async def test_event_bus_lane_isolation():
    """
    Systems Lab: Validating Multi-Lane Isolation.
    Scenario: Flood the Telemetry lane with 10k events while measuring 
    latency of a single Audio frame.
    Goal: Telemetry load should NOT starve the Audio lane.
    """
    bus = EventBus()
    await bus.start()
    
    audio_processed_time = 0.0
    audio_sent_time = 0.0
    
    async def audio_cb(event):
        nonlocal audio_processed_time
        audio_processed_time = time.perf_counter()
        
    bus.subscribe(AudioFrameEvent, audio_cb)
    
    # 1. Start flooding the Telemetry lane (Tier 3)
    flood_count = 10000
    for i in range(flood_count):
        await bus.publish(TelemetryEvent(
            timestamp=time.time(),
            source="stress_bot",
            latency_budget=5000,
            metric_name="load_test",
            value=float(i)
        ))
    
    # 2. Inject a high-priority Audio frame (Tier 1) mid-flood
    audio_sent_time = time.perf_counter()
    await bus.publish(AudioFrameEvent(
        timestamp=time.time(),
        source="voice_engine",
        latency_budget=20,
        pcm_data=b"\x00"*640,
        sample_rate=16000,
        channels=1
    ))
    
    # 3. Wait for audio frame processing
    timeout = 2.0
    wait_start = time.perf_counter()
    while audio_processed_time == 0 and (time.perf_counter() - wait_start) < timeout:
        await asyncio.sleep(0.001)
        
    await bus.stop()
    
    # 4. Calculation
    audio_latency_ms = (audio_processed_time - audio_sent_time) * 1000
    
    metrics = {
        "benchmark": "event_bus_lane_isolation",
        "telemetry_flood_count": flood_count,
        "audio_latency_ms": round(audio_latency_ms, 2),
        "status": "success" if audio_latency_ms < 10 else "failed"
    }
    
    # Save report
    report_path = Path("tests/reports/stress_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🛡️  Lane Isolation: Audio latency under load: {audio_latency_ms:.2f}ms")
    # Even under massive telemetry flood, audio should be prioritized (sub-10ms)
    assert audio_latency_ms < 10
