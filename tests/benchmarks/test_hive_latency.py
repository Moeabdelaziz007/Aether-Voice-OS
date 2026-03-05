import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ai.hive import HiveCoordinator


@pytest.fixture
def mock_registry():
    registry = MagicMock()

    # Mock Architect Soul
    architect = MagicMock()
    architect.manifest.name = "ArchitectExpert"

    # Mock Coder Soul
    coder = MagicMock()
    coder.manifest.name = "CoderExpert"

    registry.get.side_effect = lambda name: (
        architect if name == "ArchitectExpert" else coder
    )
    registry.list_packages.return_value = ["ArchitectExpert", "CoderExpert"]
    registry.find_expert = AsyncMock(return_value=coder)

    return registry


@pytest.mark.async_hive
@pytest.mark.asyncio
async def test_hive_transition_latency_benchmark(mock_registry):
    """
    Benchmark: Hive Transition Latency (Deep Handover Protocol).
    Measures the technical overhead of shifting 'Expert Souls'.
    Target: < 50ms for local state management (excluding LLM summarization).
    """
    router = MagicMock()
    hive = HiveCoordinator(
        registry=mock_registry, router=router, enable_deep_handover=True
    )

    # We want to measure the synchronous part and the immediate async start
    # Note: NeuralSummarizer is triggered via create_task, so it shouldn't block.

    durations = []

    for _ in range(100):
        start_time = time.perf_counter()

        # 1. Prepare Handoff
        success, context, msg = hive.prepare_handoff(
            target_name="CoderExpert",
            task="Optimize latency benchmarks",
            code_context={"files_modified": ["tests/benchmarks/test_hive_latency.py"]},
        )
        assert success
        hov_id = context.handover_id

        # 2. Complete Handoff
        # Simulate target agent accepting and finalizing
        success_final, msg_final = hive.complete_handoff(hov_id)
        assert success_final

        end_time = time.perf_counter()
        durations.append((end_time - start_time) * 1000)  # to ms

    avg_latency = sum(durations) / len(durations)
    p95 = sorted(durations)[int(len(durations) * 0.95)]

    print(f"\n[Hive Benchmark] Transitions Measured: {len(durations)}")
    print(f"[Hive Benchmark] Avg Transition Latency: {avg_latency:.2f} ms")
    print(f"[Hive Benchmark] p95 Transition Latency: {p95:.2f} ms")

    # Verification
    # The internal overhead for a local Pydantic-based state machine should be very low (<10ms).
    # We set a conservative threshold of 50ms for CI/CD environments.
    assert avg_latency < 50, f"Hive transition overhead too high: {avg_latency:.2f}ms"
    assert hive.active_soul.manifest.name == "CoderExpert"


if __name__ == "__main__":
    # Setup mock and run
    reg = MagicMock()
    # Mock setup similar to fixture...
    asyncio.run(test_hive_transition_latency_benchmark(reg))
