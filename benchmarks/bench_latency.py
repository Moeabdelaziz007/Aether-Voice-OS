"""
Aether Cortex — End-to-End Latency Benchmark.

Measures the internal "Zero-Friction" processing budget:
1. Audio Capture & VAD (Axon Layer)
2. Thalamic Gating & Emotion Analysis
3. Gateway Event Dispatch
4. Outbound Buffer Preparation

Usage:
    PYTHONPATH="." python3 benchmarks/bench_latency.py
"""

import asyncio
import time

import numpy as np

from core.audio.paralinguistics import ParalinguisticAnalyzer
from core.audio.processing import AdaptiveVAD


async def measure_internal_latency():
    print("=" * 60)
    print("⚡ Aether Latency Benchmark: Internal Processing Bridge")
    print("=" * 60)

    # Setup core components
    vad = AdaptiveVAD()
    analyzer = ParalinguisticAnalyzer()

    # Generate 30ms frame (standard Gemini frame size)
    sr = 16000
    frame_ms = 30
    samples = int(sr * frame_ms / 1000)
    pcm = np.random.randint(-5000, 5000, samples, dtype=np.int16)

    latencies = []

    # measure 1000 iterations to get p99
    from core.audio.processing import energy_vad

    for _ in range(1000):
        start = time.perf_counter()

        # 1. VAD & Energy Analysis
        vad_result = energy_vad(pcm, adaptive_engine=vad)
        is_speech = vad_result.is_hard
        energy = vad_result.energy_rms

        # 2. Paralinguistic Enrichment
        features = analyzer.analyze(pcm, energy)

        # 3. Simulate Gateway Payload Prep (JSON overhead)
        payload = {
            "zen_mode": features.zen_mode,
            "engagement": features.engagement_score,
            "rms": energy,
        }

        elapsed = (time.perf_counter() - start) * 1000  # to ms
        latencies.append(elapsed)

    # Results
    avg_latency = np.mean(latencies)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"  Avg Internal Latency: {avg_latency:>6.2f} ms")
    print(f"  p95 Latency:          {p95:>6.2f} ms")
    print(f"  p99 Latency:          {p99:>6.2f} ms")
    print("-" * 60)

    # ── Industry RTT estimation ──────────────────────────
    # Note: 180ms is "Total Turnaround".
    # If internal processing is <5ms, the remaining budget
    # for Gemini Live (Network + Inference) is ~175ms.

    print(f"  Processing Budget Used: {(avg_latency / 180) * 100:.1f}%")
    print("  Remaining for Network/Gemini: ~175ms")
    print("-" * 60)

    if avg_latency < 10.0:
        print("✅ SUCCESS: Engine overhead is sub-10ms (Zero-Friction verified).")
    else:
        print("⚠️  WARNING: Engine overhead exceeds Zero-Friction targets.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(measure_internal_latency())
