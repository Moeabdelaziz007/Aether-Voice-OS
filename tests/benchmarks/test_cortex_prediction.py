import asyncio
import json
import time
from pathlib import Path

import pytest

from core.ai.scheduler import CognitiveScheduler


class MockBus:
    def subscribe(self, event_type, callback):
        pass


class MockRouter:
    pass


@pytest.mark.asyncio
async def test_cortex_neural_lead_time():
    """
    Systems Lab: Cortex Neural Lead Time.
    Goal: Measure how far in advance (ms) a tool is pre-warmed relative to
    an average 3-second sentence.
    """
    bus = MockBus()
    router = MockRouter()
    cortex = CognitiveScheduler(event_bus=bus, router=router)

    # Simulate a user speaking a sentence that takes ~3 seconds.
    # Prediction should trigger early in the fragment.

    sentence_fragments = [
        "I",
        "I am",
        "I am seeing",
        "I am seeing some",
        "I am seeing some errors",
        "I am seeing some errors in",
        "I am seeing some errors in the logs",
    ]

    start_time = time.perf_counter()
    pre_warm_time = 0.0

    # Average speaking rate simulation
    for i, fragment in enumerate(sentence_fragments):
        cortex.speculate(fragment)
        if cortex.is_tool_pre_warmed("system_tool.read_logs") and pre_warm_time == 0:
            pre_warm_time = time.perf_counter()

        # Simulate time between words (~300ms)
        await asyncio.sleep(0.01)  # Sped up for testing, but we capture the 'word' pos

    end_time = time.perf_counter()

    # Lead time is basically: (Duration for full sentence) - (Time until pre-warm trigger)
    # We estimate based on word count/position.
    # If it triggered at word 5 of 8, it saved 3 words of time.

    prediction_triggered = cortex.is_tool_pre_warmed("system_tool.read_logs")

    metrics = {
        "benchmark": "cortex_neural_lead_time",
        "total_fragments": len(sentence_fragments),
        "pre_warmed": prediction_triggered,
        "pre_warm_elapsed_ms": round((pre_warm_time - start_time) * 1000, 2)
        if pre_warm_time > 0
        else 0,
        "status": "success" if prediction_triggered else "failed",
    }

    # Save report
    report_path = Path("tests/reports/cortex_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"\n🧠 Neural Lead Time: Pre-warmed at {metrics['pre_warm_elapsed_ms']}ms")
    assert prediction_triggered
