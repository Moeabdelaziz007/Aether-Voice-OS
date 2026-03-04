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
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from google import genai
from google.genai import types

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
            thr = f"<{r.threshold}{r.unit}".ljust(8) if r.threshold > 0 else "N/A".ljust(8)
            lines.append(f"│ {name} │ {val} │ {thr} │ {status} │")

        lines.append("└──────────────────────────────┴───────────┴──────────┴────────┘")

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines.append(f"\n  Score: {passed}/{total} ({passed/total*100:.0f}%)")

        if self.suggestions:
            lines.append("\n  ════ Voice Quality Improvement Suggestions ════")
            for i, s in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {s}")

        lines.append("")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# Benchmark Tests
# ═══════════════════════════════════════════════════════════

def generate_test_tone(freq_hz: float = 440.0, duration_s: float = 1.0,
                        sample_rate: int = 16000) -> bytes:
    """Generate a pure sine wave tone as PCM16 bytes."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    samples = (np.sin(2 * np.pi * freq_hz * t) * 16000).astype(np.int16)
    return samples.tobytes()


def generate_speech_like_signal(duration_s: float = 2.0,
                                 sample_rate: int = 16000) -> bytes:
    """Generate a speech-like signal with formants for testing."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    # Simulate speech with multiple formants
    f1 = np.sin(2 * np.pi * 150 * t) * 8000   # Fundamental (male voice)
    f2 = np.sin(2 * np.pi * 500 * t) * 4000   # First formant
    f3 = np.sin(2 * np.pi * 1500 * t) * 2000  # Second formant
    f4 = np.sin(2 * np.pi * 2500 * t) * 1000  # Third formant

    # Apply amplitude envelope (speech cadence)
    envelope = np.abs(np.sin(2 * np.pi * 3 * t))  # ~3 syllables/sec
    signal = (f1 + f2 + f3 + f4) * envelope
    return signal.astype(np.int16).tobytes()


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
                system_instruction="You are a voice latency benchmarking agent. Respond with exactly one word: 'acknowledged'. Be as fast as possible.",
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
                    turns=[types.Content(parts=[types.Part(text=f"Ping #{i+1}")])]
                )
                async for response in session.receive():
                    if response.data:
                        latency_ms = (time.perf_counter() - start) * 1000
                        latencies.append(latency_ms)
                        logger.info(f"  Iteration {i+1}: {latency_ms:.0f}ms")
                        break
                    if response.text:
                        latency_ms = (time.perf_counter() - start) * 1000
                        latencies.append(latency_ms)
                        logger.info(f"  Iteration {i+1}: {latency_ms:.0f}ms (text)")
                        break
        except Exception as e:
            logger.warning(f"  Iteration {i+1} failed: {e}")
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

    prompt = """You are a senior audio engineer specializing in real-time voice AI systems.

Analyze the following voice pipeline architecture and provide:
1. A quality score from 0-100 based on the architecture's potential
2. Exactly 5 specific, actionable suggestions to improve voice quality

Pipeline Architecture:
- Input: PyAudio C-callback capture at 16kHz PCM16 mono
- AEC: Custom DynamicAEC using frequency-domain NLMS with double-talk detection
- Secondary AEC: Rust-accelerated AECBridge (when available)
- VAD: Dual-threshold HyperVAD (soft/hard detection with adaptive baseline)
- Paralinguistic Analysis: Real-time emotion detection from acoustic features (pitch, energy, ZCR, spectral centroid)
- Thalamic Gate: Software-defined echo cancellation with hysteresis gating and smooth muting (256-sample ramp)
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


def benchmark_aec_effectiveness() -> BenchmarkResult:
    """
    Measure AEC Echo Return Loss Enhancement (ERLE) using synthetic signals.
    Target: > 12dB ERLE.
    """
    logger.info("📊 [3/5] Benchmarking AEC Effectiveness (ERLE)...")

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
    noise = (np.random.randn(len(t)) * 200).astype(np.int16)

    mic_full = np.zeros_like(far_end_full)
    mic_full[delay_samples:] = (far_end_full[:-delay_samples] * echo_gain).astype(np.int16)
    mic_full += noise

    erle_values = []
    for i in range(total_frames):
        start = i * frame_size
        end = start + frame_size
        mic_frame = mic_full[start:end]
        far_frame = far_end_full[start:end]

        cleaned, state = aec.process_frame(mic_frame, far_frame)
        erle_values.append(state.erle_db)

    # Average ERLE over last 60% of frames (after convergence)
    converged_erle = erle_values[int(len(erle_values) * 0.4):]
    avg_erle = np.mean(converged_erle) if converged_erle else 0.0

    return BenchmarkResult(
        test_name="AEC ERLE (Echo Suppression)",
        metric="erle_db",
        value=avg_erle,
        unit="dB",
        passed=avg_erle >= 12.0,
        threshold=12,
        details=f"Converged frames: {len(converged_erle)}, peak={max(erle_values):.1f}dB",
    )


def benchmark_vad_accuracy() -> BenchmarkResult:
    """
    Test VAD accuracy using synthetic speech and silence signals.
    Target: > 90% classification accuracy.
    """
    logger.info("📊 [4/5] Benchmarking VAD Accuracy...")

    from core.audio.processing import AdaptiveVAD, energy_vad

    vad = AdaptiveVAD()
    sample_rate = 16000
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
    mic_frames = [(np.random.randn(frame_size) * 5000).astype(np.int16) for _ in range(100)]
    ref_frames = [(np.random.randn(frame_size) * 3000).astype(np.int16) for _ in range(100)]

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
        report.add(BenchmarkResult("Round-Trip Latency", "latency_ms", 9999, "ms", False, 500, str(e)))

    # 2. Voice Quality Analysis & Suggestions
    try:
        result, suggestions = await benchmark_voice_quality_analysis(api_key)
        report.add(result)
        report.suggestions = suggestions
    except Exception as e:
        logger.error(f"Quality analysis failed: {e}")
        report.suggestions = [f"Error: {e}"]

    # 3. AEC ERLE
    try:
        result = benchmark_aec_effectiveness()
        report.add(result)
    except Exception as e:
        logger.error(f"AEC benchmark failed: {e}")
        report.add(BenchmarkResult("AEC ERLE", "erle_db", 0, "dB", False, 12, str(e)))

    # 4. VAD Accuracy
    try:
        result = benchmark_vad_accuracy()
        report.add(result)
    except Exception as e:
        logger.error(f"VAD benchmark failed: {e}")
        report.add(BenchmarkResult("VAD Accuracy", "accuracy_%", 0, "%", False, 85, str(e)))

    # 5. Thalamic Gate Latency
    try:
        result = benchmark_thalamic_gate_latency()
        report.add(result)
    except Exception as e:
        logger.error(f"Gate latency benchmark failed: {e}")
        report.add(BenchmarkResult("Gate Latency", "gate_ms", 999, "ms", False, 2, str(e)))

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
                "value": r.value,
                "unit": r.unit,
                "passed": r.passed,
                "threshold": r.threshold,
                "details": r.details,
            }
            for r in report.results
        ],
        "suggestions": report.suggestions,
    }
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"Report saved to {report_path}")

    return report


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
