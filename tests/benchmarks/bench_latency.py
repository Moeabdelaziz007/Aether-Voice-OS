"""
Aether Cortex — Latency Benchmark Harness.

Includes:
1. Internal processing latency (VAD + paralinguistics).
2. Chunk profile comparison for turn latency and WS message rate.

Usage:
    PYTHONPATH="." python3 tests/benchmarks/bench_latency.py
"""

import asyncio
import random
import statistics
import time
from dataclasses import dataclass

import numpy as np

from core.audio.paralinguistics import ParalinguisticAnalyzer
from core.audio.processing import AdaptiveVAD


@dataclass
class ChunkProfileResult:
    profile: str
    chunk_samples: int
    chunk_ms: float
    ws_msgs_per_second: float
    turn_latency_p50_ms: float
    turn_latency_p95_ms: float


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(values, p))


async def measure_internal_latency() -> None:
    print("=" * 72)
    print("⚡ Aether Latency Benchmark: Internal Processing")
    print("=" * 72)

    vad = AdaptiveVAD()
    analyzer = ParalinguisticAnalyzer()

    sr = 16000
    frame_ms = 30
    samples = int(sr * frame_ms / 1000)
    pcm = np.random.randint(-5000, 5000, samples, dtype=np.int16)

    latencies: list[float] = []

    from core.audio.processing import energy_vad

    for _ in range(1000):
        start = time.perf_counter()
        vad_result = energy_vad(pcm, adaptive_engine=vad)
        _ = analyzer.analyze(pcm, vad_result.energy_rms)
        elapsed = (time.perf_counter() - start) * 1000
        latencies.append(elapsed)

    avg_latency = statistics.mean(latencies)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    print(f"  Avg Internal Latency: {avg_latency:>6.2f} ms")
    print(f"  p95 Latency:          {p95:>6.2f} ms")
    print(f"  p99 Latency:          {p99:>6.2f} ms")
    print(f"  Processing Budget Used (180ms turn): {(avg_latency / 180) * 100:.1f}%")
    print("-" * 72)


async def compare_chunk_profiles(iterations: int = 600) -> None:
    """
    Browser-aligned chunk profile benchmark model.

    The model estimates end-to-end turn latency and WebSocket message rates
    across chunk sizes by combining:
    - Capture accumulation delay (chunk_ms)
    - Base network+model latency with jitter
    - Queue pressure penalties
    """
    print("📊 Chunk Profile Comparison (turn latency + WS msg rate)")

    profiles = {
        "ultra_low_latency": 512,
        "low_latency": 1024,
        "balanced": 2048,
        "bandwidth_saver": 4096,
    }

    results: list[ChunkProfileResult] = []

    for name, chunk_samples in profiles.items():
        chunk_ms = (chunk_samples / 16000) * 1000
        ws_msgs_per_second = 1000.0 / chunk_ms

        turn_latencies: list[float] = []
        queue_pressure = 0.0

        for _ in range(iterations):
            base_network_model_ms = random.gauss(125, 20)
            base_network_model_ms = max(70.0, min(220.0, base_network_model_ms))

            # Higher msg rate tends to increase queue pressure.
            pressure_drift = max(0.0, (ws_msgs_per_second - 16.0) * 0.4)
            queue_pressure = max(0.0, queue_pressure * 0.92 + pressure_drift + random.uniform(-1.0, 1.0))

            queue_penalty_ms = min(80.0, queue_pressure * 1.8)
            capture_penalty_ms = chunk_ms * 0.55

            turn_latency = base_network_model_ms + capture_penalty_ms + queue_penalty_ms
            turn_latencies.append(turn_latency)

        results.append(
            ChunkProfileResult(
                profile=name,
                chunk_samples=chunk_samples,
                chunk_ms=chunk_ms,
                ws_msgs_per_second=ws_msgs_per_second,
                turn_latency_p50_ms=percentile(turn_latencies, 50),
                turn_latency_p95_ms=percentile(turn_latencies, 95),
            )
        )

    print(f"{'Profile':<20} {'Chunk(ms)':>10} {'WS msg/s':>10} {'p50 turn(ms)':>14} {'p95 turn(ms)':>14}")
    print("-" * 72)
    for row in results:
        print(
            f"{row.profile:<20} {row.chunk_ms:>10.1f} {row.ws_msgs_per_second:>10.2f}"
            f" {row.turn_latency_p50_ms:>14.1f} {row.turn_latency_p95_ms:>14.1f}"
        )

    print("-" * 72)
    print("Recommendation:")
    print("  • Conversational default: 512–1024 samples (32–64ms)")
    print("  • Bandwidth-saver mode: 4096 samples (256ms)")
    print("=" * 72)


async def main() -> None:
    await measure_internal_latency()
    await compare_chunk_profiles()


if __name__ == "__main__":
    asyncio.run(main())
