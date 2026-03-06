"""
Aether Voice OS — The Singularity Gauntlet (Full System Stress Test).

Validates:
1. Parallel Tool Execution (System 2: Deliberative)
2. Semantic Tool Recovery (Neural Dispatcher V3)
3. A2A Handoff Protocol (ADK V3)
4. Adaptive VAD Stability (System 1: Reflex)
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from core.ai.handover import create_handoff_protocol
from core.audio.processing import AdaptiveVAD
from core.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_parallel_tool_stress():
    """Phase 7.1: Verify router can handle multiple concurrent tool calls."""
    router = ToolRouter()

    # Register dummy tools
    async def slow_tool(x: int):
        await asyncio.sleep(0.1)
        return {"val": x * 2}

    router.register("slow_tool", "A slow tool", {"x": {"type": "integer"}}, slow_tool)

    # Mock function calls
    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args

    calls = [MockCall("slow_tool", {"x": i}) for i in range(10)]

    # Dispatch in parallel (simulating session._handle_tool_call logic)
    tasks = [router.dispatch(c) for c in calls]
    results = await asyncio.gather(*tasks)

    assert len(results) == 10
    for i, res in enumerate(results):
        assert res["result"]["val"] == i * 2
        assert res["x-a2a-status"] == 200


@pytest.mark.asyncio
async def test_semantic_recovery_success():
    """Phase 7.3: Verify Neural Dispatcher V3 recovers typos via semantic search."""
    router = ToolRouter()
    # We need a real API key for embeddings, but for test we mock the vector store
    router._vector_store = MagicMock()
    router._vector_store.get_query_embedding = AsyncMock(return_value=np.zeros(768))
    router._vector_store.search = MagicMock(
        return_value=[
            {
                "key": "delegate_to_agent",
                "similarity": 0.95,
                "metadata": {"name": "delegate_to_agent"},
            }
        ]
    )
    router._vector_store.add_text = (
        AsyncMock()
    )  # Must be AsyncMock for asyncio.create_task

    # Register the real tool
    protocol = create_handoff_protocol()
    router.register_module(protocol)

    # Mock function call object
    mock_fc = MagicMock()
    mock_fc.name = "delgate_to_agent_TYPO"
    mock_fc.args = {"target_agent_id": "test", "task_description": "test"}

    result = await router.dispatch(mock_fc)

    # Should have recovered to 'delegate_to_agent'
    assert result["x-a2a-status"] == 202
    assert "Target expert" in result["result"].get(
        "message", ""
    ) or "Task delegated" in result["result"].get("message", "")


@pytest.mark.asyncio
async def test_vad_stability_drift():
    """Phase 7.2: Verify Adaptive VAD noise floor tracking stays bounded."""
    from core.audio.processing import energy_vad

    vad = AdaptiveVAD(window_size_sec=1.0, sample_rate=16000)

    # 1. Steady low noise
    for _ in range(10):
        chunk = (np.random.normal(0, 0.01, 1600) * 32768).astype(np.int16)
        energy_vad(chunk, adaptive_engine=vad)

    initial_mu = vad._mu

    # 2. Sudden blast of noise (simulating a door slam)
    for _ in range(5):
        chunk = (np.random.normal(0, 0.5, 1600) * 32768).astype(np.int16)
        energy_vad(chunk, adaptive_engine=vad)

    # 3. Verify it adapts back down
    for _ in range(20):
        chunk = (np.random.normal(0, 0.01, 1600) * 32768).astype(np.int16)
        energy_vad(chunk, adaptive_engine=vad)

    assert vad._mu < initial_mu * 10  # Should not be stuck high
    assert vad._mu > 0


if __name__ == "__main__":
    asyncio.run(test_parallel_tool_stress())
    asyncio.run(test_semantic_recovery_success())
    asyncio.run(test_vad_stability_drift())
    print("GAUNTLET PASSED: V3 Architecture Verified.")
