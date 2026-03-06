import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

def setup_mocks():
    mock_modules = ['firebase_admin', 'firebase_admin.credentials', 'firebase_admin.firestore', 'google.cloud.firestore', 'websockets', 'google.genai', 'pyaudio', 'watchdog', 'watchdog.observers', 'watchdog.events', 'webrtcvad']
    for module_name in mock_modules:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()

setup_mocks()

import pytest  # noqa: E402

from core.logic.managers.audio import AudioManager  # noqa: E402
from core.infra.config import AetherConfig  # noqa: E402


@pytest.fixture
def mock_config():
    config = MagicMock(spec=AetherConfig)
    config.audio = MagicMock()
    config.audio.send_sample_rate = 16000
    config.audio.vad_window_sec = 5.0
    return config


@pytest.fixture
def mock_gateway():
    gateway = MagicMock()
    gateway.audio_in_queue = MagicMock()
    gateway.audio_out_queue = MagicMock()
    gateway.broadcast = MagicMock()
    gateway.broadcast_binary = MagicMock()
    return gateway


@pytest.fixture
def audio_manager(mock_config, mock_gateway):
    with (
        patch("core.logic.managers.audio.ParalinguisticAnalyzer"),
        patch("core.logic.managers.audio.AdaptiveVAD"),
        patch("core.logic.managers.audio.AudioCapture"),
        patch("core.logic.managers.audio.AudioPlayback")
    ):
        manager = AudioManager(
            config=mock_config,
            gateway=mock_gateway,
            on_affective_data=MagicMock()
        )
        return manager


@pytest.mark.asyncio
async def test_audio_manager_start(audio_manager):
    with (
        patch("core.logic.managers.audio.AudioCapture") as MockCapture,
        patch("core.logic.managers.audio.AudioPlayback") as MockPlayback
    ):
        mock_capture_instance = MockCapture.return_value
        mock_capture_instance.start = AsyncMock()
        mock_playback_instance = MockPlayback.return_value
        mock_playback_instance.start = AsyncMock()

        await audio_manager.start()

        mock_capture_instance.start.assert_called_once()
        mock_playback_instance.start.assert_called_once()

@pytest.mark.asyncio
async def test_audio_manager_stop(audio_manager):
    with (
        patch("core.logic.managers.audio.AudioCapture") as MockCapture,
        patch("core.logic.managers.audio.AudioPlayback") as MockPlayback
    ):
        mock_capture_instance = MockCapture.return_value
        mock_capture_instance.start = AsyncMock()
        mock_capture_instance.stop = AsyncMock()
        mock_playback_instance = MockPlayback.return_value
        mock_playback_instance.start = AsyncMock()
        mock_playback_instance.stop = AsyncMock()

        await audio_manager.start()
        await audio_manager.stop()

        mock_capture_instance.stop.assert_called_once()
        mock_playback_instance.stop.assert_called_once()
