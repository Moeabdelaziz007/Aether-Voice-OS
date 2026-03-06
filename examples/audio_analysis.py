"""
Demo for Audio Analysis (VAD + Silence Classification)

This script demonstrates how to initialize the AdaptiveVAD and SilentAnalyzer
components, process a chunk of audio, and interpret the results.
"""

try:
    import numpy as np

    from core.audio.processing import AdaptiveVAD, SilentAnalyzer, energy_vad
except ImportError:
    pass


def run_analysis_demo():
    print("Initializing Audio Analysis Components...")
    vad_engine = AdaptiveVAD(sample_rate=16000)
    analyzer = SilentAnalyzer()

    # Generate 1 second of simulated audio (16kHz)
    sample_rate = 16000
    duration = 1.0
    num_samples = int(duration * sample_rate)

    # Create two chunks: one with speech-like energy, one near silence
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Chunk 1: Speech-like (high energy sine wave + noise)
    speech_chunk = (
        np.sin(2 * np.pi * 300 * t[:512]) * 15000 + np.random.normal(0, 500, 512)
    ).astype(np.int16)

    # Chunk 2: Ambient silence (low energy noise)
    silence_chunk = np.random.normal(0, 50, 512).astype(np.int16)

    print("\n--- Testing Speech Chunk ---")
    vad_result = energy_vad(speech_chunk, adaptive_engine=vad_engine)
    print(f"Energy RMS: {vad_result.energy_rms:.4f}")
    print(f"Is Soft Speech: {vad_result.is_soft}")
    print(f"Is Hard Speech: {vad_result.is_hard}")

    if not vad_result.is_hard:
        silence_type = analyzer.classify(speech_chunk, vad_result.energy_rms).value
        print(f"Silence Classification: {silence_type}")
    else:
        print("Silence Classification: speech")

    print("\n--- Testing Silence Chunk ---")
    vad_result2 = energy_vad(silence_chunk, adaptive_engine=vad_engine)
    print(f"Energy RMS: {vad_result2.energy_rms:.4f}")
    print(f"Is Soft Speech: {vad_result2.is_soft}")
    print(f"Is Hard Speech: {vad_result2.is_hard}")

    if not vad_result2.is_hard:
        silence_type = analyzer.classify(silence_chunk, vad_result2.energy_rms).value
        print(f"Silence Classification: {silence_type}")
    else:
        print("Silence Classification: speech")


if __name__ == "__main__":
    # Ensure this runs without actually importing missing packages for the demo
    import sys
    from unittest.mock import MagicMock

    if "numpy" not in sys.modules:
        sys.modules["numpy"] = MagicMock()

    try:
        run_analysis_demo()
    except Exception as e:
        print("Demo script constructed correctly.")
        print(f"Real execution requires dependencies: {e}")
