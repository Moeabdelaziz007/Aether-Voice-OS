"""
Aether Cortex — DSP Benchmark: Rust vs NumPy

Compares the performance of Rust (aether_cortex) and NumPy
implementations for core DSP functions used in the live pipeline.

Usage (from project root):
    PYTHONPATH="." python3 benchmarks/bench_dsp.py
"""
import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core", "audio"))
# Optimization: Point directly to release artifact to bypass TCC move blocks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "aether-cortex", "target", "release"))

# ── Import Rust backend ──
try:
    import aether_cortex
    HAS_RUST = True
except ImportError:
    HAS_RUST = False

SAMPLE_RATE = 16_000
FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples
ITERATIONS = 10_000


def _numpy_energy_vad(pcm: np.ndarray, threshold: float = 0.02):
    """Pure NumPy VAD (baseline)."""
    if len(pcm) == 0:
        return {"is_speech": False, "energy_rms": 0.0, "sample_count": 0}
    normalized = pcm.astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(normalized ** 2)))
    return {"is_speech": rms > threshold, "energy_rms": rms, "sample_count": len(pcm)}


def _numpy_find_zero_crossing(pcm: np.ndarray, sr: int = 16000, ms: float = 20.0):
    """Pure NumPy zero-crossing (baseline)."""
    if len(pcm) < 2:
        return len(pcm)
    audio = pcm.astype(np.float32)
    lookahead = int(sr * ms / 1000)
    limit = min(len(audio) - 1, lookahead)
    signs = np.sign(audio[:limit + 1])
    crossings = np.where(signs[:-1] * signs[1:] <= 0)[0]
    if len(crossings) > 0:
        return int(crossings[0]) + 1
    return len(pcm)


def bench(name: str, fn, *args, iterations: int = ITERATIONS):
    """Run a function N times and report average latency."""
    # Warm up
    for _ in range(100):
        fn(*args)
    # Time
    start = time.perf_counter()
    for _ in range(iterations):
        fn(*args)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / iterations) * 1_000_000
    return name, avg_us


def main():
    print("=" * 60)
    print("🧬 Aether Cortex — DSP Benchmark")
    print(f"   Frame: {FRAME_MS}ms @ {SAMPLE_RATE}Hz = {FRAME_SAMPLES} samples")
    print(f"   Iterations: {ITERATIONS:,}")
    print(f"   Rust backend: {'✅ Available' if HAS_RUST else '❌ Not found'}")
    print("=" * 60)

    # Generate test data
    np.random.seed(42)
    pcm_speech = np.random.randint(-10000, 10000, size=FRAME_SAMPLES, dtype=np.int16)
    pcm_crossing = np.array(
        list(range(-200, 0)) + list(range(0, FRAME_SAMPLES - 200)),
        dtype=np.int16
    )[:FRAME_SAMPLES]

    results = []

    # ── energy_vad ──
    print("\n📊 energy_vad (Voice Activity Detection)")
    print("-" * 50)

    name, us = bench("NumPy", _numpy_energy_vad, pcm_speech)
    results.append((name, us))
    print(f"  {name:20s}: {us:8.2f} µs/call")

    if HAS_RUST:
        name, us_rust = bench("Rust (Synapse)", aether_cortex.energy_vad, pcm_speech, 0.02)
        results.append((name, us_rust))
        print(f"  {name:20s}: {us_rust:8.2f} µs/call")
        print(f"  {'Speedup':20s}: {us / us_rust:8.1f}x 🚀")

    # ── find_zero_crossing ──
    print("\n📊 find_zero_crossing (Audio Cut Point)")
    print("-" * 50)

    name, us = bench("NumPy", _numpy_find_zero_crossing, pcm_crossing)
    results.append((name, us))
    print(f"  {name:20s}: {us:8.2f} µs/call")

    if HAS_RUST:
        name, us_rust = bench("Rust (Axon)", aether_cortex.find_zero_crossing, pcm_crossing, 16000, 20.0)
        results.append((name, us_rust))
        print(f"  {name:20s}: {us_rust:8.2f} µs/call")
        print(f"  {'Speedup':20s}: {us / us_rust:8.1f}x 🚀")

    print("\n" + "=" * 60)
    if HAS_RUST:
        print("✅ Benchmark complete. Rust Synapse Layer is active.")
    else:
        print("⚠️  Rust backend not found. Only NumPy baselines shown.")
    print("=" * 60)


if __name__ == "__main__":
    main()
