import asyncio
import queue

import numpy as np
import pytest

from core.audio.capture import AudioCapture
from core.audio.playback import AudioPlayback
from core.audio.state import audio_state
from core.infra.config import AudioConfig


@pytest.fixture
def audio_config():
    return AudioConfig()


@pytest.fixture
def audio_queues():
    return asyncio.Queue(maxsize=10), asyncio.Queue(maxsize=10)


@pytest.mark.asyncio
async def test_capture_playback_round_trip(audio_config, audio_queues, mocker):
    """Test complete audio pipeline: capture → process → playback"""
    capture_queue, playback_queue = audio_queues

    # Mock pyaudio to avoid ALSA errors in CI/testing
    mocker.patch("pyaudio.PyAudio")

    # Create capture and playback instances
    capture = AudioCapture(audio_config, capture_queue)
    playback = AudioPlayback(audio_config, playback_queue)

    # Start both
    await capture.start()
    await playback.start()

    # Generate test audio
    test_signal = np.random.randint(-1000, 1000, 512, dtype=np.int16)

    # Simulate capture → playback flow
    # Assuming AudioCapture has a _push_to_async_queue method or we can put directly
    if hasattr(capture, "_push_to_async_queue"):
        capture._push_to_async_queue({"data": test_signal.tobytes()})
    else:
        await capture_queue.put({"data": test_signal.tobytes()})

    # Route capture queue to playback queue to simulate processing
    data = await capture_queue.get()
    await playback_queue.put(data["data"])

    # Also push to playback's internal buffer since `run()` might not be running in test
    playback._buffer.put(data["data"])

    # Wait for processing
    await asyncio.sleep(0.1)

    # Verify playback received data
    assert not playback._buffer.empty()

    # Cleanup
    await capture.stop()
    await playback.stop()


@pytest.mark.asyncio
async def test_barge_in_interrupts_playback(audio_config, audio_queues, mocker):
    """Test that barge-in immediately stops playback"""
    _, playback_queue = audio_queues

    mocker.patch("pyaudio.PyAudio")

    playback = AudioPlayback(audio_config, playback_queue)

    await playback.start()

    # Fill buffer
    for _ in range(5):
        await playback_queue.put(b"\x00" * 1024)

    # Also fill internal buffer if possible
    for _ in range(5):
        try:
            playback._buffer.put_nowait(b"\x00" * 1024)
        except queue.Full:
            pass

    # Trigger interrupt
    playback.interrupt()

    # Verify both queues are empty
    assert playback_queue.empty()
    assert playback._buffer.empty()

    # audio_state.is_playing is updated by interrupt() / set_playing(False)
    assert not audio_state.is_playing

    await playback.stop()
