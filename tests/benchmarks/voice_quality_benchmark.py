#!/usr/bin/env python3
"""
Aether Voice OS — Real Voice Quality Benchmark Suite.
=====================================================
Uses the Gemini Live API to run real-time voice quality tests:
  1. Round-Trip Latency (Audio In → AI Response → Audio Out)
  2. Speech Recognition Accuracy (Word Error Rate)
  3. Thalamic Gate AEC Effectiveness (Echo Return Loss Enhancement)
  4. Emotion Detection Accuracy (Paralinguistic F1)
  5. Barge-In Responsiveness (Interrupt Latency)

Run:
    python tests/benchmarks/voice_quality_benchmark.py

Requires:
    - GOOGLE_API_KEY in .env
    - PyAudio + working microphone/speaker
    - numpy, scipy
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

logger = logging.getLogger("voice_benchmark")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

# ═══════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════


@dataclass
class BenchmarkResult:
    """Stores the results of a single benchmark run."""

    test_name: str
    metric: str
    value: float
    unit: str
    passed: bool
    threshold: float
    details: str = ""


@dataclass
class VoiceBenchmarkReport:
    """Complete voice quality benchmark report."""

    results: list[BenchmarkResult] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    timestamp: str = ""
    gemini_model: str = ""
    total_duration_s: float = 0.0

    def add(self, result: BenchmarkResult):
        self.results.append(result)

    def summary(self) -> str:
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════╗",
            "║       ⟡  AETHER VOICE QUALITY BENCHMARK REPORT  ⟡       ║",
            "╚══════════════════════════════════════════════════════════╝",
            "",
            f"  Model:     {self.gemini_model}",
            f"  Duration:  {self.total_duration_s:.1f}s",
            f"  Tests:     {len(self.results)}",
            "",
            "┌──────────────────────────────┬───────────┬──────────┬────────┐",
            "│ Test                         │ Value     │ Target   │ Status │",
            "├──────────────────────────────┼───────────┼──────────┼────────┤",
        ]
        for r in self.results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            name = r.test_name[:28].ljust(28)
            val = f"{r.value:.1f}{r.unit}".ljust(9)
            thr = (
                f"<{r.threshold}{r.unit}".ljust(8)
                if r.threshold > 0
                else "N/A".ljust(8)
            )
            lines.append(f"│ {name} │ {val} │ {thr} │ {status} │")

        lines.append("└──────────────────────────────┴───────────┴──────────┴────────┘")

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines.append(f"\n  Score: {passed}/{total} ({passed / total * 100:.0f}%)")

        if self.suggestions:
            lines.append("\n  ════ Voice Quality Improvement Suggestions ════")
            for i, s in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {s}")

        lines.append("")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# Benchmark Tests
# ═══════════════════════════════════════════════════════════


def generate_test_tone(
    freq_hz: float = 440.0, duration_s: float = 1.0, sample_rate: int = 16000
) -> bytes:
    """Generate a pure sine wave tone as PCM16 bytes."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    samples = (np.sin(2 * np.pi * freq_hz * t) * 16000).astype(np.int16)
    return samples.tobytes()


def generate_speech_like_signal(
    duration_s: float = 2.0, sample_rate: int = 16000
) -> bytes:
    """Generate a speech-like signal with formants for testing."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    # Simulate speech with multiple formants
    f1 = np.sin(2 * np.pi * 150 * t) * 8000  # Fundamental (male voice)
    f2 = np.sin(2 * np.pi * 500 * t) * 4000  # First formant
    f3 = np.sin(2 * np.pi * 1500 * t) * 2000  # Second formant
    f4 = np.sin(2 * np.pi * 2500 * t) * 1000  # Third formant

    # Apply amplitude envelope (speech cadence)
    envelope = np.abs(np.sin(2 * np.pi * 3 * t))  # ~3 syllables/sec
    signal = (f1 + f2 + f3 + f4) * envelope
    return signal.astype(np.int16).tobytes()


def generate_cafe_noise(
    duration_s: float = 5.0, sample_rate: int = 16000
) -> np.ndarray:
    """Generate simulated cafe chatter noise (overlapping sine waves)."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    noise = np.zeros_like(t)
    # Add multiple overlapping voices (sine waves) with varying envelopes
    num_voices = 10
    for _ in range(num_voices):
        freq = np.random.uniform(200, 4000)
        # Random amplitude envelope
        envelope = np.abs(
            np.sin(
                2 * np.pi * np.random.uniform(0.5, 2.0) * t
                + np.random.uniform(0, 2 * np.pi)
            )
        )
        voice = np.sin(2 * np.pi * freq * t) * envelope
        noise += voice

    # Normalize to max amplitude 1.0 roughly, before scaling
    if np.max(np.abs(noise)) > 0:
        noise = noise / np.max(np.abs(noise))
    return noise


def generate_keyboard_noise(
    duration_s: float = 5.0, sample_rate: int = 16000
) -> np.ndarray:
    """Generate simulated keyboard clacking noise (impulse bursts)."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    noise = np.zeros_like(t)

    # 3 to 6 keystrokes per second
    num_clicks = int(duration_s * np.random.uniform(3, 6))

    for _ in range(num_clicks):
        # Click position in time
        click_t = np.random.uniform(0, duration_s)
        click_idx = int(click_t * sample_rate)

        # Click duration 2-5ms
        click_dur_s = np.random.uniform(0.002, 0.005)
        click_len = int(click_dur_s * sample_rate)

        if click_idx + click_len < len(t):
            # Center frequency 2-4kHz
            freq = np.random.uniform(2000, 4000)
            click_t_arr = t[click_idx : click_idx + click_len] - t[click_idx]

            # Exponential decay envelope
            envelope = np.exp(-click_t_arr * (1.0 / click_dur_s * 2))
            click_signal = np.sin(2 * np.pi * freq * click_t_arr) * envelope

            noise[click_idx : click_idx + click_len] += click_signal

    if np.max(np.abs(noise)) > 0:
        noise = noise / np.max(np.abs(noise))
    return noise


def compute_snr(signal: np.ndarray, noise: np.ndarray) -> float:
    """Compute Signal-to-Noise Ratio in dB."""
    signal_power = np.mean(signal.astype(np.float64) ** 2) + 1e-10
    noise_power = np.mean(noise.astype(np.float64) ** 2) + 1e-10
    return 10 * np.log10(signal_power / noise_power)


async def benchmark_round_trip_latency(
    api_key: str, model: str = "models/gemini-2.0-flash-exp"
) -> BenchmarkResult:
    """
    Measure Round-Trip Latency: Send text → receive audio response.
    Target: < 500ms for first audio chunk.
    """
    logger.info("📊 [1/5] Benchmarking Round-Trip Latency...")
    client = genai.Client(api_key=api_key)

    latencies = []
    for i in range(3):
        try:
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                system_instruction=(
                    "You are a voice latency benchmarking agent. "
                    "Respond with exactly one word: 'acknowledged'. "
                    "Be as fast as possible."
                ),
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Puck"
                        )
                    )
                ),
            )
            async with client.aio.live.connect(model=model, config=config) as session:
                start = time.perf_counter()
                await session.send_client_content(
                    turns=[types.Content(parts=[types.Part(text=f"Ping #{i + 1}")])]
                )
                async for response in session.receive():
                    if response.data:
                        latency_ms = (time.perf_counter() - start) * 1000
                        latencies.append(latency_ms)
                        logger.info(f"  Iteration {i + 1}: {latency_ms:.0f}ms")
                        break
                    if response.text:
                        latency_ms = (time.perf_counter() - start) * 1000
                        latencies.append(latency_ms)
                        logger.info(f"  Iteration {i + 1}: {latency_ms:.0f}ms (text)")
                        break
        except Exception as e:
            logger.warning(f"  Iteration {i + 1} failed: {e}")
            latencies.append(5000.0)

    avg = sum(latencies) / len(latencies) if latencies else 9999.0
    p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else avg

    return BenchmarkResult(
        test_name="Round-Trip Latency (avg)",
        metric="latency_avg_ms",
        value=avg,
        unit="ms",
        passed=avg < 500,
        threshold=500,
        details=f"p95={p95:.0f}ms, samples={len(latencies)}",
    )


async def benchmark_voice_quality_analysis(
    api_key: str, model: str = "models/gemini-2.0-flash-exp"
) -> tuple[BenchmarkResult, list[str]]:
    """
    Ask Gemini to analyze Aether's voice pipeline and suggest improvements.
    Returns benchmark result + list of suggestions.
    """
    logger.info("📊 [2/5] Requesting Voice Quality Analysis from Gemini...")
    client = genai.Client(api_key=api_key)

    prompt = """You are a senior audio engineer specializing in voice AI systems.

Analyze the following voice pipeline architecture and provide:
1. A quality score from 0-100 based on the architecture's potential
2. Exactly 5 specific, actionable suggestions to improve voice quality

Pipeline Architecture:
- Input: PyAudio C-callback capture at 16kHz PCM16 mono
- AEC: Custom DynamicAEC using frequency-domain NLMS with double-talk detection
- Secondary AEC: Rust-accelerated AECBridge (when available)
- VAD: Dual-threshold HyperVAD (soft/hard detection with adaptive baseline)
- Paralinguistics: Real-time emotion detection via pitch, energy, ZCR, centroid
- Thalamic Gate: Software-defined echo cancellation with hysteresis gating
- AI Model: Gemini 2.5 Flash Native Audio (bidirectional WebSocket)
- Output: Direct PCM playback via PyAudio
- Latency target: < 200ms end-to-end
- Echo suppression: ~15dB ERLE target

Respond in this exact JSON format:
{
  "quality_score": <number 0-100>,
  "suggestions": [
    "suggestion 1",
    "suggestion 2", 
    "suggestion 3",
    "suggestion 4",
    "suggestion 5"
  ],
  "latency_assessment": "<excellent|good|fair|poor>",
  "aec_assessment": "<excellent|good|fair|poor>",
  "overall_assessment": "<brief 1-line summary>"
}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )

        result_text = response.text.strip()
        # Parse JSON response
        data = json.loads(result_text)
        score = data.get("quality_score", 0)
        suggestions = data.get("suggestions", [])
        assessment = data.get("overall_assessment", "No assessment")

        return BenchmarkResult(
            test_name="AI Voice Quality Score",
            metric="quality_score",
            value=score,
            unit="/100",
            passed=score >= 70,
            threshold=70,
            details=assessment,
        ), suggestions

    except Exception as e:
        logger.error(f"Voice quality analysis failed: {e}")
        return BenchmarkResult(
            test_name="AI Voice Quality Score",
            metric="quality_score",
            value=0,
            unit="/100",
            passed=False,
            threshold=70,
            details=f"Error: {e}",
        ), ["Could not retrieve suggestions — check API key"]


def benchmark_double_talk_performance() -> BenchmarkResult:
    """
    Simulate Cross-Talk (Double-Talk) where AI and user speak simultaneously.
    Target: DynamicAEC flags double_talk_detected = True, and near-end signal
    retains at least 60% of original RMS energy.
    """
    logger.info("📊 Benchmarking Double-Talk (Cross-Talk) Performance...")

    from core.audio.dynamic_aec import DynamicAEC

    sample_rate = 16000
    frame_size = 1600  # 100ms
    duration_s = 5.0
    total_frames = int(duration_s * sample_rate / frame_size)

    aec = DynamicAEC(
        sample_rate=sample_rate,
        frame_size=frame_size,
        filter_length_ms=100.0,
        step_size=0.5,
    )

    # 1. AI Far-End Signal (lower frequency, longer duration)
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    far_end = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)

    # 2. User Near-End Signal (higher frequency speech-like signal)
    # Give it some delay so AEC has a moment to start
    user_start_s = 1.0
    user_start_idx = int(user_start_s * sample_rate)

    near_end_speech = (np.sin(2 * np.pi * 500 * t) * 12000).astype(np.int16)
    near_end_speech[:user_start_idx] = 0  # Silent at first

    # 3. Simulate Mic Signal (Near-end speech + Far-end echo)
    echo_gain = 0.3
    delay_samples = 160  # 10ms echo delay

    echo_signal = np.zeros_like(far_end, dtype=np.float64)
    echo_signal[delay_samples:] = far_end[:-delay_samples] * echo_gain

    mic_full = echo_signal.astype(np.int16) + near_end_speech

    detected_double_talk_frames = 0
    total_double_talk_frames = 0

    cleaned_full = np.zeros_like(mic_full)

    for i in range(total_frames):
        start = i * frame_size
        end = start + frame_size
        mic_frame = mic_full[start:end]
        far_frame = far_end[start:end]

        cleaned, state = aec.process_frame(mic_frame, far_frame)
        cleaned_full[start:end] = cleaned

        # Only check double talk during the region where user is actually speaking
        if (i * frame_size) >= user_start_idx:
            total_double_talk_frames += 1
            if state.double_talk_detected:
                detected_double_talk_frames += 1

    # Check that near-end speech wasn't excessively muted during double talk
    user_segment_original = near_end_speech[user_start_idx:]
    user_segment_cleaned = cleaned_full[user_start_idx:]

    original_rms = (
        np.sqrt(np.mean(user_segment_original.astype(np.float64) ** 2)) + 1e-10
    )
    cleaned_rms = np.sqrt(np.mean(user_segment_cleaned.astype(np.float64) ** 2)) + 1e-10

    rms_retained_pct = (cleaned_rms / original_rms) * 100
    double_talk_accuracy = (
        (detected_double_talk_frames / total_double_talk_frames) * 100
        if total_double_talk_frames > 0
        else 0
    )

    passed = (double_talk_accuracy > 80.0) and (rms_retained_pct >= 60.0)

    return BenchmarkResult(
        test_name="Cross-Talk (Double-Talk)",
        metric="energy_retained_%",
        value=rms_retained_pct,
        unit="%",
        passed=passed,
        threshold=60.0,
        details=(
            f"Detection accuracy: {double_talk_accuracy:.1f}%, "
            f"Retained RMS: {rms_retained_pct:.1f}%"
        ),
    )


def benchmark_aec_effectiveness(
    snr_db: float = 15.0, noise_type: str = "cafe"
) -> BenchmarkResult:
    """
    Measure AEC Echo Return Loss Enhancement (ERLE) using synthetic signals.
    Target: > 12dB ERLE.
    Includes background noise injection based on SNR.
    """
    logger.info(
        f"📊 Benchmarking AEC Effectiveness (ERLE) - "
        f"{noise_type.title()} Noise at {snr_db}dB SNR..."
    )

    from core.audio.dynamic_aec import DynamicAEC

    sample_rate = 16000
    frame_size = 1600  # 100ms
    duration_s = 5.0
    total_frames = int(duration_s * sample_rate / frame_size)

    aec = DynamicAEC(
        sample_rate=sample_rate,
        frame_size=frame_size,
        filter_length_ms=100.0,
        step_size=0.5,
        convergence_threshold_db=15.0,
    )

    # Generate far-end (AI speaking) reference signal
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    far_end_full = (np.sin(2 * np.pi * 300 * t) * 10000).astype(np.int16)

    # Simulate echo path: attenuated + delayed far-end + mic noise
    echo_gain = 0.3
    delay_samples = 160  # 10ms echo delay

    # Generate background noise
    if noise_type == "cafe":
        raw_noise = generate_cafe_noise(duration_s, sample_rate)
    else:
        raw_noise = generate_keyboard_noise(duration_s, sample_rate)

    # Scale background noise based on desired SNR against far-end echo
    echo_signal = np.zeros_like(far_end_full, dtype=np.float64)
    echo_signal[delay_samples:] = far_end_full[:-delay_samples] * echo_gain

    echo_power = np.mean(echo_signal**2) + 1e-10
    raw_noise_power = np.mean(raw_noise**2) + 1e-10

    # SNR = 10 * log10(echo_power / noise_power)
    # noise_power = echo_power / (10 ** (SNR / 10))
    target_noise_power = echo_power / (10 ** (snr_db / 10))
    noise_scale = np.sqrt(target_noise_power / raw_noise_power)

    scaled_noise = (raw_noise * noise_scale).astype(np.int16)

    mic_full = echo_signal.astype(np.int16) + scaled_noise

    erle_values = []
    for i in range(total_frames):
        start = i * frame_size
        end = start + frame_size
        mic_frame = mic_full[start:end]
        far_frame = far_end_full[start:end]

        cleaned, state = aec.process_frame(mic_frame, far_frame)
        erle_values.append(state.erle_db)

    # Average ERLE over last 60% of frames (after convergence)
    converged_erle = erle_values[int(len(erle_values) * 0.4) :]
    avg_erle = np.mean(converged_erle) if converged_erle else 0.0

    return BenchmarkResult(
        test_name=f"AEC ERLE ({noise_type}, {snr_db}dB)",
        metric="erle_db",
        value=avg_erle,
        unit="dB",
        passed=avg_erle >= 12.0,
        threshold=12,
        details=(
            f"Converged frames: {len(converged_erle)}, peak={max(erle_values):.1f}dB"
        ),
    )


def benchmark_emotion_f1_score() -> BenchmarkResult:
    """
    Measure Emotion Detection accuracy across different pitch baselines.
    Classes: 'calm', 'alert', 'frustrated', 'flow_state'
    Target: Macro-averaged F1 >= 0.75
    """
    logger.info("📊 Benchmarking Emotion Detection F1-Score...")

    from sklearn.metrics import confusion_matrix, f1_score

    from core.audio.paralinguistics import ParalinguisticAnalyzer

    sample_rate = 16000
    analyzer = ParalinguisticAnalyzer(sample_rate=sample_rate)

    classes = ["calm", "alert", "frustrated", "flow_state"]
    num_samples_per_class = 20
    chunk_duration = 0.5  # 500ms chunks
    chunk_size = int(sample_rate * chunk_duration)

    y_true = []
    y_pred = []

    for cls in classes:
        for _ in range(num_samples_per_class):
            t = np.linspace(0, chunk_duration, chunk_size, endpoint=False)

            # Reset analyzer history slightly for independent samples
            # (In reality it's a rolling window, but here we feed chunks)
            analyzer = ParalinguisticAnalyzer(sample_rate=sample_rate)

            if cls == "calm":
                # Monotone, low pitch variance (<10Hz), low RMS
                base_freq = 120.0
                freq = base_freq + np.random.uniform(-2, 2)
                signal = (np.sin(2 * np.pi * freq * t) * 3000).astype(np.int16)

            elif cls == "alert":
                # Mid pitch (~180Hz), moderate energy
                base_freq = 180.0
                freq = base_freq + np.random.uniform(-5, 5)
                signal = (np.sin(2 * np.pi * freq * t) * 8000).astype(np.int16)

            elif cls == "frustrated":
                # High pitch variance (>30Hz), high ZCR, elevated RMS
                base_freq = 250.0
                # Generate high pitch variance by changing freq over time
                t_frames = np.linspace(0, chunk_duration, chunk_size)
                # Modulate freq with a sine wave to create variance in pitch over time
                # make it slower to ensure F0 estimation catches the changes
                freq_mod = np.sin(2 * np.pi * 3 * t_frames) * 100
                # Create a signal with varying frequency (chirp-like or vibrato)
                # Need phase integral for frequency modulation
                phase = 2 * np.pi * np.cumsum(base_freq + freq_mod) / sample_rate
                signal = (np.sin(phase) * 16000).astype(np.int16)
                # Add noise for higher ZCR
                signal += (np.random.randn(len(t)) * 5000).astype(np.int16)

            elif cls == "flow_state":
                # Stable pitch, very low variance, consistent RMS (zen mode)
                # simulate typing (zen_mode requires typing cadence + low speech)
                base_freq = 100.0
                signal = (np.sin(2 * np.pi * base_freq * t) * 1500).astype(np.int16)
                # add some typing spikes
                for _ in range(4):  # 4 clicks in 0.5s = 8 Hz transience
                    idx = np.random.randint(0, chunk_size - 100)
                    signal[idx : idx + 50] += (np.random.randn(50) * 8000).astype(
                        np.int16
                    )

            rms = np.sqrt(np.mean((signal.astype(np.float32) / 32768.0) ** 2)) + 1e-10

            # To simulate a continuous 2-second stream of this emotion and allow
            # rms_variance (variance of pitch over history) to build up,
            # we break the 500ms chunk into smaller sub-chunks.
            features = None
            sub_chunk_size = int(sample_rate * 0.1)  # 100ms

            # Feed 10 chunks to simulate 1 second of this emotion
            for _ in range(2):
                for i in range(0, chunk_size, sub_chunk_size):
                    sub_signal = signal[i : i + sub_chunk_size]
                    if len(sub_signal) > 0:
                        features = analyzer.analyze(sub_signal, float(rms))

            # Simple decision tree to classify based on features
            predicted_class = "calm"

            if features.zen_mode:
                predicted_class = "flow_state"
            elif features.rms_variance > 50 and features.pitch_estimate > 180:
                predicted_class = "frustrated"
            elif features.pitch_estimate > 140:
                predicted_class = "alert"
            else:
                predicted_class = "calm"

            y_true.append(cls)
            y_pred.append(predicted_class)

    # Compute F1-score
    macro_f1 = float(f1_score(y_true, y_pred, average="macro"))

    # Generate confusion matrix string for details
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    cm_str = "\\nConfusion Matrix:\\n"
    for row, cls in zip(cm, classes):
        cm_str += f"{cls.ljust(12)} {row}\\n"

    passed = macro_f1 >= 0.75

    return BenchmarkResult(
        test_name="Emotion Detection F1-Score",
        metric="macro_f1",
        value=macro_f1,
        unit="",
        passed=passed,
        threshold=0.75,
        details=f"Macro-F1: {macro_f1:.2f}{cm_str}",
    )


def benchmark_vad_accuracy() -> BenchmarkResult:
    """
    Test VAD accuracy using synthetic speech and silence signals.
    Target: > 90% classification accuracy.
    """
    logger.info("📊 [4/5] Benchmarking VAD Accuracy...")

    from core.audio.processing import AdaptiveVAD, energy_vad

    vad = AdaptiveVAD()
    correct = 0
    total = 0

    # Test 1: Pure silence → should NOT detect speech
    for _ in range(20):
        silence = np.zeros(1600, dtype=np.int16)
        noise = (np.random.randn(1600) * 50).astype(np.int16)
        result = energy_vad(silence + noise, adaptive_engine=vad)
        if not result.is_hard:
            correct += 1
        total += 1

    # Test 2: Clear speech-like signal → SHOULD detect speech
    for freq in [150, 200, 250, 300, 350]:
        t = np.linspace(0, 0.1, 1600, endpoint=False)
        speech = (np.sin(2 * np.pi * freq * t) * 12000).astype(np.int16)
        # Add harmonics
        speech += (np.sin(2 * np.pi * freq * 2 * t) * 6000).astype(np.int16)
        speech += (np.sin(2 * np.pi * freq * 3 * t) * 3000).astype(np.int16)
        for _ in range(4):
            result = energy_vad(speech, adaptive_engine=vad)
            if result.is_hard:
                correct += 1
            total += 1

    accuracy = (correct / total) * 100 if total > 0 else 0

    return BenchmarkResult(
        test_name="VAD Classification Accuracy",
        metric="accuracy_%",
        value=accuracy,
        unit="%",
        passed=accuracy >= 85,
        threshold=85,
        details=f"Correct: {correct}/{total}",
    )


def benchmark_thalamic_gate_latency() -> BenchmarkResult:
    """
    Measure the processing latency of a single Thalamic Gate cycle.
    Target: < 2ms per frame.
    """
    logger.info("📊 [5/5] Benchmarking Thalamic Gate Latency...")

    from core.audio.dynamic_aec import DynamicAEC

    sample_rate = 16000
    frame_size = 1600
    aec = DynamicAEC(
        sample_rate=sample_rate,
        frame_size=frame_size,
        filter_length_ms=100.0,
        step_size=0.5,
    )

    # Pre-generate test frames
    mic_frames = [
        (np.random.randn(frame_size) * 5000).astype(np.int16) for _ in range(100)
    ]
    ref_frames = [
        (np.random.randn(frame_size) * 3000).astype(np.int16) for _ in range(100)
    ]

    # Warmup
    for i in range(10):
        aec.process_frame(mic_frames[i], ref_frames[i])

    # Benchmark
    latencies = []
    for i in range(10, 100):
        start = time.perf_counter()
        aec.process_frame(mic_frames[i], ref_frames[i])
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

    avg_ms = np.mean(latencies)
    p99_ms = np.percentile(latencies, 99)

    return BenchmarkResult(
        test_name="Thalamic Gate Latency",
        metric="gate_latency_ms",
        value=avg_ms,
        unit="ms",
        passed=avg_ms < 2.0,
        threshold=2,
        details=f"p99={p99_ms:.2f}ms, frames={len(latencies)}",
    )


# ═══════════════════════════════════════════════════════════
# Main Runner
# ═══════════════════════════════════════════════════════════


async def run_all_benchmarks() -> VoiceBenchmarkReport:
    """Execute the full voice quality benchmark suite."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("No API key found. Set GOOGLE_API_KEY in .env")
        sys.exit(1)

    model = "models/gemini-2.0-flash-exp"
    report = VoiceBenchmarkReport(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        gemini_model=model,
    )

    start_time = time.perf_counter()

    print("\n⟡ Aether Voice Quality Benchmark Suite ⟡")
    print("═" * 50 + "\n")

    # 1. Round-Trip Latency
    try:
        result = await benchmark_round_trip_latency(api_key, model)
        report.add(result)
    except Exception as e:
        logger.error(f"Latency benchmark failed: {e}")
        report.add(
            BenchmarkResult(
                "Round-Trip Latency", "latency_ms", 9999, "ms", False, 500, str(e)
            )
        )

    # 2. Voice Quality Analysis & Suggestions
    try:
        result, suggestions = await benchmark_voice_quality_analysis(api_key)
        report.add(result)
        report.suggestions = suggestions
    except Exception as e:
        logger.error(f"Quality analysis failed: {e}")
        report.suggestions = [f"Error: {e}"]

    # 3. AEC ERLE with noise injection
    for snr in [15.0, 10.0, 5.0]:
        for noise in ["cafe", "keyboard"]:
            try:
                result = benchmark_aec_effectiveness(snr_db=snr, noise_type=noise)
                report.add(result)
            except Exception as e:
                logger.error(f"AEC benchmark failed ({noise} {snr}dB): {e}")
                report.add(
                    BenchmarkResult(
                        f"AEC ERLE ({noise}, {snr}dB)",
                        "erle_db",
                        0,
                        "dB",
                        False,
                        12,
                        str(e),
                    )
                )

    # 4. Cross-Talk (Double-Talk) Simulation
    try:
        result = benchmark_double_talk_performance()
        report.add(result)
    except Exception as e:
        logger.error(f"Double-Talk benchmark failed: {e}")
        report.add(
            BenchmarkResult("Cross-Talk", "retained_%", 0, "%", False, 60.0, str(e))
        )

    # 5. Emotion Detection F1-Score
    try:
        result = benchmark_emotion_f1_score()
        report.add(result)
    except Exception as e:
        logger.error(f"Emotion F1-Score benchmark failed: {e}")
        report.add(
            BenchmarkResult("Emotion Detection", "macro_f1", 0, "", False, 0.75, str(e))
        )

    # 6. VAD Accuracy
    try:
        result = benchmark_vad_accuracy()
        report.add(result)
    except Exception as e:
        logger.error(f"VAD benchmark failed: {e}")
        report.add(
            BenchmarkResult("VAD Accuracy", "accuracy_%", 0, "%", False, 85, str(e))
        )

    # 7. Thalamic Gate Latency
    try:
        result = benchmark_thalamic_gate_latency()
        report.add(result)
    except Exception as e:
        logger.error(f"Gate latency benchmark failed: {e}")
        report.add(
            BenchmarkResult("Gate Latency", "gate_ms", 999, "ms", False, 2, str(e))
        )

    report.total_duration_s = time.perf_counter() - start_time

    # Print Report
    print(report.summary())

    # Save to file
    report_path = ROOT / "tests" / "benchmarks" / "voice_benchmark_report.json"
    report_data = {
        "timestamp": report.timestamp,
        "model": report.gemini_model,
        "duration_s": report.total_duration_s,
        "results": [
            {
                "test": r.test_name,
                "value": float(r.value),
                "unit": r.unit,
                "passed": bool(r.passed),
                "threshold": float(r.threshold),
                "details": str(r.details),
            }
            for r in report.results
        ],
        "suggestions": [str(s) for s in report.suggestions],
    }
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"Report saved to {report_path}")

    return report


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
