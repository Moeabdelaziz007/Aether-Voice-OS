import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from core.ai.session import GeminiLiveSession
from core.audio.processing import AdaptiveVAD, energy_vad


@pytest.mark.asyncio
async def test_adaptive_vad_noise_climb():
    """Verify that AdaptiveVAD follows a rising noise floor."""
    vad = AdaptiveVAD(window_size_sec=1.0, min_threshold=0.01)

    # 1. Quiet environment
    quiet_chunk = np.random.normal(0, 100, 1600).astype(np.int16)  # Low energy
    res1 = energy_vad(quiet_chunk, adaptive_engine=vad)
    initial_threshold = vad.update(res1.energy_rms)

    # 2. Noise floor rises
    for _ in range(20):
        noisy_chunk = np.random.normal(0, 1000, 1600).astype(np.int16)
        energy_vad(noisy_chunk, adaptive_engine=vad)

    final_threshold = vad.update(0.015)  # Still noisy

    assert final_threshold > initial_threshold
    print(f"\nVAD Adaptation: {initial_threshold[1]:.4f} -> {final_threshold[1]:.4f}")


@pytest.mark.asyncio
async def test_parallel_dispatch_benchmark():
    """Verify that multiple tool calls are executed in parallel."""
    # Mock router that delays 0.5s per call
    mock_router = MagicMock()
    mock_router.count = 5

    async def delayed_dispatch(fc):
        await asyncio.sleep(0.5)
        return {"status": "ok", "tool": fc.name}

    mock_router.dispatch = AsyncMock(side_effect=delayed_dispatch)

    # Mock Session
    mock_session = AsyncMock()

    # Initialize Gemini session logic
    gs = GeminiLiveSession(
        config=MagicMock(),
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        tool_router=mock_router,
    )

    # Simulate 5 parallel function calls from Gemini
    mock_tool_call = MagicMock()
    mock_tool_call.function_calls = [
        MagicMock(name=f"tool_{i}", args={}) for i in range(5)
    ]
    for i, fc in enumerate(mock_tool_call.function_calls):
        fc.name = f"tool_{i}"

    start_time = time.perf_counter()
    await gs._handle_tool_call(mock_session, mock_tool_call)
    end_time = time.perf_counter()

    duration = end_time - start_time

    # If sequential, it would take 2.5s. If parallel, ~0.5s.
    assert duration < 1.0
    print(
        f"\nParallel Dispatch Duration: {duration:.4f}s for 5 tools (Sequential would be 2.5s)"
    )
