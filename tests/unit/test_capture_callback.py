
import asyncio
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

# Mock the audio_state singleton before it's imported by other modules
from core.audio import state as audio_state_module
mock_audio_state = MagicMock()
mock_audio_state.far_end_pcm.read_last.return_value = np.zeros(512, dtype=np.int16) # Default empty far-end
patcher = patch.dict('sys.modules', {'core.audio.state': mock_audio_state})
patcher.start()

# Now import the class to be tested
from core.audio.capture import AudioCapture
from core.infra.config import AudioConfig

# Constants
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
    with (patch('core.audio.capture.DynamicAEC') as MockDynamicAEC,
          patch('core.audio.capture.SmoothMuter') as MockSmoothMuter,
          patch('core.audio.capture.HysteresisGate') as MockHysteresis,
          patch('core.audio.capture.AECBridge') as MockAECBridge):
        
        # Configure the return values of the mocked instances
        mock_aec_instance = MockDynamicAEC.return_value
        mock_aec_state = MagicMock()
        mock_aec_state.converged = True
        mock_aec_state.convergence_progress = 1.0
        mock_aec_state.erle_db = 25.0
        mock_aec_state.estimated_delay_ms = 0.0
        mock_aec_state.double_talk_detected = False
        mock_aec_instance.process_frame.return_value = (np.zeros(CHUNK_SIZE, dtype=np.int16), mock_aec_state)
        
        mock_smooth_muter_instance = MockSmoothMuter.return_value
        mock_smooth_muter_instance._current_gain = 1.0
        
        yield {
            "config": mock_config,
            "queue": mock_queue,
            "vad": mock_vad,
            "analyzer": mock_analyzer,
            "paralinguistic": mock_paralinguistic,
            "MockDynamicAEC": MockDynamicAEC,
            "MockSmoothMuter": MockSmoothMuter,
        }

@pytest.fixture
def capture_instance(mock_dependencies):
    """Provides an AudioCapture instance with mocked dependencies."""
    # Reset the global mock state before each test
    mock_audio_state.reset_mock()
    mock_audio_state.is_playing = False
    mock_audio_state.just_started_playing = False
    mock_audio_state.just_stopped_playing = False
    mock_audio_state.far_end_pcm.read_last.return_value = np.zeros(CHUNK_SIZE, dtype=np.int16)


    instance = AudioCapture(
        config=mock_dependencies['config'],
        output_queue=mock_dependencies['queue'],
        vad_engine=mock_dependencies['vad'],
        analyzer=mock_dependencies['analyzer'],
        paralinguistic_analyzer=mock_dependencies['paralinguistic'],
    )
    # Mock the event loop for thread-safe calls
    instance._loop = MagicMock()
    return instance

def test_callback_when_ai_is_silent_and_user_speaks(capture_instance, mock_dependencies):
    """
    Scenario: AI is not playing, user speaks.
    Expected: SmoothMuter.unmute() is called.
    """
    mock_audio_state.is_playing = False
    aec_instance = mock_dependencies['MockDynamicAEC'].return_value
    aec_instance.is_user_speaking.return_value = True
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()
    
    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)

    muter_instance = mock_dependencies['MockSmoothMuter'].return_value
    muter_instance.unmute.assert_called_once()
    muter_instance.mute.assert_not_called()

def test_callback_thalamic_gate_mutes_echo(capture_instance, mock_dependencies):
    """
    Scenario: AI is playing, and the incoming audio is determined to be echo.
    Expected: SmoothMuter.mute() is called.
    """
    mock_audio_state.is_playing = True
    aec_instance = mock_dependencies['MockDynamicAEC'].return_value
    aec_instance.is_user_speaking.return_value = False
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()

    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)

    muter_instance = mock_dependencies['MockSmoothMuter'].return_value
    muter_instance.mute.assert_called_once()
    muter_instance.unmute.assert_not_called()

def test_callback_thalamic_gate_allows_barge_in(capture_instance, mock_dependencies):
    """
    Scenario: AI is playing, but the user speaks over it (barge-in).
    Expected: SmoothMuter.unmute() is called.
    """
    mock_audio_state.is_playing = True
    aec_instance = mock_dependencies['MockDynamicAEC'].return_value
    aec_instance.is_user_speaking.return_value = True
    in_data = (np.ones(CHUNK_SIZE, dtype=np.int16) * 1000).tobytes()

    capture_instance._callback(in_data, frame_count=CHUNK_SIZE, time_info={}, status=0)

    muter_instance = mock_dependencies['MockSmoothMuter'].return_value
    muter_instance.unmute.assert_called_once()
    muter_instance.mute.assert_not_called()

# Stop the patcher after all tests are done
@pytest.fixture(scope="session", autouse=True)
def stop_patcher():
    yield
    patcher.stop()
