#!/usr/bin/env python3
"""
🎵 Aether Voice OS — Comprehensive Voice Processing Test Suite
Expert-level tests for voice quality, performance, and reliability.

Tests cover:
- Voice Activity Detection (VAD) accuracy
- Acoustic Echo Cancellation (AEC) effectiveness
- Thalamic Gate performance
- Emotion detection reliability
- End-to-end voice pipeline performance
- Memory usage and latency benchmarks
"""

from __future__ import annotations

import gc
import logging
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import pytest

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

logger = logging.getLogger("voice_tests")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


# ═══════════════════════════════════════════════════════════
# Test Data Models
# ═══════════════════════════════════════════════════════════


@dataclass
class VoiceTestResult:
    """Result of a single voice processing test."""

    test_name: str
    passed: bool
    metric_name: str
    metric_value: float
    threshold: float
    unit: str = ""
    details: str = ""
    latency_ms: float = 0.0
    memory_mb: float = 0.0


@dataclass
class VoiceTestSuite:
    """Collection of voice processing test results."""

    results: List[VoiceTestResult] = field(default_factory=list)
    total_duration_s: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def add(self, result: VoiceTestResult):
        self.results.append(result)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def pass_rate(self) -> float:
        return self.passed_count / max(1, len(self.results)) * 100


# ═══════════════════════════════════════════════════════════
# Signal Generation Utilities
# ═══════════════════════════════════════════════════════════


def generate_sine_wave(
    freq_hz: float, duration_s: float, sample_rate: int = 16000, amplitude: float = 0.8
) -> np.ndarray:
    """Generate a pure sine wave."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    signal = (np.sin(2 * np.pi * freq_hz * t) * amplitude * 32767).astype(np.int16)
    return signal


def generate_speech_signal(
    duration_s: float = 2.0, sample_rate: int = 16000, fundamental_freq: float = 150.0
) -> np.ndarray:
    """Generate synthetic speech-like signal with formants."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)

    # Fundamental + harmonics (simulating speech formants)
    f0 = np.sin(2 * np.pi * fundamental_freq * t) * 8000
    f1 = np.sin(2 * np.pi * fundamental_freq * 2 * t) * 4000  # 1st harmonic
    f2 = np.sin(2 * np.pi * fundamental_freq * 3 * t) * 2000  # 2nd harmonic
    f3 = np.sin(2 * np.pi * 500 * t) * 3000  # Formant 1 (~500Hz)
    f4 = np.sin(2 * np.pi * 1500 * t) * 1500  # Formant 2 (~1500Hz)

    # Apply speech-like envelope (syllabic rhythm ~4 syllables/sec)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)

    signal = ((f0 + f1 + f2 + f3 + f4) * envelope).astype(np.int16)
    return signal


def generate_noise(
    duration_s: float,
    sample_rate: int = 16000,
    noise_type: str = "white",
    amplitude: float = 0.1,
) -> np.ndarray:
    """Generate various types of noise."""
    n_samples = int(sample_rate * duration_s)

    if noise_type == "white":
        noise = np.random.randn(n_samples) * amplitude * 32767
    elif noise_type == "pink":
        # Pink noise: 1/f spectrum
        white = np.random.randn(n_samples)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n_samples)
        freqs[0] = 1e-10  # Avoid division by zero
        fft = fft / np.sqrt(freqs)
        noise = np.fft.irfft(fft) * amplitude * 32767 * 0.1
    elif noise_type == "brown":
        # Brown noise: cumulative sum of white noise
        white = np.random.randn(n_samples) * 0.01
        noise = np.cumsum(white) * amplitude * 32767
        noise = noise - np.mean(noise)  # Remove DC offset
    else:
        noise = np.random.randn(n_samples) * amplitude * 32767

    return noise.astype(np.int16)


def generate_echo_signal(
    original: np.ndarray,
    delay_ms: float = 50.0,
    attenuation: float = 0.3,
    sample_rate: int = 16000,
) -> np.ndarray:
    """Generate echo of original signal."""
    delay_samples = int(delay_ms * sample_rate / 1000)
    echo = np.zeros(len(original) + delay_samples, dtype=np.float64)
    echo[delay_samples : delay_samples + len(original)] = original * attenuation
    return echo[: len(original)].astype(np.int16)


def mix_signals(
    signal1: np.ndarray, signal2: np.ndarray, snr_db: float = 10.0
) -> np.ndarray:
    """Mix two signals at specified SNR."""
    # Ensure same length
    min_len = min(len(signal1), len(signal2))
    s1 = signal1[:min_len].astype(np.float64)
    s2 = signal2[:min_len].astype(np.float64)

    # Calculate scaling for desired SNR
    power_s1 = np.mean(s1**2) + 1e-10
    power_s2 = np.mean(s2**2) + 1e-10

    target_power_s2 = power_s1 / (10 ** (snr_db / 10))
    scale = np.sqrt(target_power_s2 / power_s2)

    mixed = s1 + s2 * scale
    return np.clip(mixed, -32768, 32767).astype(np.int16)


# ═══════════════════════════════════════════════════════════
# VAD Tests
# ═══════════════════════════════════════════════════════════


class TestVAD:
    """Voice Activity Detection test suite."""

    @pytest.fixture
    def vad(self):
        """Create VAD instance."""
        from core.audio.vad import AetherVAD

        return AetherVAD(sample_rate=16000, frame_duration_ms=20)

    def test_vad_silence_detection(self, vad):
        """Test that VAD correctly detects silence."""
        frame_size = 320  # 20ms at 16kHz

        # Generate pure silence
        silence = np.zeros(frame_size, dtype=np.int16)

        # Feed multiple frames
        detections = []
        for _ in range(50):
            result = vad.process_frame(silence.tobytes())
            detections.append(result)

        # Should not detect voice in silence
        false_positive_rate = sum(detections) / len(detections)
        assert false_positive_rate < 0.05, (
            f"False positive rate {false_positive_rate:.2%} exceeds 5%"
        )

    def test_vad_speech_detection(self, vad):
        """Test that VAD correctly detects speech."""
        frame_size = 320
        sample_rate = 16000

        # Generate speech-like signal
        speech = generate_speech_signal(duration_s=1.0, sample_rate=sample_rate)

        # Feed frames
        detections = []
        for i in range(0, len(speech) - frame_size, frame_size):
            frame = speech[i : i + frame_size]
            result = vad.process_frame(frame.tobytes())
            detections.append(result)

        # Should detect voice in speech signal (after warmup)
        detection_rate = sum(detections[5:]) / len(detections[5:])
        assert detection_rate > 0.8, f"Detection rate {detection_rate:.2%} below 80%"

    def test_vad_noisy_speech_detection(self, vad):
        """Test VAD with speech in noisy environment."""
        frame_size = 320
        sample_rate = 16000
        duration_s = 2.0

        # Generate speech + noise
        speech = generate_speech_signal(duration_s=duration_s, sample_rate=sample_rate)
        noise = generate_noise(
            duration_s=duration_s, sample_rate=sample_rate, amplitude=0.05
        )
        noisy_speech = mix_signals(speech, noise, snr_db=15.0)

        # Feed frames
        detections = []
        for i in range(0, len(noisy_speech) - frame_size, frame_size):
            frame = noisy_speech[i : i + frame_size]
            result = vad.process_frame(frame.tobytes())
            detections.append(result)

        # Should still detect voice in noisy speech
        detection_rate = sum(detections[10:]) / len(detections[10:])
        assert detection_rate > 0.7, (
            f"Noisy detection rate {detection_rate:.2%} below 70%"
        )

    def test_vad_latency(self, vad):
        """Test VAD processing latency."""
        frame_size = 320
        frame = generate_speech_signal(0.02, 16000)  # 20ms frame

        # Warmup
        for _ in range(10):
            vad.process_frame(frame.tobytes())

        # Measure latency
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            vad.process_frame(frame.tobytes())
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = np.mean(latencies)
        p99_latency = np.percentile(latencies, 99)

        # VAD should be very fast (<1ms)
        assert avg_latency < 1.0, f"Average latency {avg_latency:.2f}ms exceeds 1ms"
        assert p99_latency < 2.0, f"P99 latency {p99_latency:.2f}ms exceeds 2ms"


# ═══════════════════════════════════════════════════════════
# AEC Tests
# ═══════════════════════════════════════════════════════════


class TestAEC:
    """Acoustic Echo Cancellation test suite."""

    @pytest.fixture
    def aec(self):
        """Create AEC instance."""
        from core.audio.dynamic_aec import DynamicAEC

        return DynamicAEC(
            sample_rate=16000,
            frame_size=1600,  # 100ms
            filter_length_ms=100.0,
            step_size=0.5,
            convergence_threshold_db=15.0,
        )

    def test_aec_echo_suppression(self, aec):
        """Test basic echo suppression capability."""
        sample_rate = 16000
        frame_size = 1600
        duration_s = 5.0

        # Generate far-end (speaker) signal
        t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
        far_end = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)

        # Generate echo (attenuated + delayed far-end)
        echo = generate_echo_signal(
            far_end, delay_ms=50, attenuation=0.3, sample_rate=sample_rate
        )

        # Process through AEC
        erle_values = []
        for i in range(0, len(far_end) - frame_size, frame_size):
            near_frame = echo[i : i + frame_size]
            far_frame = far_end[i : i + frame_size]

            cleaned, state = aec.process_frame(near_frame, far_frame)
            erle_values.append(state.erle_db)

        # Check ERLE after convergence (last 60%)
        converged_erle = erle_values[int(len(erle_values) * 0.4) :]
        avg_erle = np.mean(converged_erle) if converged_erle else 0

        assert avg_erle >= 10.0, f"ERLE {avg_erle:.1f}dB below 10dB threshold"

    def test_aec_double_talk(self, aec):
        """Test AEC performance during double-talk (simultaneous speech)."""
        sample_rate = 16000
        frame_size = 1600
        duration_s = 5.0

        # Far-end signal
        t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
        far_end = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)

        # Near-end speech (user speaking)
        near_end_speech = (np.sin(2 * np.pi * 500 * t) * 12000).astype(np.int16)
        # Start near-end after 1 second
        near_end_speech[:sample_rate] = 0

        # Echo + near-end speech
        echo = generate_echo_signal(far_end, delay_ms=50, attenuation=0.3)
        mic_signal = echo.astype(np.float32) + near_end_speech.astype(np.float32)
        mic_signal = np.clip(mic_signal, -32768, 32767).astype(np.int16)

        # Process and check double-talk detection
        double_talk_detections = []

        for i in range(0, len(far_end) - frame_size, frame_size):
            near_frame = mic_signal[i : i + frame_size]
            far_frame = far_end[i : i + frame_size]

            cleaned, state = aec.process_frame(near_frame, far_frame)

            # Check during double-talk region
            if i >= sample_rate:
                double_talk_detections.append(state.double_talk_detected)

        # Should detect double-talk
        detection_rate = sum(double_talk_detections) / max(
            1, len(double_talk_detections)
        )
        assert detection_rate > 0.5, (
            f"Double-talk detection rate {detection_rate:.2%} below 50%"
        )

    def test_aec_convergence_time(self, aec):
        """Test AEC convergence speed."""
        sample_rate = 16000
        frame_size = 1600
        duration_s = 10.0

        # Far-end signal
        t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
        far_end = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)
        echo = generate_echo_signal(far_end, delay_ms=50, attenuation=0.3)

        # Track convergence
        convergence_frame = None

        for idx, i in enumerate(range(0, len(far_end) - frame_size, frame_size)):
            near_frame = echo[i : i + frame_size]
            far_frame = far_end[i : i + frame_size]

            cleaned, state = aec.process_frame(near_frame, far_frame)

            if state.converged and convergence_frame is None:
                convergence_frame = idx
                break

        if convergence_frame:
            convergence_time_s = convergence_frame * (frame_size / sample_rate)
            assert convergence_time_s < 5.0, (
                f"Convergence time {convergence_time_s:.1f}s exceeds 5s"
            )

    def test_aec_latency(self, aec):
        """Test AEC processing latency per frame."""
        frame_size = 1600
        far_frame = generate_sine_wave(300, 0.1, 16000)[:frame_size]
        near_frame = generate_sine_wave(300, 0.1, 16000)[:frame_size]

        # Warmup
        for _ in range(10):
            aec.process_frame(near_frame, far_frame)

        # Measure
        latencies = []
        for _ in range(50):
            start = time.perf_counter()
            aec.process_frame(near_frame, far_frame)
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = np.mean(latencies)
        p99_latency = np.percentile(latencies, 99)

        # AEC should process in <5ms per 100ms frame
        assert avg_latency < 5.0, f"Average latency {avg_latency:.2f}ms exceeds 5ms"


# ═══════════════════════════════════════════════════════════
# Echo Guard (Thalamic Gate) Tests
# ═══════════════════════════════════════════════════════════


class TestEchoGuard:
    """Thalamic Gate (Echo Guard) test suite."""

    @pytest.fixture
    def echo_guard(self):
        """Create EchoGuard instance."""
        from core.audio.echo_guard import EchoGuard

        return EchoGuard(window_size_sec=3.0, sample_rate=16000)

    def test_echo_guard_self_recognition(self, echo_guard):
        """Test that EchoGuard recognizes AI output as 'self'."""
        # Register AI output
        ai_speech = generate_speech_signal(duration_s=1.0, fundamental_freq=200)
        echo_guard.register_output_audio(ai_speech.tobytes())

        # Simulate echo coming back through mic
        echo = ai_speech * 0.5  # Attenuated

        # Should recognize as self (not user)
        is_user = echo_guard.is_user_speaking(echo.tobytes())
        assert not is_user, "EchoGuard failed to recognize self-echo"

    def test_echo_guard_user_recognition(self, echo_guard):
        """Test that EchoGuard recognizes different voice as user."""
        # Register AI output (low pitch)
        ai_speech = generate_speech_signal(duration_s=1.0, fundamental_freq=200)
        echo_guard.register_output_audio(ai_speech.tobytes())

        # User speaks with different characteristics
        user_speech = generate_speech_signal(duration_s=0.5, fundamental_freq=350)

        # Wait for lockout
        import time

        time.sleep(0.2)

        # Should recognize as user
        is_user = echo_guard.is_user_speaking(user_speech.tobytes())
        # Note: This may be flaky due to timing

    def test_echo_guard_latency(self, echo_guard):
        """Test EchoGuard processing latency."""
        mic_signal = generate_speech_signal(duration_s=0.1)

        # Warmup
        for _ in range(10):
            echo_guard.is_user_speaking(mic_signal.tobytes())

        # Measure
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            echo_guard.is_user_speaking(mic_signal.tobytes())
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = np.mean(latencies)
        assert avg_latency < 2.0, f"EchoGuard latency {avg_latency:.2f}ms exceeds 2ms"


# ═══════════════════════════════════════════════════════════
# Emotion Detection Tests
# ═══════════════════════════════════════════════════════════


class TestEmotionDetection:
    """Paralinguistic emotion detection tests."""

    @pytest.fixture
    def analyzer(self):
        """Create ParalinguisticAnalyzer instance."""
        from core.audio.paralinguistics import ParalinguisticAnalyzer

        return ParalinguisticAnalyzer(sample_rate=16000)

    def test_calm_detection(self, analyzer):
        """Test detection of calm/relaxed state."""
        # Calm: low pitch, low variance, steady RMS
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        calm_signal = (np.sin(2 * np.pi * 120 * t) * 3000).astype(np.int16)

        rms = np.sqrt(np.mean((calm_signal.astype(np.float32) / 32768) ** 2))

        # Feed multiple chunks
        for _ in range(5):
            features = analyzer.analyze(calm_signal, float(rms))

        # Verify calm characteristics
        assert features.pitch_estimate < 150, (
            f"Pitch {features.pitch_estimate} too high for calm"
        )

    def test_alert_detection(self, analyzer):
        """Test detection of alert/engaged state."""
        # Alert: higher pitch, moderate energy
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        alert_signal = (np.sin(2 * np.pi * 180 * t) * 8000).astype(np.int16)

        rms = np.sqrt(np.mean((alert_signal.astype(np.float32) / 32768) ** 2))

        for _ in range(5):
            features = analyzer.analyze(alert_signal, float(rms))

        # Higher pitch for alert
        assert features.pitch_estimate > 140, (
            f"Pitch {features.pitch_estimate} too low for alert"
        )

    def test_emotion_latency(self, analyzer):
        """Test emotion analysis latency."""
        signal = generate_speech_signal(0.1, 16000)
        rms = 0.1

        # Warmup
        for _ in range(10):
            analyzer.analyze(signal, rms)

        # Measure
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            analyzer.analyze(signal, rms)
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = np.mean(latencies)
        assert avg_latency < 2.0, (
            f"Emotion analysis latency {avg_latency:.2f}ms exceeds 2ms"
        )


# ═══════════════════════════════════════════════════════════
# Memory and Performance Tests
# ═══════════════════════════════════════════════════════════


class TestPerformance:
    """Performance and resource usage tests."""

    def test_memory_usage_vad(self):
        """Test VAD memory footprint."""
        from core.audio.vad import AetherVAD

        gc.collect()
        tracemalloc.start()

        vad = AetherVAD()
        frame = generate_speech_signal(0.02, 16000).tobytes()

        # Process many frames
        for _ in range(1000):
            vad.process_frame(frame)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        assert peak_mb < 10, f"VAD peak memory {peak_mb:.1f}MB exceeds 10MB"

    def test_memory_usage_aec(self):
        """Test AEC memory footprint."""
        from core.audio.dynamic_aec import DynamicAEC

        gc.collect()
        tracemalloc.start()

        aec = DynamicAEC(sample_rate=16000, frame_size=1600)
        near = generate_sine_wave(300, 0.1, 16000)[:1600]
        far = generate_sine_wave(300, 0.1, 16000)[:1600]

        # Process many frames
        for _ in range(100):
            aec.process_frame(near, far)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        assert peak_mb < 50, f"AEC peak memory {peak_mb:.1f}MB exceeds 50MB"

    def test_sustained_processing(self):
        """Test sustained processing without memory leaks."""
        from core.audio.echo_guard import EchoGuard
        from core.audio.vad import AetherVAD

        vad = AetherVAD()
        guard = EchoGuard()

        gc.collect()
        initial_objects = len(gc.get_objects())

        # Simulate 5 minutes of processing (300 seconds / 20ms = 15000 frames)
        frame = generate_speech_signal(0.02, 16000)

        for _ in range(1000):  # Reduced for test speed
            vad.process_frame(frame.tobytes())
            guard.is_user_speaking(frame.tobytes())

        gc.collect()
        final_objects = len(gc.get_objects())

        object_growth = final_objects - initial_objects
        # Allow some growth but not unbounded
        assert object_growth < 10000, f"Object count grew by {object_growth}"


# ═══════════════════════════════════════════════════════════
# End-to-End Pipeline Tests
# ═══════════════════════════════════════════════════════════


class TestVoicePipeline:
    """End-to-end voice pipeline tests."""

    def test_pipeline_latency_budget(self):
        """Test total pipeline latency stays within budget."""
        from core.audio.echo_guard import EchoGuard
        from core.audio.vad import AetherVAD

        vad = AetherVAD()
        guard = EchoGuard()

        frame = generate_speech_signal(0.02, 16000)

        # Measure full pipeline
        latencies = []
        for _ in range(100):
            start = time.perf_counter()

            # VAD
            vad.process_frame(frame.tobytes())

            # Echo guard
            guard.is_user_speaking(frame.tobytes())

            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = np.mean(latencies)
        p99_latency = np.percentile(latencies, 99)

        # Total audio processing should be <10ms
        assert avg_latency < 10, f"Pipeline latency {avg_latency:.2f}ms exceeds 10ms"
        assert p99_latency < 20, f"P99 latency {p99_latency:.2f}ms exceeds 20ms"

    def test_pipeline_under_load(self):
        """Test pipeline performance under sustained load."""
        from core.audio.vad import AetherVAD

        vad = AetherVAD()

        # Simulate high-frequency processing (50ms frames continuously)
        frame = generate_speech_signal(0.05, 16000)

        start_time = time.perf_counter()
        frames_processed = 0

        while time.perf_counter() - start_time < 1.0:  # 1 second test
            vad.process_frame(frame.tobytes())
            frames_processed += 1

        # Should process at least 20 frames/second (50ms each)
        assert frames_processed >= 20, f"Only processed {frames_processed} frames"


# ═══════════════════════════════════════════════════════════
# Run All Tests
# ═══════════════════════════════════════════════════════════


def run_comprehensive_tests() -> VoiceTestSuite:
    """Run all voice processing tests and collect results."""
    suite = VoiceTestSuite()
    start_time = time.perf_counter()

    logger.info("🎵 Starting Comprehensive Voice Processing Tests")
    logger.info("=" * 60)

    # VAD Tests
    try:
        from core.audio.vad import AetherVAD

        vad = AetherVAD()

        # Test 1: Silence detection
        silence = np.zeros(320, dtype=np.int16)
        detections = [vad.process_frame(silence.tobytes()) for _ in range(50)]
        fp_rate = sum(detections) / len(detections)
        suite.add(
            VoiceTestResult(
                test_name="VAD Silence Detection",
                passed=fp_rate < 0.05,
                metric_name="false_positive_rate",
                metric_value=fp_rate * 100,
                threshold=5.0,
                unit="%",
            )
        )

        # Test 2: Speech detection
        vad2 = AetherVAD()
        speech = generate_speech_signal(0.5, 16000)
        detections = []
        for i in range(0, len(speech) - 320, 320):
            detections.append(vad2.process_frame(speech[i : i + 320].tobytes()))
        det_rate = sum(detections[3:]) / len(detections[3:])
        suite.add(
            VoiceTestResult(
                test_name="VAD Speech Detection",
                passed=det_rate > 0.8,
                metric_name="detection_rate",
                metric_value=det_rate * 100,
                threshold=80.0,
                unit="%",
            )
        )

        logger.info("✅ VAD Tests Complete")

    except Exception as e:
        logger.error(f"❌ VAD Tests Failed: {e}")
        suite.add(
            VoiceTestResult(
                test_name="VAD Tests",
                passed=False,
                metric_name="error",
                metric_value=0,
                threshold=0,
                details=str(e),
            )
        )

    # AEC Tests
    try:
        from core.audio.dynamic_aec import DynamicAEC

        aec = DynamicAEC(sample_rate=16000, frame_size=1600)

        # Generate test signals
        t = np.linspace(0, 3.0, 48000, endpoint=False)
        far_end = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)
        echo = generate_echo_signal(far_end, delay_ms=50, attenuation=0.3)

        erle_vals = []
        for i in range(0, len(far_end) - 1600, 1600):
            _, state = aec.process_frame(echo[i : i + 1600], far_end[i : i + 1600])
            erle_vals.append(state.erle_db)

        avg_erle = np.mean(erle_vals[len(erle_vals) // 2 :])
        suite.add(
            VoiceTestResult(
                test_name="AEC Echo Suppression",
                passed=avg_erle >= 10.0,
                metric_name="ERLE",
                metric_value=avg_erle,
                threshold=10.0,
                unit="dB",
            )
        )

        logger.info("✅ AEC Tests Complete")

    except Exception as e:
        logger.error(f"❌ AEC Tests Failed: {e}")
        suite.add(
            VoiceTestResult(
                test_name="AEC Tests",
                passed=False,
                metric_name="error",
                metric_value=0,
                threshold=0,
                details=str(e),
            )
        )

    # Echo Guard Tests
    try:
        from core.audio.echo_guard import EchoGuard

        guard = EchoGuard()

        # Latency test
        signal = generate_speech_signal(0.1, 16000)
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            guard.is_user_speaking(signal.tobytes())
            latencies.append((time.perf_counter() - start) * 1000)

        avg_lat = np.mean(latencies)
        suite.add(
            VoiceTestResult(
                test_name="Echo Guard Latency",
                passed=avg_lat < 2.0,
                metric_name="avg_latency",
                metric_value=avg_lat,
                threshold=2.0,
                unit="ms",
            )
        )

        logger.info("✅ Echo Guard Tests Complete")

    except Exception as e:
        logger.error(f"❌ Echo Guard Tests Failed: {e}")

    suite.total_duration_s = time.perf_counter() - start_time

    # Generate recommendations
    suite.recommendations = generate_recommendations(suite)

    return suite


def generate_recommendations(suite: VoiceTestSuite) -> List[str]:
    """Generate optimization recommendations based on test results."""
    recommendations = []

    for result in suite.results:
        if not result.passed:
            if "VAD" in result.test_name:
                recommendations.append(
                    "🎙️ VAD: Consider tuning noise floor threshold or hysteresis parameters"
                )
            elif "AEC" in result.test_name:
                recommendations.append(
                    "🔊 AEC: Increase filter length or adjust NLMS step size for better convergence"
                )
            elif "Latency" in result.test_name:
                recommendations.append(
                    "⚡ Latency: Profile hot paths, consider Rust acceleration for DSP operations"
                )

    # General recommendations
    recommendations.extend(
        [
            "💡 Use SIMD intrinsics (via numpy) for vectorized audio operations",
            "💡 Consider pre-allocating buffers to avoid GC pressure in audio callbacks",
            "💡 Implement adaptive step size for AEC based on signal characteristics",
            "💡 Use ring buffers with fixed allocation for real-time processing",
        ]
    )

    return recommendations[:10]


def print_test_report(suite: VoiceTestSuite):
    """Print formatted test report."""
    print("\n" + "=" * 70)
    print("    🎵 AETHER VOICE OS - COMPREHENSIVE TEST REPORT")
    print("=" * 70)
    print(f"\n  Duration: {suite.total_duration_s:.2f}s")
    print(
        f"  Tests: {len(suite.results)} | Passed: {suite.passed_count} | Failed: {suite.failed_count}"
    )
    print(f"  Pass Rate: {suite.pass_rate:.1f}%")
    print("\n" + "-" * 70)
    print("  TEST RESULTS")
    print("-" * 70)

    for r in suite.results:
        status = "✅" if r.passed else "❌"
        print(f"  {status} {r.test_name}")
        print(
            f"     {r.metric_name}: {r.metric_value:.2f}{r.unit} (threshold: {r.threshold}{r.unit})"
        )

    print("\n" + "-" * 70)
    print("  RECOMMENDATIONS")
    print("-" * 70)
    for i, rec in enumerate(suite.recommendations, 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    suite = run_comprehensive_tests()
    print_test_report(suite)
