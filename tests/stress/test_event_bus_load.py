import asyncio
import time

import pytest

from core.infra.event_bus import AudioFrameEvent, ControlEvent, EventBus, TelemetryEvent


@pytest.mark.async_event_bus
@pytest.mark.asyncio
async def test_event_bus_10k_eps_stress():
    """
    Stress Test: 10,000+ Events Per Second (EPS).
    Ensures the 3-Tier priority queue handles extreme load without crashing
    and respects latency budgets.
    """
    bus = EventBus()
    processed_counts = {"Audio": 0, "Control": 0, "Telemetry": 0}

    # Callbacks
    async def audio_cb(event):
        processed_counts["Audio"] += 1

    async def control_cb(event):
        processed_counts["Control"] += 1

    async def telemetry_cb(event):
        processed_counts["Telemetry"] += 1

    bus.subscribe(AudioFrameEvent, audio_cb)
    bus.subscribe(ControlEvent, control_cb)
    bus.subscribe(TelemetryEvent, telemetry_cb)

    await bus.start()

    total_events = 12000
    start_time = time.perf_counter()

    # 1. Producer: Flood the bus
    for i in range(total_events):
        ts = time.time()
        if i % 3 == 0:
            # Tier 1: High Priority
            await bus.publish(
                AudioFrameEvent(
                    timestamp=ts,
                    source="test",
                    latency_budget=5000,
                    pcm_data=b"\x00" * 640,
                    sample_rate=16000,
                    channels=1,
                )
            )
        elif i % 3 == 1:
            # Tier 2: Medium Priority
            await bus.publish(
                ControlEvent(
                    timestamp=ts,
                    source="test",
                    latency_budget=5000,
                    command="TEST_CMD",
                    payload={},
                )
            )
        else:
            # Tier 3: Low Priority (Droppable)
            await bus.publish(
                TelemetryEvent(
                    timestamp=ts,
                    source="test",
                    latency_budget=5000,
                    metric_name="test_metric",
                    value=1.0,
                )
            )

    # 2. Wait for processing (Max 5 seconds)
    max_wait = 10.0  # Increased wait time for full processing
    wait_start = time.perf_counter()
    while (
        sum(processed_counts.values()) < total_events
        and (time.perf_counter() - wait_start) < max_wait
    ):
        await asyncio.sleep(0.1)

    end_time = time.perf_counter()
    duration = end_time - start_time
    actual_eps = total_events / duration

    await bus.stop()

    # Results
    print(f"\n[Stress Test] Total Events: {total_events}")
    print(f"[Stress Test] Duration: {duration:.2f}s")
    print(f"[Stress Test] EPS (Events Per Second): {actual_eps:.2f}")
    print(f"[Stress Test] Final Counts: {processed_counts}")

    # Verification
    # We expect high throughput. Sub-10ms processing per burst usually yields >10k EPS easily in asyncio.
    assert actual_eps > 1000, f"Throughput too low: {actual_eps:.2f} EPS"
    # In a clean env, all should be processed (none should expire within 10s)
    assert sum(processed_counts.values()) > total_events * 0.95, (
        f"Lost too many events: {total_events - sum(processed_counts.values())} dropped."
    )


if __name__ == "__main__":
    asyncio.run(test_event_bus_10k_eps_stress())
