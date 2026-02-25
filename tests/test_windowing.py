"""Tests for the legacy windowing module (core/windowing.py)."""
import numpy as np
from core.windowing import AudioWindow, detect_vad


class TestAudioWindow:
    """Tests for the AudioWindow tumbling window implementation."""

    def test_window_creation(self):
        window = AudioWindow()
        assert window.sample_rate == 16000

    def test_window_size_calculation(self):
        window = AudioWindow(sample_rate=16000, window_size_ms=3000)
        expected_samples = int(16000 * 3000 / 1000)
        assert window.window_size_samples == expected_samples

    def test_add_chunks_below_threshold(self):
        window = AudioWindow(window_size_ms=3000)
        small_bytes = np.zeros(100, dtype=np.int16).tobytes()
        window.add_chunks([small_bytes])
        result = window.get_window()
        assert result is None  # Not enough

    def test_add_chunks_full_window(self):
        window = AudioWindow(window_size_ms=100)  # 1600 samples
        full = np.zeros(window.window_size_samples, dtype=np.int16).tobytes()
        window.add_chunks([full])
        result = window.get_window()
        assert result is not None
        assert len(result) == window.window_size_samples

    def test_clear(self):
        window = AudioWindow()
        data = np.ones(500, dtype=np.int16).tobytes()
        window.add_chunks([data])
        window.clear()
        assert len(window.buffer) == 0


class TestZeroCrossing:
    """Tests for zero-crossing detection (static method)."""

    def test_silent_audio(self):
        silent = np.zeros(1000, dtype=np.int16)
        idx = AudioWindow.find_zero_crossing(silent)
        assert idx >= 0

    def test_sine_wave_crossing(self):
        t = np.linspace(0, 0.01, 160, endpoint=False)
        sine = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
        idx = AudioWindow.find_zero_crossing(sine)
        assert 0 <= idx <= len(sine)


class TestVAD:
    """Tests for voice activity detection."""

    def test_silence_returns_false(self):
        silent = np.zeros(2400, dtype=np.int16)
        assert detect_vad(silent) == False  # noqa: E712 (numpy bool_)

    def test_loud_signal_returns_true(self):
        loud = (np.ones(2400, dtype=np.int16) * 10000)
        assert detect_vad(loud) == True  # noqa: E712 (numpy bool_)
