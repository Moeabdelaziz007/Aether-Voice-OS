"""Tests for core.audio.processing VAD components.

Covers:
- AdaptiveVAD baseline adaptation
- energy_vad silence/speech behavior
- soft vs hard thresholding
- HyperVADResult fields
- SilentAnalyzer classification

These tests are written to tolerate the optional Rust backend by focusing
on semantic outcomes rather than exact numerical equality.
"""

from __future__ import annotations

import numpy as np

from core.audio.processing import (
    AdaptiveVAD,
    HyperVADResult,
    SilenceType,
    SilentAnalyzer,
    energy_vad,
)

SAMPLE_RATE = 16000
CHUNK_DURATION_S = 0.1
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_S)


def _sine_pcm16(
    freq_hz: float, amp: float, n: int = CHUNK_SAMPLES, sr: int = SAMPLE_RATE
) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / sr
    x = amp * np.sin(2.0 * np.pi * freq_hz * t)
    return (np.clip(x, -1.0, 1.0) * 32767.0).astype(np.int16)


def test_energy_vad_pure_silence_is_not_hard():
    x = np.zeros(CHUNK_SAMPLES, dtype=np.int16)
    res = energy_vad(x)
    assert isinstance(res, HyperVADResult)
    assert res.is_hard is False


def test_energy_vad_loud_speech_is_hard():
    x = _sine_pcm16(freq_hz=300.0, amp=0.6)
    res = energy_vad(x)
    assert isinstance(res, HyperVADResult)
    assert res.is_hard is True


def test_adaptive_vad_baseline_adapts_and_hits_accuracy_targets():
    rng = np.random.default_rng(0)
    vad = AdaptiveVAD(window_size_sec=2.0, sample_rate=SAMPLE_RATE)

    # 25 silence/noise frames to train baseline
    silence_frames = []
    for _ in range(25):
        noise = (rng.standard_normal(CHUNK_SAMPLES) * 0.002 * 32767.0).astype(np.int16)
        silence_frames.append(noise)
        energy_vad(noise, adaptive_engine=vad)

    # Evaluate silence accuracy (baseline established)
    silence_hard = sum(
        1 for fr in silence_frames if energy_vad(fr, adaptive_engine=vad).is_hard
    )
    silence_acc = 1.0 - (silence_hard / len(silence_frames))
    assert silence_acc >= 0.85, f"Silence accuracy too low: {silence_acc:.2%}"

    # Now evaluate speech accuracy
    speech_frames = [_sine_pcm16(freq_hz=440.0, amp=0.5) for _ in range(25)]
    speech_hard = sum(
        1 for fr in speech_frames if energy_vad(fr, adaptive_engine=vad).is_hard
    )
    speech_acc = speech_hard / len(speech_frames)
    assert speech_acc >= 0.85, f"Speech accuracy too low: {speech_acc:.2%}"


def test_soft_vs_hard_thresholds_with_adaptive_vad():
    vad = AdaptiveVAD(window_size_sec=2.0, sample_rate=SAMPLE_RATE)

    # Establish baseline with low noise
    for _ in range(25):
        energy_vad(np.zeros(CHUNK_SAMPLES, dtype=np.int16), adaptive_engine=vad)

    # Grab thresholds based on a baseline rms
    soft_thr, hard_thr = vad.update(vad.noise_stats["mu"])

    # Build a soft signal (above soft, below hard) and a hard signal
    soft_amp = min(0.2, max(soft_thr * 1.5, 0.02))
    hard_amp = min(0.8, max(hard_thr * 1.5, 0.2))

    soft = _sine_pcm16(freq_hz=200.0, amp=soft_amp)
    hard = _sine_pcm16(freq_hz=220.0, amp=hard_amp)

    res_soft = energy_vad(soft, adaptive_engine=vad)
    res_hard = energy_vad(hard, adaptive_engine=vad)

    assert res_soft.is_soft is True
    assert res_hard.is_hard is True


def test_hyper_vad_result_fields_and_sample_count():
    x = _sine_pcm16(freq_hz=300.0, amp=0.5)
    res = energy_vad(x)

    assert isinstance(res, HyperVADResult)
    assert hasattr(res, "is_soft")
    assert hasattr(res, "is_hard")
    assert hasattr(res, "energy_rms")
    assert hasattr(res, "sample_count")
    assert res.sample_count > 0


def test_silent_analyzer_classification_void_and_thinking_and_breathing():
    analyzer = SilentAnalyzer(sample_rate=SAMPLE_RATE)

    # VOID
    void = np.zeros(CHUNK_SAMPLES, dtype=np.int16)
    st = analyzer.classify(void, current_rms=0.0)
    assert st == SilenceType.VOID

    # THINKING (sustained low level)
    thinking = _sine_pcm16(freq_hz=60.0, amp=0.015)
    rms_thinking = float(np.sqrt(np.mean((thinking.astype(np.float32) / 32768.0) ** 2)))
    st2 = analyzer.classify(thinking, current_rms=rms_thinking)
    assert st2 in (SilenceType.THINKING, SilenceType.VOID)

    # BREATHING requires variance across history and low ZCR; simulate small oscillations
    # across multiple frames to build variance.
    for amp in (0.006, 0.009, 0.007, 0.009, 0.006, 0.009):
        fr = _sine_pcm16(freq_hz=80.0, amp=amp)
        rms = float(np.sqrt(np.mean((fr.astype(np.float32) / 32768.0) ** 2)))
        analyzer.classify(fr, current_rms=rms)

    fr = _sine_pcm16(freq_hz=80.0, amp=0.008)
    rms = float(np.sqrt(np.mean((fr.astype(np.float32) / 32768.0) ** 2)))
    st3 = analyzer.classify(fr, current_rms=rms)
    assert st3 in (SilenceType.BREATHING, SilenceType.THINKING, SilenceType.VOID)
