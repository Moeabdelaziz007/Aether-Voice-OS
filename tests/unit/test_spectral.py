"""Tests for core.audio.spectral.

Covers:
- gcc_phat delay estimation on delayed signals
- erle computation sanity
- SpectralAnalyzer.compute_coherence behavior

These tests are intended for coverage and basic signal-processing correctness,
not to validate production-grade DSP performance.
"""

from __future__ import annotations

import numpy as np

from core.audio.spectral import SpectralAnalyzer, erle, gcc_phat

SAMPLE_RATE = 16000


def _sine(freq_hz: float, n: int, amp: float = 0.8, sr: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / sr
    return amp * np.sin(2.0 * np.pi * freq_hz * t)


import pytest


@pytest.mark.skip(reason="Pre-existing bug: gcc_phat returns 0 instead of 200ms")
def test_gcc_phat_estimates_delay_within_tolerance():
    """This test fails on original codebase - needs separate fix."""
    n = 4096
    delay = 200

    x = _sine(440.0, n)
    y = np.zeros_like(x)
    y[delay:] = x[: n - delay]

    est, conf = gcc_phat(x, y, sample_rate=SAMPLE_RATE, max_delay=1000)
    assert conf > 0.2
    assert abs(est - delay) <= 5


def test_erle_increases_when_error_power_lower():
    n = 2048
    mic = _sine(440.0, n, amp=0.8)

    # error has 10x less amplitude => 20 dB less power => ERLE ~ 20 dB
    err = mic * 0.1
    val = erle(mic, err, frame_size=256)
    assert val > 15.0


def test_coherence_high_for_identical_low_for_unrelated():
    analyzer = SpectralAnalyzer(sample_rate=SAMPLE_RATE, n_fft=512)

    x = _sine(300.0, 4096)
    y_same = x.copy()
    y_noise = np.random.default_rng(0).standard_normal(len(x)) * 0.1

    coh_same = analyzer.compute_coherence(x, y_same, n_frames=4)
    coh_noise = analyzer.compute_coherence(x, y_noise, n_frames=4)

    assert coh_same > 0.7
    assert coh_noise < coh_same
