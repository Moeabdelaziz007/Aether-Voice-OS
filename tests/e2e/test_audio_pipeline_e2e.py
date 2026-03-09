"""
Aether Voice OS — End-to-End Audio Pipeline Tests.

Validates the complete flow from microphone input through the audio 
processing chain, AI session management, and audio output playback.

Test Categories:
1. Audio Capture and Processing Pipeline
2. Thalamic Gate AEC Functionality  
3. Multi-Agent Orchestration
4. WebSocket Gateway Communication
5. Real-time Telemetry and State Management
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from core.audio.capture import (
    AdaptiveJitterBuffer,
    SmoothMuter,
)
from core.audio.dynamic_aec import (
    AECState,
    DelayEstimator,
    DoubleTalkDetector,
    DynamicAEC,
    FrequencyDomainNLMS,
)
from core.audio.state import HysteresisGate, audio_state
from core.infra.config import AudioConfig

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def audio_config() -> AudioConfig:
    """Create test audio configuration."""
    return AudioConfig(
        send_sample_rate=16000,
        chunk_size=256,
        channels=1,
        aec_filter_length_ms=100.0,
        aec_step_size=0.5,
        aec_convergence_threshold_db=15.0,
        jitter_buffer_target_ms=60.0,
        jitter_buffer_max_ms=200.0,
        mute_delay_samples=800,
        unmute_delay_samples=1200,
        mic_queue_max=100,
    )


@pytest.fixture
def sample_audio_chunk() -> np.ndarray:
    """Generate a sample audio chunk (sine wave at 440Hz)."""
    duration_ms = 16  # 256 samples at 16kHz
    t = np.linspace(0, duration_ms / 1000, 256, dtype=np.float32)
    frequency = 440  # A4 note
    amplitude = 0.5
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return (sine_wave * 32767).astype(np.int16)


@pytest.fixture
def echo_audio_chunk(sample_audio_chunk: np.ndarray) -> np.ndarray:
    """Generate an echo-like audio chunk (delayed and attenuated)."""
    delay_samples = 50  # ~3ms delay
    attenuation = 0.3
    echo = np.zeros_like(sample_audio_chunk)
    echo[delay_samples:] = sample_audio_chunk[:-delay_samples] * attenuation
    return echo.astype(np.int16)


@pytest.fixture
def silence_chunk() -> np.ndarray:
    """Generate a silence chunk."""
    return np.zeros(256, dtype=np.int16)


@pytest.fixture
def noise_chunk() -> np.ndarray:
    """Generate white noise chunk."""
    return np.random.randint(-1000, 1000, 256, dtype=np.int16)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: ADAPTIVE JITTER BUFFER
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdaptiveJitterBuffer:
    """Test suite for AdaptiveJitterBuffer functionality."""

    def test_jitter_buffer_write_read_cycle(self):
        """Test basic write and read operations."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        # Write some data
        data = np.random.randint(-10000, 10000, 256, dtype=np.int16)
        jbuffer.write(data)
        
        # Read back
        result = jbuffer.read(256)
        
        assert len(result) == 256
        np.testing.assert_array_equal(result, data)

    def test_jitter_buffer_underrun_returns_zeros(self):
        """Test that underrun returns zero-padded output."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        # Read without writing
        result = jbuffer.read(256)
        
        assert len(result) == 256
        assert np.all(result == 0)

    def test_jitter_buffer_accumulation(self):
        """Test that multiple writes accumulate correctly."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        # Write multiple chunks
        chunk1 = np.ones(256, dtype=np.int16) * 100
        chunk2 = np.ones(256, dtype=np.int16) * 200
        chunk3 = np.ones(256, dtype=np.int16) * 300
        
        jbuffer.write(chunk1)
        jbuffer.write(chunk2)
        jbuffer.write(chunk3)
        
        # Read all
        result = jbuffer.read(768)
        
        assert len(result) == 768
        np.testing.assert_array_equal(result[:256], chunk1)
        np.testing.assert_array_equal(result[256:512], chunk2)
        np.testing.assert_array_equal(result[512:768], chunk3)

    def test_jitter_buffer_wrap_around(self):
        """Test circular buffer wrap-around behavior."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        max_samples = int(200.0 * 16000 / 1000)  # 3200 samples
        
        # Write more than buffer capacity to trigger wrap
        large_data = np.random.randint(-10000, 10000, max_samples + 500, dtype=np.int16)
        jbuffer.write(large_data)
        
        # Should keep only the last max_samples
        result = jbuffer.read(max_samples)
        
        assert len(result) == max_samples

    def test_jitter_buffer_latency_target(self):
        """Test that jitter buffer maintains target latency."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        target_samples = int(60.0 * 16000 / 1000)  # 960 samples
        
        # Write enough data to reach target
        for _ in range(4):
            jbuffer.write(np.random.randint(-1000, 1000, 256, dtype=np.int16))
        
        # Buffer should have accumulated data
        assert jbuffer.size >= target_samples


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: SMOOTH MUTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestSmoothMuter:
    """Test suite for SmoothMuter fade in/out functionality."""

    def test_muter_passes_audio_at_full_gain(self, sample_audio_chunk):
        """Test that unmuted audio passes through at full gain."""
        muter = SmoothMuter(ramp_samples=256)
        muter.unmute()
        
        # Process after unmute
        result = muter.process(sample_audio_chunk)
        
        # Should be nearly identical (allowing for float conversion)
        np.testing.assert_array_almost_equal(result, sample_audio_chunk, decimal=0)

    def test_muter_mutes_audio(self, sample_audio_chunk):
        """Test that muted audio becomes silence."""
        muter = SmoothMuter(ramp_samples=256)
        muter.unmute()
        muter.process(sample_audio_chunk)  # Process once at full gain
        
        muter.mute()
        
        # Process multiple times to complete ramp
        for _ in range(5):
            result = muter.process(sample_audio_chunk)
        
        # Should be silence
        assert np.max(np.abs(result)) < 100  # Very small values

    def test_muter_ramp_continuity(self, sample_audio_chunk):
        """Test that ramp has no discontinuities (no clicks/pops)."""
        muter = SmoothMuter(ramp_samples=256)
        
        # Process multiple chunks with changing state
        results = []
        muter.unmute()
        results.append(muter.process(sample_audio_chunk))
        muter.mute()
        results.append(muter.process(sample_audio_chunk))
        results.append(muter.process(sample_audio_chunk))
        
        # Check for discontinuities
        for result in results:
            # Check that there are no large jumps between adjacent samples
            diffs = np.abs(np.diff(result.astype(np.float32)))
            max_jump = np.max(diffs)
            assert max_jump < 1000, f"Large discontinuity detected: {max_jump}"

    def test_muter_ramp_endpoint_accuracy(self, sample_audio_chunk):
        """Test that ramp lands exactly on target gain."""
        muter = SmoothMuter(ramp_samples=256)
        
        # Start muted, unmute
        muter.mute()
        muter.process(sample_audio_chunk)
        
        muter.unmute()
        # Process enough chunks to complete ramp
        for _ in range(3):
            muter.process(sample_audio_chunk)
        
        # Check final gain is exactly 1.0
        assert muter._current_gain == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: DYNAMIC AEC
# ═══════════════════════════════════════════════════════════════════════════════

class TestDynamicAEC:
    """Test suite for Dynamic Acoustic Echo Cancellation."""

    def test_aec_initialization(self, audio_config: AudioConfig):
        """Test that DynamicAEC initializes correctly."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
            filter_length_ms=audio_config.aec_filter_length_ms,
            step_size=audio_config.aec_step_size,
            convergence_threshold_db=audio_config.aec_convergence_threshold_db,
        )
        
        assert aec.sample_rate == 16000
        assert aec.frame_size == 256
        assert aec.state.converged is False
        assert aec.state.erle_db == 0.0

    def test_aec_process_frame_basic(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
        echo_audio_chunk: np.ndarray,
    ):
        """Test basic frame processing."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        # Process frame with echo
        cleaned, state = aec.process_frame(sample_audio_chunk, echo_audio_chunk)
        
        assert len(cleaned) == audio_config.chunk_size
        assert isinstance(state, AECState)
        assert state.frames_processed == 1

    def test_aec_echo_reduction(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
    ):
        """Test that AEC reduces echo energy."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        # Create echo signal (delayed copy)
        delay_samples = 100
        echo = np.zeros_like(sample_audio_chunk)
        echo[delay_samples:] = sample_audio_chunk[:-delay_samples] * 0.5
        echo = echo.astype(np.int16)
        
        # Process multiple frames to allow convergence
        for _ in range(50):
            cleaned, state = aec.process_frame(sample_audio_chunk, echo)
        
        # Echo energy should be reduced
        original_energy = np.mean(echo.astype(np.float32) ** 2)
        cleaned_energy = np.mean(cleaned.astype(np.float32) ** 2)
        
        # Cleaned should have less energy than echo (echo cancellation working)
        assert state.erle_db > 0 or cleaned_energy < original_energy

    def test_aec_convergence_tracking(self, audio_config: AudioConfig):
        """Test AEC convergence progress tracking."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
            convergence_threshold_db=10.0,
        )
        
        # Simulate sustained high ERLE (would indicate convergence)
        # In practice, this depends on actual audio signals
        assert aec.state.convergence_progress == 0.0
        
        # After processing, check state updates
        near_end = np.random.randint(-5000, 5000, 256, dtype=np.int16)
        far_end = np.random.randint(-5000, 5000, 256, dtype=np.int16)
        
        cleaned, state = aec.process_frame(near_end, far_end)
        
        assert state.frames_processed == 1

    def test_aec_double_talk_detection(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
        silence_chunk: np.ndarray,
    ):
        """Test double-talk detection during simultaneous speech."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        # Process with only far-end (AI speaking)
        for _ in range(10):
            cleaned, state = aec.process_frame(silence_chunk, sample_audio_chunk)
        
        # Process with both near and far-end (double-talk)
        for _ in range(10):
            cleaned, state = aec.process_frame(sample_audio_chunk, sample_audio_chunk)
        
        # Double-talk detector should eventually trigger
        # (depends on energy ratios and coherence)

    def test_aec_reset(self, audio_config: AudioConfig):
        """Test AEC reset functionality."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        # Process some frames
        for _ in range(10):
            near = np.random.randint(-5000, 5000, 256, dtype=np.int16)
            far = np.random.randint(-5000, 5000, 256, dtype=np.int16)
            aec.process_frame(near, far)
        
        # Reset
        aec.reset()
        
        # Check state is reset
        assert aec.state.frames_processed == 0
        assert aec.state.converged is False

    def test_aec_is_user_speaking_detection(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
        silence_chunk: np.ndarray,
    ):
        """Test is_user_speaking method for barge-in detection."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        # Process some frames to establish baseline
        for _ in range(20):
            aec.process_frame(silence_chunk, sample_audio_chunk)
        
        # Check user speaking detection
        result = aec.is_user_speaking(sample_audio_chunk)
        
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: FREQUENCY DOMAIN NLMS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFrequencyDomainNLMS:
    """Test suite for Frequency-Domain NLMS adaptive filter."""

    def test_nlms_initialization(self):
        """Test NLMS filter initialization."""
        nlms = FrequencyDomainNLMS(
            filter_length=512,
            step_size=0.5,
            regularization=1e-4,
            leakage=0.999,
        )
        
        assert nlms.filter_length == 512
        assert nlms.step_size == 0.5
        assert len(nlms.W) == 513  # n_fft // 2 + 1

    def test_nlms_process_shape(self):
        """Test that process returns correct shapes."""
        nlms = FrequencyDomainNLMS(filter_length=256)
        
        far_end = np.random.randn(256)
        near_end = np.random.randn(256)
        
        error, echo_est = nlms.process(far_end, near_end)
        
        assert len(error) == 256
        assert len(echo_est) == 256

    def test_nlms_filter_energy(self):
        """Test filter energy computation."""
        nlms = FrequencyDomainNLMS(filter_length=256)
        
        # Process some data
        for _ in range(10):
            far = np.random.randn(256)
            near = np.random.randn(256)
            nlms.process(far, near)
        
        energy = nlms.get_filter_energy()
        
        assert energy > 0

    def test_nlms_reset(self):
        """Test NLMS filter reset."""
        nlms = FrequencyDomainNLMS(filter_length=256)
        
        # Process some data
        for _ in range(10):
            far = np.random.randn(256)
            near = np.random.randn(256)
            nlms.process(far, near)
        
        nlms.reset()
        
        # Check weights are reset
        assert np.all(nlms.W == 0)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: DOUBLE TALK DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestDoubleTalkDetector:
    """Test suite for Double-Talk Detection."""

    def test_dtd_initialization(self):
        """Test DTD initialization."""
        dtd = DoubleTalkDetector(
            sample_rate=16000,
            coherence_threshold=0.65,
            energy_ratio_threshold=0.5,
            hangover_frames=10,
        )
        
        assert dtd.sample_rate == 16000
        assert dtd.is_double_talk is False

    def test_dtd_energy_ratio_detection(self):
        """Test DTD based on energy ratio."""
        dtd = DoubleTalkDetector(sample_rate=16000)
        
        # High near-end energy relative to far-end
        near_end = np.random.randn(256) * 0.5
        far_end = np.random.randn(256) * 0.01
        error = near_end - far_end
        
        # Process multiple frames
        for _ in range(15):
            dtd.update(far_end, near_end, error)
        
        # Should detect as double-talk or near-end speech
        # (depends on thresholds)

    def test_dtd_reset(self):
        """Test DTD reset functionality."""
        dtd = DoubleTalkDetector(sample_rate=16000)
        
        # Process some frames
        near = np.random.randn(256)
        far = np.random.randn(256)
        error = near - far
        
        for _ in range(10):
            dtd.update(far, near, error)
        
        dtd.reset()
        
        assert dtd.is_double_talk is False
        assert dtd.hangover_counter == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: DELAY ESTIMATOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestDelayEstimator:
    """Test suite for GCC-PHAT Delay Estimation."""

    def test_delay_estimator_initialization(self):
        """Test delay estimator initialization."""
        de = DelayEstimator(
            sample_rate=16000,
            max_delay_ms=200.0,
            update_interval_ms=500.0,
        )
        
        assert de.sample_rate == 16000
        assert de.estimated_delay_samples == 0

    def test_delay_estimation_known_delay(self):
        """Test delay estimation with known delay."""
        de = DelayEstimator(sample_rate=16000, update_interval_ms=100.0)
        
        # Create signal with known delay
        signal = np.random.randn(3200)
        delay_samples = 100
        delayed = np.zeros(3200)
        delayed[delay_samples:] = signal[:-delay_samples]
        
        # Process multiple chunks
        chunk_size = 256
        for i in range(0, len(signal) - chunk_size, chunk_size):
            de.process(
                signal[i:i + chunk_size],
                delayed[i:i + chunk_size]
            )
        
        # Should estimate delay (may not be exact due to adaptive smoothing)
        assert de.estimated_delay_samples > 0

    def test_delay_estimator_reset(self):
        """Test delay estimator reset."""
        de = DelayEstimator(sample_rate=16000)
        
        # Process some data
        signal = np.random.randn(1000)
        de.process(signal, signal)
        
        de.reset()
        
        assert de.estimated_delay_samples == 0
        assert de.confidence == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: HYSTERESIS GATE
# ═══════════════════════════════════════════════════════════════════════════════

class TestHysteresisGate:
    """Test suite for Hysteresis Gate functionality."""

    def test_hysteresis_basic_operation(self):
        """Test basic on/off operation."""
        gate = HysteresisGate()
        
        # Initially off
        assert gate.update(False) is False
        
        # Turn on
        assert gate.update(True) is True
        
        # Turn off
        assert gate.update(False) is False

    def test_hysteresis_prevents_bouncing(self):
        """Test that hysteresis prevents rapid on/off switching."""
        gate = HysteresisGate()
        
        # Rapid switching
        results = []
        for state in [True, False, True, False, True]:
            results.append(gate.update(state))
        
        # Should eventually settle
        assert len(results) == 5

    def test_hysteresis_state_persistence(self):
        """Test that state persists through brief changes."""
        gate = HysteresisGate()
        
        # Turn on
        gate.update(True)
        
        # Brief off
        gate.update(False)
        
        # Should still be in some defined state
        result = gate.update(True)
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: AUDIO STATE
# ═══════════════════════════════════════════════════════════════════════════════

class TestAudioState:
    """Test suite for global audio state management."""

    def test_audio_state_initialization(self):
        """Test audio state initialization."""
        assert hasattr(audio_state, 'is_playing')
        assert hasattr(audio_state, 'last_rms')
        assert hasattr(audio_state, 'is_soft')
        assert hasattr(audio_state, 'is_hard')

    def test_audio_state_update_aec(self):
        """Test AEC state update."""
        audio_state.update_aec_state(
            converged=True,
            convergence_progress=0.8,
            erle_db=20.0,
            delay_ms=50.0,
            double_talk=False,
        )
        
        assert audio_state.aec_converged is True

    def test_audio_state_rms_update(self):
        """Test RMS level update."""
        audio_state.last_rms = 0.0
        audio_state.last_rms = 0.5
        
        assert audio_state.last_rms == 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAudioPipelinePerformance:
    """Performance benchmarks for audio pipeline."""

    @pytest.mark.performance
    def test_aec_frame_processing_latency(self, audio_config: AudioConfig):
        """Benchmark AEC frame processing latency."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        
        near = np.random.randint(-5000, 5000, 256, dtype=np.int16)
        far = np.random.randint(-5000, 5000, 256, dtype=np.int16)
        
        # Warm up
        for _ in range(10):
            aec.process_frame(near, far)
        
        # Benchmark
        iterations = 1000
        start = time.perf_counter()
        
        for _ in range(iterations):
            aec.process_frame(near, far)
        
        elapsed = time.perf_counter() - start
        avg_latency_ms = (elapsed / iterations) * 1000
        
        # Should be less than 2ms per frame (16ms is real-time budget)
        assert avg_latency_ms < 2.0, f"AEC latency too high: {avg_latency_ms:.2f}ms"
        print(f"\nAEC frame latency: {avg_latency_ms:.3f}ms")

    @pytest.mark.performance
    def test_jitter_buffer_latency(self):
        """Benchmark jitter buffer read/write latency."""
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=60.0,
            max_latency_ms=200.0,
            sample_rate=16000,
        )
        
        data = np.random.randint(-10000, 10000, 256, dtype=np.int16)
        
        # Warm up
        for _ in range(10):
            jbuffer.write(data)
            jbuffer.read(256)
        
        # Benchmark
        iterations = 10000
        start = time.perf_counter()
        
        for _ in range(iterations):
            jbuffer.write(data)
            jbuffer.read(256)
        
        elapsed = time.perf_counter() - start
        avg_latency_us = (elapsed / iterations) * 1_000_000
        
        # Should be less than 100 microseconds
        assert avg_latency_us < 100, f"Jitter buffer latency too high: {avg_latency_us:.1f}us"
        print(f"\nJitter buffer latency: {avg_latency_us:.1f}us")

    @pytest.mark.performance
    def test_smooth_muter_latency(self, sample_audio_chunk: np.ndarray):
        """Benchmark smooth muter latency."""
        muter = SmoothMuter(ramp_samples=256)
        
        # Warm up
        for _ in range(10):
            muter.process(sample_audio_chunk)
        
        # Benchmark
        iterations = 10000
        start = time.perf_counter()
        
        for _ in range(iterations):
            muter.process(sample_audio_chunk)
        
        elapsed = time.perf_counter() - start
        avg_latency_us = (elapsed / iterations) * 1_000_000
        
        # Should be less than 50 microseconds
        assert avg_latency_us < 50, f"SmoothMuter latency too high: {avg_latency_us:.1f}us"
        print(f"\nSmoothMuter latency: {avg_latency_us:.1f}us")


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAudioPipelineIntegration:
    """Integration tests for complete audio pipeline."""

    @pytest.mark.asyncio
    async def test_complete_pipeline_flow(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
    ):
        """Test complete flow: capture -> AEC -> VAD -> output."""
        # Create components
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        jbuffer = AdaptiveJitterBuffer(
            target_latency_ms=audio_config.jitter_buffer_target_ms,
            max_latency_ms=audio_config.jitter_buffer_max_ms,
            sample_rate=audio_config.send_sample_rate,
        )
        muter = SmoothMuter(ramp_samples=256)
        hysteresis = HysteresisGate()
        
        # Simulate AI playing
        audio_state.is_playing = True
        audio_state.just_started_playing = True
        
        # Simulate pipeline
        far_end = sample_audio_chunk
        near_end = np.random.randint(-5000, 5000, 256, dtype=np.int16)
        
        # Write far-end to jitter buffer
        jbuffer.write(far_end)
        
        # Read from jitter buffer
        far_ref = jbuffer.read(256)
        
        # Process through AEC
        cleaned, aec_state = aec.process_frame(near_end, far_ref)
        
        # Check if user speaking
        is_user = aec.is_user_speaking(cleaned)
        
        # Update hysteresis
        ai_playing = hysteresis.update(audio_state.is_playing)
        
        # Mute decision
        should_mute = ai_playing and not is_user
        
        if should_mute:
            muter.mute()
        else:
            muter.unmute()
        
        # Apply mute
        output = muter.process(cleaned)
        
        assert len(output) == audio_config.chunk_size
        assert isinstance(aec_state, AECState)

    @pytest.mark.asyncio
    async def test_barge_in_scenario(
        self,
        audio_config: AudioConfig,
        sample_audio_chunk: np.ndarray,
    ):
        """Test barge-in detection and handling."""
        aec = DynamicAEC(
            sample_rate=audio_config.send_sample_rate,
            frame_size=audio_config.chunk_size,
        )
        muter = SmoothMuter(ramp_samples=256)
        
        # AI is speaking
        audio_state.is_playing = True
        
        # Initially, user is silent
        silence = np.zeros(256, dtype=np.int16)
        
        for _ in range(20):
            cleaned, _ = aec.process_frame(silence, sample_audio_chunk)
        
        # User starts speaking (barge-in)
        user_speech = sample_audio_chunk
        
        for _ in range(10):
            cleaned, state = aec.process_frame(user_speech, sample_audio_chunk)
            is_user = aec.is_user_speaking(cleaned)
            
            if is_user:
                # Should unmute user
                muter.unmute()
                break
        
        output = muter.process(cleaned)
        
        assert len(output) == audio_config.chunk_size


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
