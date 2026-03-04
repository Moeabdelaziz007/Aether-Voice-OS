"""
Aether Cortex — Focus Detection (Zen Mode) Benchmark.

Evaluates the ParalinguisticAnalyzer against synthetic and sampled audio signatures:
- Typing (Zen Mode: True)
- Speech (Zen Mode: False)
- Silence (Zen Mode: False)

Usage:
    PYTHONPATH="." python3 benchmarks/bench_focus.py
"""

import os
import sys
import wave

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Ensure core is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.audio.paralinguistics import ParalinguisticAnalyzer


def generate_typing_chunk(sr=16000, duration=1.0, count=5):
    """Generates audio with sharp spikes (typing simulation)."""
    samples = int(sr * duration)
    audio = np.random.normal(0, 50, samples).astype(np.int16)

    # Add sharp spikes
    for _ in range(count):
        pos = np.random.randint(0, samples - 100)
        audio[pos : pos + 10] = np.random.randint(10000, 30000, 10, dtype=np.int16)
    return audio


def generate_speech_chunk(sr=16000, duration=1.0):
    """Generates audio with lower freq oscillations (speech simulation)."""
    samples = int(sr * duration)
    t = np.linspace(0, duration, samples)
    # Fundamental + harmonics
    audio = (10000 * np.sin(2 * np.pi * 150 * t)).astype(np.int16)
    audio += (5000 * np.sin(2 * np.pi * 300 * t)).astype(np.int16)
    return audio


def generate_silence_chunk(sr=16000, duration=1.0):
    """Generates low-level noise (silence)."""
    samples = int(sr * duration)
    return np.random.normal(0, 10, samples).astype(np.int16)


def _label_from_filename(name: str) -> int | None:
    lower = name.lower()
    if "zen" in lower or "typing" in lower or "focus" in lower:
        return 1
    if "speech" in lower or "talk" in lower or "voice" in lower:
        return 0
    if "silence" in lower or "quiet" in lower:
        return 0
    return None


def _load_real_frames(path: str, frame_samples: int = 1600) -> list[np.ndarray]:
    try:
        with wave.open(path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                return []
            if wf.getframerate() != 16000:
                return []
            raw = wf.readframes(wf.getnframes())
    except Exception:
        return []

    pcm = np.frombuffer(raw, dtype=np.int16)
    frames = []
    for i in range(0, len(pcm) - frame_samples + 1, frame_samples):
        frames.append(pcm[i : i + frame_samples])
    return frames


def run_benchmark():
    analyzer = ParalinguisticAnalyzer()
    y_true = []
    y_pred = []

    real_dir = os.getenv("AETHER_FOCUS_REAL_DATA_DIR")
    use_real = bool(real_dir and os.path.isdir(real_dir))
    total_frames = 0

    print("=" * 60)
    print("🧠 Aether Focus Benchmark: Zen Mode Accuracy & F1")
    print("   Frame Size: 100ms")
    print("=" * 60)

    if use_real:
        for name in sorted(os.listdir(real_dir)):
            label = _label_from_filename(name)
            if label is None:
                continue
            frames = _load_real_frames(os.path.join(real_dir, name))
            for i, chunk in enumerate(frames):
                rms = np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2))
                features = analyzer.analyze(chunk, rms)
                if label == 1 and i <= 5:
                    continue
                y_true.append(label)
                y_pred.append(1 if features.zen_mode else 0)
                total_frames += 1
    else:
        for _ in range(50):
            for _ in range(10):
                chunk = generate_silence_chunk(duration=0.1)
                rms = np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2))
                features = analyzer.analyze(chunk, rms)
                y_true.append(0)
                y_pred.append(1 if features.zen_mode else 0)
                total_frames += 1

        for _ in range(50):
            for _ in range(10):
                chunk = generate_speech_chunk(duration=0.1)
                rms = np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2))
                features = analyzer.analyze(chunk, rms)
                y_true.append(0)
                y_pred.append(1 if features.zen_mode else 0)
                total_frames += 1

        for _ in range(50):
            for i in range(20):
                count = 1 if np.random.random() > 0.4 else 0
                chunk = generate_typing_chunk(duration=0.1, count=count)
                rms = np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2))
                features = analyzer.analyze(chunk, rms)
                if i > 5:
                    y_true.append(1)
                    y_pred.append(1 if features.zen_mode else 0)
                    total_frames += 1

    print(f"   Running {total_frames} frames")

    # Calculate Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f"  Accuracy:  {acc * 100:>6.1f}%")
    print(f"  Precision: {prec * 100:>6.1f}%")
    print(f"  Recall:    {rec * 100:>6.1f}%")
    print(f"  F1 Score:  {f1 * 100:>6.1f}%")
    print("-" * 60)

    if acc >= 0.90 and f1 >= 0.85:
        print("✅ SUCCESS: Benchmark meets 'Competitive Edge' thresholds.")
    else:
        print("⚠️  WARNING: Performance below target thresholds.")
    print("=" * 60)


if __name__ == "__main__":
    run_benchmark()
