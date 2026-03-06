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

from core.infra.config import AetherConfig  # noqa: E402
from core.logic.managers.audio import AudioManager  # noqa: E402


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


def test_audio_manager_start(audio_manager):
    # Setup the async mocks for start methods
    audio_manager._capture.start = AsyncMock()
    audio_manager._playback.start = AsyncMock()

    # Call the method
    asyncio.run(audio_manager.start())

    # Verify both were called
    audio_manager._capture.start.assert_called_once()
    audio_manager._playback.start.assert_called_once()

def test_audio_manager_stop(audio_manager):
    audio_manager._capture.stop = AsyncMock()
    audio_manager._playback.stop = AsyncMock()

    asyncio.run(audio_manager.stop())

    audio_manager._capture.stop.assert_called_once()
    audio_manager._playback.stop.assert_called_once()
