"""Tests for the audio processing module (core/audio/processing.py)."""

import numpy as np

from core.audio.dsp.processing import RingBuffer, energy_vad, find_zero_crossing


class TestRingBuffer:
    """Tests for the RingBuffer implementation."""

    def test_window_creation(self):
        buf = RingBuffer(capacity_samples=16000)
        assert buf.capacity == 16000
        assert buf.count == 0

    def test_write_and_read(self):
        buf = RingBuffer(capacity_samples=16000)
        data = np.ones(100, dtype=np.int16)
        buf.write(data)
        assert buf.count == 100
        result = buf.read_last(100)
        assert len(result) == 100
        assert np.all(result == 1)

    def test_wrap_around(self):
        buf = RingBuffer(capacity_samples=100)
        data1 = np.ones(80, dtype=np.int16)
        data2 = np.ones(40, dtype=np.int16) * 2
        buf.write(data1)
        buf.write(data2)
        assert buf.count == 100
        result = buf.read_last(100)
        assert len(result) == 100
        assert np.all(result[:60] == 1)
        assert np.all(result[60:] == 2)

    def test_clear(self):
        buf = RingBuffer(capacity_samples=100)
        data = np.ones(50, dtype=np.int16)
        buf.write(data)
        buf.clear()
        assert buf.count == 0


class TestZeroCrossing:
    """Tests for zero-crossing detection."""

    def test_silent_audio(self):
        silent = np.zeros(1000, dtype=np.int16)
        idx = find_zero_crossing(silent)
        assert idx >= 0

    def test_sine_wave_crossing(self):
        t = np.linspace(0, 0.01, 160, endpoint=False)
        sine = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
        idx = find_zero_crossing(sine)
        assert 0 <= idx <= len(sine)


class TestVAD:
    """Tests for voice activity detection."""

    def test_silence_returns_false(self):
        silent = np.zeros(2400, dtype=np.int16)
        result = energy_vad(silent)
        assert result.is_hard is False

    def test_loud_signal_returns_true(self):
        loud = np.ones(2400, dtype=np.int16) * 10000
        result = energy_vad(loud)
        assert result.is_hard is True
