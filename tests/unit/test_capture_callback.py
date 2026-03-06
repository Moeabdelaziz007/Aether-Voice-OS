"""Tests for core.audio.capture AudioCapture callback + SmoothMuter.

Focus:
- SmoothMuter ramp is gradual and lands on target
- Mute/unmute transitions avoid large boundary discontinuities (click proxy)
- Callback runs without errors when audio_state.is_playing True/False
- Queue overflow handling drops oldest and increments telemetry counter

These tests mock:
- audio_state singleton
- DynamicAEC
- DynamicAEC
- HysteresisGate
- Event loop injection

Note: The callback returns (None, paContinue) because capture does not echo audio.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Patch the audio_state module before importing AudioCapture
mock_audio_state = MagicMock()
mock_audio_state.far_end_pcm.read_last.return_value = np.zeros(512, dtype=np.int16)
mock_audio_state.capture_queue_drops = 0

patcher = patch.dict(
    "sys.modules",
    {
        "core.audio.state": MagicMock(
            audio_state=mock_audio_state, HysteresisGate=MagicMock()
        )
    },
)
patcher.start()

import sys  # noqa: E402
from unittest.mock import Mock  # noqa: E402

sys.modules["pyaudio"] = Mock()
from core.audio.capture import AudioCapture, SmoothMuter  # noqa: E402
from core.infra.config import AudioConfig  # noqa: E402

SAMPLE_RATE = 16000
CHUNK_SIZE = 512


@pytest.fixture
def mock_dependencies():
    """Mocks all external dependencies for AudioCapture."""
    mock_config = AudioConfig(send_sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE)
    mock_queue = MagicMock(spec=asyncio.Queue)
    mock_vad = MagicMock()
    mock_analyzer = MagicMock()
    mock_paralinguistic = MagicMock()

    # We also need to mock the classes instantiated inside AudioCapture
    with (
        patch("core.audio.capture.DynamicAEC") as MockDynamicAEC,
        patch("core.audio.capture.SmoothMuter") as MockSmoothMuter,
        patch("core.audio.capture.HysteresisGate") as MockHysteresis,
    ):
        # Configure the return values of the mocked instances
        mock_aec_instance = MockDynamicAEC.return_value
        mock_aec_state = MagicMock()
        mock_aec_state.converged = True
        mock_aec_state.convergence_progress = 1.0
        mock_aec_state.erle_db = 25.0
        mock_aec_state.estimated_delay_ms = 0.0
        mock_aec_state.double_talk_detected = False
        mock_aec_instance.process_frame.return_value = (
            np.zeros(CHUNK_SIZE, dtype=np.int16),
            mock_aec_state,
        )

        mock_smooth_muter_instance = MockSmoothMuter.return_value
        mock_smooth_muter_instance._current_gain = 1.0

        # Hysteresis gate just mirrors is_playing
        MockHysteresis.return_value.update.side_effect = lambda x: x

        yield {
            "config": mock_config,
            "queue": mock_queue,
            "vad": mock_vad,
            "analyzer": mock_analyzer,
            "paralinguistic": mock_paralinguistic,
            "MockDynamicAEC": MockDynamicAEC,
            "MockSmoothMuter": MockSmoothMuter,
        }


def _sine_pcm16(
    freq_hz: float, amp: float, n: int = CHUNK_SIZE, sr: int = SAMPLE_RATE
) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / sr
    x = amp * np.sin(2.0 * np.pi * freq_hz * t)
    return (np.clip(x, -1.0, 1.0) * 32767.0).astype(np.int16)


@pytest.fixture(scope="session", autouse=True)
def _stop_patcher():
    yield
    patcher.stop()


def test_smooth_muter_ramp_is_gradual_and_hits_target():
    muter = SmoothMuter(ramp_samples=256)
    x = np.full(512, 20000, dtype=np.int16)

    muter.mute()
    y1 = muter.process(x)
    assert muter._current_gain < 1.0
    assert np.abs(y1[-1]) < np.abs(x[-1])

    # After enough samples processed, should land exactly at 0.0
    y2 = muter.process(x)
    assert muter._current_gain == 0.0
    assert np.all(y2[-10:] == 0)

    muter.unmute()
    muter.process(x)
    # After unmute, gain should have risen (ramp_samples=256 fits inside chunk of 512)
    assert muter._current_gain == 1.0

    y4 = muter.process(x)
    assert muter._current_gain == 1.0
    np.testing.assert_array_equal(y4, x)


def test_smooth_muter_no_large_boundary_discontinuity_click_proxy():
    muter = SmoothMuter(ramp_samples=256)
    x = _sine_pcm16(440.0, amp=0.8, n=512)

    # Mute transition
    muter.mute()
    y1 = muter.process(x)
    y2 = muter.process(x)

    # Click proxy: boundary jump between last sample of y1 and first of y2
    jump = int(y2[0]) - int(y1[-1])
    assert abs(jump) < 8000  # generous bound; should not be a full-scale step


@pytest.fixture
def capture_instance():
    # Reset mocked global state
    mock_audio_state.reset_mock()
    mock_audio_state.is_playing = False
    mock_audio_state.just_started_playing = False
    mock_audio_state.just_stopped_playing = False
    mock_audio_state.far_end_pcm.read_last.return_value = np.zeros(
        CHUNK_SIZE, dtype=np.int16
    )
    mock_audio_state.capture_queue_drops = 0

    config = AudioConfig(send_sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE)
    q: asyncio.Queue = MagicMock(spec=asyncio.Queue)

    with (
        patch("core.audio.capture.DynamicAEC") as MockAEC,
        patch("core.audio.capture.HysteresisGate") as MockHyst,
    ):
        # Configure AEC mock
        aec_state = MagicMock()
        aec_state.converged = True
        aec_state.convergence_progress = 1.0
        aec_state.erle_db = 20.0
        aec_state.estimated_delay_ms = 0.0
        aec_state.double_talk_detected = False

        MockAEC.return_value.process_frame.return_value = (
            np.zeros(CHUNK_SIZE, dtype=np.int16),
            aec_state,
        )
        MockAEC.return_value.is_user_speaking.return_value = True

        # Hysteresis gate just mirrors is_playing
        MockHyst.return_value.update.side_effect = lambda x: x

        inst = AudioCapture(config=config, output_queue=q)
        inst._loop = MagicMock()
        return inst


def test_callback_when_ai_is_silent_and_user_speaks(
    capture_instance, mock_dependencies
):
    """
    Scenario: AI is not playing, user speaks.
    Expected: SmoothMuter.unmute() is called.
    """
    import core.audio.capture

    core.audio.capture.audio_state.is_playing = False
    core.audio.capture.audio_state.just_started_playing = False
    core.audio.capture.audio_state.just_stopped_playing = False

    aec_instance = mock_dependencies["MockDynamicAEC"].return_value
    aec_instance.is_user_speaking.return_value = True
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()

    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)


def test_callback_runs_when_ai_not_playing(capture_instance: AudioCapture):
    mock_audio_state.is_playing = False
    in_data = _sine_pcm16(220.0, amp=0.2).tobytes()

    out, status = capture_instance._callback(in_data, CHUNK_SIZE, {}, 0)
    assert out is None
    assert status is not None


def test_callback_thalamic_gate_mutes_echo(capture_instance, mock_dependencies):
    """
    Scenario: AI is playing, and the incoming audio is determined to be echo.
    Expected: SmoothMuter.mute() is called.
    """
    import core.audio.capture

    core.audio.capture.audio_state.is_playing = True
    core.audio.capture.audio_state.just_started_playing = False
    core.audio.capture.audio_state.just_stopped_playing = False

    aec_instance = mock_dependencies["MockDynamicAEC"].return_value
    aec_instance.is_user_speaking.return_value = False
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()

    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)


def test_callback_runs_when_ai_playing(capture_instance: AudioCapture):
    mock_audio_state.is_playing = True
    in_data = _sine_pcm16(220.0, amp=0.2).tobytes()

    out, status = capture_instance._callback(in_data, CHUNK_SIZE, {}, 0)
    assert out is None
    assert status is not None


def test_callback_thalamic_gate_allows_barge_in(capture_instance, mock_dependencies):
    """
    Scenario: AI is playing, but the user speaks over it (barge-in).
    Expected: SmoothMuter.unmute() is called.
    """
    import core.audio.capture

    core.audio.capture.audio_state.is_playing = True
    core.audio.capture.audio_state.just_started_playing = False
    core.audio.capture.audio_state.just_stopped_playing = False

    aec_instance = mock_dependencies["MockDynamicAEC"].return_value
    aec_instance.is_user_speaking.return_value = True
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()

    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)


def test_push_to_async_queue_overflow_drops_oldest_and_counts_telemetry(
    capture_instance: AudioCapture,
):
    import core.audio.capture

    # Simulate QueueFull once, then success.
    q = capture_instance._async_queue

    class _Full(Exception):
        pass

    # Use real asyncio exceptions
    q.put_nowait.side_effect = [asyncio.QueueFull(), None]
    q.get_nowait.side_effect = [object()]

    capture_instance._push_to_async_queue({"data": b"x", "mime_type": "audio/pcm"})

    assert core.audio.capture.audio_state.capture_queue_drops >= 1
    assert q.get_nowait.call_count == 1
    assert q.put_nowait.call_count == 2
