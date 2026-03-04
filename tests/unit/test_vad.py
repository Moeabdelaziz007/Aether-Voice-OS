
import numpy as np
import pytest
from core.audio.processing import energy_vad, enhanced_vad, AdaptiveVAD, HyperVADResult

# Constants
SAMPLE_RATE = 16000
CHUNK_DURATION_S = 0.1 # 100ms chunks
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_S)
SILENCE_LEVEL = 0.0
NOISE_LEVEL = 0.02 # Represents background noise, breathing
SPEECH_LEVEL = 0.6 # Represents clear speech

def generate_complex_signal(level: float, freq: float = 220.0) -> np.ndarray:
    """Generates a slightly more complex signal for VAD testing."""
    t = np.linspace(0, CHUNK_DURATION_S, CHUNK_SAMPLES, endpoint=False)
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    signal = (level * 0.7 * np.sin(phase)) + (level * 0.3 * np.sin(phase * 2))
    return (signal * 32767).astype(np.int16)

@pytest.fixture
def adaptive_vad_engine():
    """Provides an AdaptiveVAD instance."""
    return AdaptiveVAD(sample_rate=SAMPLE_RATE, window_size_sec=2.0)

def generate_chunk(level: float, freq: float = 300.0) -> np.ndarray:
    """Generates a single audio chunk."""
    t = np.linspace(0, CHUNK_DURATION_S, CHUNK_SAMPLES, endpoint=False)
    if level == SILENCE_LEVEL:
        signal = np.zeros(CHUNK_SAMPLES)
    else:
        signal = level * np.sin(2 * np.pi * freq * t)
    
    return (signal * 32767).astype(np.int16)

def test_vad_with_static_threshold():
    """
    Tests basic VAD functionality with a fixed threshold.
    """
    silent_chunk = generate_chunk(SILENCE_LEVEL)
    speech_chunk = generate_chunk(SPEECH_LEVEL)
    
    # Using the basic energy_vad as it's simpler
    vad_result_silence = energy_vad(silent_chunk, threshold=0.1)
    vad_result_speech = energy_vad(speech_chunk, threshold=0.1)
    
    assert isinstance(vad_result_silence, HyperVADResult)
    assert not vad_result_silence.is_hard, "VAD incorrectly detected speech in silence"
    
    assert isinstance(vad_result_speech, HyperVADResult)
    assert vad_result_speech.is_hard, "VAD failed to detect speech"
    assert vad_result_speech.energy_rms > 0.1

def test_adaptive_vad_engine_updates_thresholds(adaptive_vad_engine):
    """
    Tests if the AdaptiveVAD engine correctly updates its internal noise statistics
    and provides adapted soft/hard thresholds.
    """
    # 1. Feed noise for a few seconds to establish a baseline
    for _ in range(20): # 2 seconds of noise
        noise_chunk = generate_chunk(NOISE_LEVEL)
        energy_vad(noise_chunk, adaptive_engine=adaptive_vad_engine)

    initial_stats = adaptive_vad_engine.noise_stats
    soft_thresh, hard_thresh = adaptive_vad_engine.update(initial_stats['mu'])
    
    print(f"Noise floor (mu): {initial_stats['mu']:.4f}")
    print(f"Adaptive thresholds -> Soft: {soft_thresh:.4f}, Hard: {hard_thresh:.4f}")

    # 3. Test detection with these thresholds
    soft_speech_chunk = generate_chunk(level=soft_thresh * 1.5, freq=200.0)
    # Use a simple, unambiguously loud signal for hard speech
    hard_speech_chunk = generate_chunk(level=0.5, freq=220.0)

    result_soft = enhanced_vad(soft_speech_chunk, adaptive_engine=adaptive_vad_engine)
    result_hard = enhanced_vad(hard_speech_chunk, adaptive_engine=adaptive_vad_engine)

    assert result_soft.is_soft, "Adaptive VAD failed to detect soft speech"
    assert result_hard.is_hard, "Adaptive VAD failed to detect hard speech"

def test_vad_scenario_silence_speech_silence(adaptive_vad_engine):
    """
    Simulates a realistic scenario of silence -> speech -> silence and checks VAD states.
    """
    # 1. Start with silence to establish a low noise floor
    for _ in range(10):
        result = energy_vad(generate_chunk(SILENCE_LEVEL), adaptive_engine=adaptive_vad_engine)
        assert not result.is_hard and not result.is_soft

    # 2. Introduce speech
    for _ in range(10):
        result = energy_vad(generate_chunk(SPEECH_LEVEL), adaptive_engine=adaptive_vad_engine)
        assert result.is_hard
        assert result.is_soft

    # 3. Return to silence
    # The adaptive engine's history now contains high energy, so thresholds will be high.
    # We test if it re-adapts to silence correctly.
    for _ in range(30): # Longer period to allow history to be replaced
        result = energy_vad(generate_chunk(SILENCE_LEVEL), adaptive_engine=adaptive_vad_engine)
    
    # After re-adapting, it should no longer trigger on silence.
    final_silent_result = energy_vad(generate_chunk(SILENCE_LEVEL), adaptive_engine=adaptive_vad_engine)
    assert not final_silent_result.is_hard
    assert not final_silent_result.is_soft

    final_stats = adaptive_vad_engine.noise_stats
    assert final_stats['mu'] < 0.01, "VAD failed to re-adapt to a low noise floor"
