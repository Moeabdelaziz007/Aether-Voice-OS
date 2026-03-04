"""Tests for core.audio.paralinguistics.

Validates feature extraction behavior:
- pitch estimation accuracy on known-frequency sines
- spectral centroid sanity
- multi-harmonic feature behavior
- edge cases (zeros, max amplitude, very short frames)

Note: ParalinguisticAnalyzer does not expose an RMS function; RMS is computed
externally where needed.
"""

from __future__ import annotations

import numpy as np

from core.audio.paralinguistics import ParalinguisticAnalyzer

SAMPLE_RATE = 16000


def _sine_pcm16(
    freq_hz: float, duration_s: float, amp: float, sr: int = SAMPLE_RATE
) -> np.ndarray:
    n = int(duration_s * sr)
    t = np.arange(n, dtype=np.float64) / sr
    x = amp * np.sin(2.0 * np.pi * freq_hz * t)
    return (np.clip(x, -1.0, 1.0) * 32767.0).astype(np.int16)


def _rms(pcm: np.ndarray) -> float:
    if len(pcm) == 0:
        return 0.0
    x = pcm.astype(np.float32) / 32768.0
    return float(np.sqrt(np.mean(x * x)))


def test_pitch_estimation_known_sines_within_tolerance():
    analyzer = ParalinguisticAnalyzer(sample_rate=SAMPLE_RATE)

    for f in (100.0, 200.0, 300.0, 440.0):
        pcm = _sine_pcm16(f, duration_s=0.2, amp=0.6)
        est = analyzer._estimate_pitch(pcm)
        assert est > 0
        assert abs(est - f) / f < 0.05, f"Pitch off for {f}Hz: got {est:.2f}Hz"


def test_spectral_centroid_is_near_tone_frequency_for_pure_sine():
    analyzer = ParalinguisticAnalyzer(sample_rate=SAMPLE_RATE)
    pcm = _sine_pcm16(400.0, duration_s=0.2, amp=0.6)
    res = analyzer.analyze(pcm, current_rms=_rms(pcm))

    # Loose tolerance due to FFT leakage/windowing.
    assert 200.0 <= res.spectral_centroid <= 800.0


def test_multi_harmonic_signal_has_centroid_above_fundamental():
    analyzer = ParalinguisticAnalyzer(sample_rate=SAMPLE_RATE)

    f0 = 200.0
    base = _sine_pcm16(f0, duration_s=0.2, amp=0.3).astype(np.int32)
    h2 = _sine_pcm16(2 * f0, duration_s=0.2, amp=0.2).astype(np.int32)
    h3 = _sine_pcm16(3 * f0, duration_s=0.2, amp=0.1).astype(np.int32)

    pcm = (base + h2 + h3).clip(-32768, 32767).astype(np.int16)
    res = analyzer.analyze(pcm, current_rms=_rms(pcm))

    assert res.pitch_estimate == 0.0 or abs(res.pitch_estimate - f0) / f0 < 0.08
    assert res.spectral_centroid > f0


def test_edge_cases_zeros_max_amp_and_very_short_frames():
    analyzer = ParalinguisticAnalyzer(sample_rate=SAMPLE_RATE)

    zeros = np.zeros(1600, dtype=np.int16)
    res0 = analyzer.analyze(zeros, current_rms=0.0)
    assert res0.pitch_estimate == 0
    assert 0.0 <= res0.engagement_score <= 1.0

    maxamp = np.full(1600, 32767, dtype=np.int16)
    res1 = analyzer.analyze(maxamp, current_rms=_rms(maxamp))
    assert np.isfinite(res1.spectral_centroid)

    short = np.zeros(32, dtype=np.int16)
    res2 = analyzer.analyze(short, current_rms=0.0)
    assert res2.pitch_estimate == 0
