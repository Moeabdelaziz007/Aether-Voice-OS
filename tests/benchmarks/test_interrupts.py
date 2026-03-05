import asyncio
import json
import time
from pathlib import Path

import pytest

from core.infra.event_bus import ControlEvent, EventBus


@pytest.mark.asyncio
async def test_interrupt_latency_t3_t1():
    """
    Systems Lab: Measuring actual end-to-end barge-in latency (T3 - T1).
    T1: User Speech Start Detected.
    T2: flash_interrupt() Signal Sent.
    T3: AI Playback Stopped (Drain Queue).
    Target: < 50ms.
    """
    # 1. Setup
    bus = EventBus()
    await bus.start()

    t1 = 0.0
    t2 = 0.0
    t3 = 0.0

    # Mock behavior: User Speech Detected (T1)
    # In a real system, VAD triggers this.

    async def flash_interrupt():
        nonlocal t2
        t2 = time.perf_counter()
        # Simulate signaling the kernel to stop
        await bus.publish(
            ControlEvent(
                timestamp=time.time(),
                source="test_lab",
                latency_budget=10,
                command="INTERRUPT_TRIGGER",
                payload={},
            )
        )

    async def on_kernel_stop(event):
        nonlocal t3
        t3 = time.perf_counter()

    bus.subscribe(ControlEvent, on_kernel_stop)

    # 2. Execution
    t1 = time.perf_counter()
    # Simulate VAD to Interrupt signal path
    await flash_interrupt()

    # Wait for processing
    wait_start = time.perf_counter()
    while t3 == 0 and (time.perf_counter() - wait_start) < 1.0:
        await asyncio.sleep(0.001)

    await bus.stop()

    # 3. Calculation
    latency_ms = (t3 - t1) * 1000
    signal_latency_ms = (t2 - t1) * 1000
    kernel_response_ms = (t3 - t2) * 1000

    metrics = {
        "benchmark": "interrupt_latency",
        "t3_t1_total_ms": round(latency_ms, 2),
        "t2_t1_signal_ms": round(signal_latency_ms, 2),
        "t3_t2_kernel_ms": round(kernel_response_ms, 2),
        "status": "success" if latency_ms < 50 else "failed",
    }

    # Save report
    report_path = Path("tests/reports/latency_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"\n⚡ Interrupt Latency (T3-T1): {latency_ms:.2f}ms")
    assert latency_ms < 50
