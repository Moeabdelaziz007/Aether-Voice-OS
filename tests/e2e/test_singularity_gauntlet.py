"""
Aether Voice OS — The Singularity Gauntlet (Full System Stress Test).

Validates:
1. Parallel Tool Execution (System 2: Deliberative)
2. Semantic Tool Recovery (Neural Dispatcher V3)
3. A2A Handoff Protocol (ADK V3)
4. Adaptive VAD Stability (System 1: Reflex)
"""

import asyncio
import os

import numpy as np
import pytest
from google.genai import types

from core.ai import handoff
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

    calls = [types.FunctionCall(name="slow_tool", args={"x": i}) for i in range(10)]

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

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY required for real semantic recovery test")

    router.init_vector_store(api_key=api_key)

    # Register the real tool
    router.register_module(handoff)

    # Allow vector index to propagate (Gemini API)
    await asyncio.sleep(2.0)

    # Genuine Google GenAI FunctionCall
    mock_fc = types.FunctionCall(
        name="delegate_to_agnt",
        args={"target_agent_id": "test", "task_description": "test"},
    )

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
