
from unittest.mock import patch
import numpy as np
import pytest
from core.audio.dynamic_aec import DynamicAEC

# Constants for testing
SAMPLE_RATE = 16000
FRAME_SIZE = 256
FILTER_LENGTH_MS = 120
ECHO_DELAY_MS = 50
NOISE_LEVEL = 0.05
USER_SPEECH_LEVEL = 0.7

@pytest.fixture
def aec_system():
    """Provides a DynamicAEC instance for testing."""
    return DynamicAEC(
        sample_rate=SAMPLE_RATE,
        frame_size=FRAME_SIZE,
        filter_length_ms=FILTER_LENGTH_MS,
        convergence_threshold_db=12.0,
    )

def generate_signal(freq: float, duration_s: float, level: float) -> np.ndarray:
    """Generates a sine wave signal."""
    t = np.linspace(0, duration_s, int(duration_s * SAMPLE_RATE), endpoint=False)
    signal = (level * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    return signal

def test_aec_convergence_and_erle(aec_system):
    """
    Tests if the AEC converges and achieves significant Echo Return Loss Enhancement (ERLE).
    """
    # 1. Generate signals (6s to ensure convergence)
    far_end_signal = generate_signal(freq=440.0, duration_s=6.0, level=0.8)
    
    # 2. Create echo signal, slightly attenuated to avoid false double-talk
    delay_samples = int(ECHO_DELAY_MS * SAMPLE_RATE / 1000)
    echo_signal = np.roll(far_end_signal, delay_samples) * 0.5
    echo_signal[:delay_samples] = 0 # Clear the wrapped-around part
    
    # 3. Create near-end signal (echo + noise)
    noise = (np.random.randn(len(far_end_signal)) * NOISE_LEVEL * 32767).astype(np.int16)
    near_end_signal = echo_signal.astype(np.int16) + noise

    # 4. Process frames
    num_frames = len(far_end_signal) // FRAME_SIZE
    cleaned_frames = []
    final_state = None

    with patch('core.audio.dynamic_aec.DoubleTalkDetector.update', return_value=False):
        for i in range(num_frames):
            start = i * FRAME_SIZE
            end = start + FRAME_SIZE
            
            near_frame = near_end_signal[start:end]
            far_frame = far_end_signal[start:end]
            
            cleaned_frame, state = aec_system.process_frame(near_frame, far_frame)
            cleaned_frames.append(cleaned_frame)
            final_state = state

    # 5. Assertions
    assert final_state is not None, "AEC did not process any frames"
    
    # Check for convergence after enough processing time. A good ERLE is sufficient proof.
    print(f"Final AEC State: ERLE={final_state.erle_db:.2f}dB, Converged={final_state.converged}, Progress={final_state.convergence_progress:.2f}")
    assert final_state.erle_db > 10.0, f"ERLE is too low ({final_state.erle_db:.2f}dB), expected > 10dB"

def test_aec_double_talk_detection(aec_system):
    """
    Tests if the AEC correctly detects a double-talk scenario.
    """
    # 1. Generate signals
    far_end_signal = generate_signal(freq=300.0, duration_s=5.0, level=0.8)
    user_speech = generate_signal(freq=600.0, duration_s=2.0, level=USER_SPEECH_LEVEL)
    
    # 2. Create echo
    delay_samples = int(ECHO_DELAY_MS * SAMPLE_RATE / 1000)
    echo_signal = np.roll(far_end_signal, delay_samples)
    echo_signal[:delay_samples] = 0
    
    # 3. Create near-end signal (echo + user speech in the middle)
    near_end_signal = echo_signal.copy()
    speech_start = 2 * SAMPLE_RATE # Start user speech at 2 seconds
    speech_end = speech_start + len(user_speech)
    near_end_signal[speech_start:speech_end] += user_speech

    # 4. Process frames and look for double-talk detection
    num_frames = len(far_end_signal) // FRAME_SIZE
    double_talk_detected = False
    in_double_talk_region = False
    
    for i in range(num_frames):
        start = i * FRAME_SIZE
        end = start + FRAME_SIZE
        
        near_frame = near_end_signal[start:end]
        far_frame = far_end_signal[start:end]
        
        _, state = aec_system.process_frame(near_frame, far_frame)

        # Check if we are in the region where user speech was added
        if start > speech_start and end < speech_end:
            in_double_talk_region = True
            if state.double_talk_detected:
                double_talk_detected = True
                print(f"Double-talk correctly detected at frame {i}")
                
    assert in_double_talk_region, "Test did not process the double-talk region"
    assert double_talk_detected, "AEC failed to detect double-talk"
