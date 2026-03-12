import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.audio.state import audio_state
from core.infra.transport.perception import PerceptionPipeline


@pytest.mark.asyncio
async def test_perception_broadcast_on_push():
    """Verify that push_audio triggers a broadcast only when VAD state changes."""
    broadcast_mock = AsyncMock()
    config = MagicMock()
    gateway_config = MagicMock()
    gateway_config.receive_sample_rate = 16000
    
    pipeline = PerceptionPipeline(config, gateway_config, broadcast_mock)
    await pipeline.start()
    
    # Mock audio_state
    audio_state.is_hard = False
    audio_state.aec_double_talk = False
    audio_state.last_rms = 0.5
    
    # First push - remains False, no broadcast
    await pipeline.push_audio(b"\x00" * 320)
    await asyncio.sleep(0.1)
    assert broadcast_mock.call_count == 0
    
    # Trigger state change
    audio_state.is_hard = True
    await pipeline.push_audio(b"\x00" * 320)
    await asyncio.sleep(0.1)
    
    assert broadcast_mock.call_count == 1
    
    # Second push with same state - should NOT trigger broadcast
    await pipeline.push_audio(b"\x00" * 320)
    await asyncio.sleep(0.1)
    
    assert broadcast_mock.call_count == 1
    
    # Change state and third push - should trigger broadcast
    audio_state.is_hard = False
    await pipeline.push_audio(b"\x00" * 320)
    await asyncio.sleep(0.1)
    
    assert broadcast_mock.call_count == 2
    
    await pipeline.stop()

@pytest.mark.asyncio
async def test_perception_loop_removal():
    """Verify that _vad_loop no longer exists or is not started."""
    broadcast_mock = AsyncMock()
    config = MagicMock()
    gateway_config = MagicMock()
    pipeline = PerceptionPipeline(config, gateway_config, broadcast_mock)
    
    assert not hasattr(pipeline, "_vad_loop")
    assert not hasattr(pipeline, "_vad_task")
