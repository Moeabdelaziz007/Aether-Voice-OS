"""
Aether Voice OS — Tests for Audio Processing.

Tests the pure-computation functions: RingBuffer,
find_zero_crossing, and energy_vad.
"""

import numpy as np

from core.audio.processing import RingBuffer, VADResult, energy_vad, find_zero_crossing


class TestRingBuffer:
    """Tests for the O(1) circular audio buffer."""

    def test_basic_write_and_read(self):
        buf = RingBuffer(capacity_samples=100)
        data = np.arange(50, dtype=np.int16)
        buf.write(data)
        assert buf.count == 50
        result = buf.read_last(50)
        np.testing.assert_array_equal(result, data)

    def test_wrap_around(self):
        buf = RingBuffer(capacity_samples=10)
        # Write 7 samples, then 7 more → second batch wraps around
        buf.write(np.arange(7, dtype=np.int16))
        buf.write(np.arange(7, 14, dtype=np.int16))
        assert buf.count == 10  # Capped at capacity
        # Should contain the most recent 10 samples: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        result = buf.read_last(10)
        expected = np.arange(4, 14, dtype=np.int16)
        np.testing.assert_array_equal(result, expected)

    def test_overflow_large_write(self):
        buf = RingBuffer(capacity_samples=5)
        # Write more than capacity — should keep only the last 5
        data = np.arange(20, dtype=np.int16)
        buf.write(data)
        assert buf.count == 5
        result = buf.read_last(5)
        np.testing.assert_array_equal(result, np.arange(15, 20, dtype=np.int16))

    def test_read_more_than_available(self):
        buf = RingBuffer(capacity_samples=100)
        buf.write(np.arange(10, dtype=np.int16))
        result = buf.read_last(50)  # Only 10 available
        assert len(result) == 10

    def test_empty_read(self):
        buf = RingBuffer(capacity_samples=100)
        result = buf.read_last(10)
        assert len(result) == 0

    def test_empty_write(self):
        buf = RingBuffer(capacity_samples=100)
        buf.write(np.array([], dtype=np.int16))
        assert buf.count == 0

    def test_clear(self):
        buf = RingBuffer(capacity_samples=100)
        buf.write(np.arange(50, dtype=np.int16))
        buf.clear()
        assert buf.count == 0
        assert len(buf.read_last(10)) == 0


class TestZeroCrossing:
    """Tests for zero-crossing detection."""

    def test_finds_crossing(self):
        # Signal: [-100, 100, ...] — crossing between index 0 and 1
        pcm = np.array([-100, 100, 200, 300], dtype=np.int16)
        idx = find_zero_crossing(pcm)
        assert idx == 1

    def test_no_crossing_positive(self):
        pcm = np.array([100, 200, 300, 400], dtype=np.int16)
        idx = find_zero_crossing(pcm)
        assert idx == len(pcm)

    def test_no_crossing_negative(self):
        pcm = np.array([-100, -200, -300], dtype=np.int16)
        idx = find_zero_crossing(pcm)
        assert idx == len(pcm)

    def test_crossing_at_zero(self):
        pcm = np.array([100, 0, -100], dtype=np.int16)
        idx = find_zero_crossing(pcm)
        assert idx == 1  # 100 * 0 = 0 ≤ 0

    def test_single_sample(self):
        pcm = np.array([42], dtype=np.int16)
        idx = find_zero_crossing(pcm)
        assert idx == 1  # len(pcm) since < 2


class TestEnergyVAD:
    """Tests for voice activity detection."""

    def test_silence_below_threshold(self):
        silence = np.zeros(1000, dtype=np.int16)
        result = energy_vad(silence)
        assert result.is_speech is False
        assert result.energy_rms == 0.0

    def test_loud_signal_above_threshold(self):
        loud = np.full(1000, 10000, dtype=np.int16)
        result = energy_vad(loud)
        assert result.is_speech is True
        assert result.energy_rms > 0.1

    def test_empty_input(self):
        result = energy_vad(np.array([], dtype=np.int16))
        assert result.is_speech is False
        assert result.sample_count == 0

    def test_returns_vad_result(self):
        data = np.random.randint(-32768, 32767, size=500, dtype=np.int16)
        result = energy_vad(data)
        assert isinstance(result, VADResult)
        assert result.sample_count == 500

    def test_custom_threshold(self):
        quiet = np.full(1000, 500, dtype=np.int16)
        # With very low threshold, should detect as speech
        result = energy_vad(quiet, threshold=0.001)
        assert result.is_speech is True
        # With very high threshold, should not detect
        result = energy_vad(quiet, threshold=0.5)
        assert result.is_speech is False
