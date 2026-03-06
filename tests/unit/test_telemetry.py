import asyncio
import sys
from unittest.mock import Mock, patch

import numpy as np
import pytest

from core.infra.config import AudioConfig

# Mock pyaudio so we don't need it installed to run tests
sys.modules["pyaudio"] = Mock()
# Must import after mocking pyaudio
from core.audio.capture import AudioCapture  # noqa: E402


@pytest.fixture
def capture_config():
    config = AudioConfig()
    config.send_sample_rate = 16000
    config.chunk_size = 512
    return config


def test_audio_telemetry_throttling(capture_config):
    q = asyncio.Queue()
    mock_telemetry_cb = Mock()

    with (
        patch("core.audio.capture.DynamicAEC"),
        patch("core.audio.capture.audio_state") as mock_state,
    ):
        mock_state.far_end_pcm.read_last.return_value = np.zeros(512, dtype=np.int16)

        capture = AudioCapture(config=capture_config, output_queue=q)

        async def async_cb(*args, **kwargs):
            mock_telemetry_cb(*args, **kwargs)

        capture._on_audio_telemetry = async_cb
        capture._loop = Mock()
        capture._loop.is_closed.return_value = False

        capture._dynamic_aec.process_frame.return_value = (
            np.zeros(512, dtype=np.int16),
            Mock(
                converged=False,
                convergence_progress=0.0,
                erle_db=0.0,
                estimated_delay_ms=0,
                double_talk_detected=False,
            ),
        )
        capture._dynamic_aec.is_user_speaking.return_value = False

        def mock_run_coroutine_threadsafe(coro, loop):
            import asyncio
            # we are in a sync test, so asyncio.run is fine
            asyncio.run(coro)

        with patch(
            "core.audio.capture.asyncio.run_coroutine_threadsafe",
            side_effect=mock_run_coroutine_threadsafe,
        ):
            in_data = b"\x00" * 1024  # 512 samples

            # Call 1st time - should trigger telemetry (initial is 0.0)
            capture._callback(in_data, 512, {}, 0)
            assert mock_telemetry_cb.call_count == 1

            # Call 2nd time immediately - should be throttled
            capture._callback(in_data, 512, {}, 0)
            assert mock_telemetry_cb.call_count == 1

            # Fast forward time to bypass throttle (> 1/15s)
            capture._last_telemetry_time -= 0.1

            # Call 3rd time - should trigger telemetry again
            capture._callback(in_data, 512, {}, 0)
            assert mock_telemetry_cb.call_count == 2
