import pytest
import time
import sys
import unittest.mock as mock

class MockPackage(mock.MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return mock.MagicMock()

sys.modules['numpy'] = MockPackage()
sys.modules['pyaudio'] = MockPackage()
sys.modules['scipy'] = MockPackage()
sys.modules['scipy.signal'] = MockPackage()

from core.audio.dsp.jitter_buffer import AudioJitterBuffer, JitterStats

def test_jitter_buffer_adaptation():
    jb = AudioJitterBuffer(capacity_ms=500, nominal_ms=40, packet_size_ms=20)
    assert jb.target_latency_ms == 40.0

    # Simulate steady arrival (no variance)
    for _ in range(15):
        jb.push(b"test")
        time.sleep(0.001) # Simulate fast network

    stats = jb.get_stats()
    # It should adapt
    assert stats.target_ms <= 40.0

def test_underrun_recovery():
    jb = AudioJitterBuffer(capacity_ms=500, nominal_ms=20, packet_size_ms=20)

    # Cause underrun
    assert jb.pop() is None

    stats = jb.get_stats()
    assert stats.underrun_count == 1
    # Check penalty applies (target > nominal)
    assert jb.target_latency_ms > 20.0

def test_overrun_handling():
    jb = AudioJitterBuffer(capacity_ms=100, nominal_ms=40, packet_size_ms=20)

    # Capacity is 5 packets. Push 6.
    for _ in range(6):
        jb.push(b"test")

    stats = jb.get_stats()
    assert stats.overrun_count == 1
