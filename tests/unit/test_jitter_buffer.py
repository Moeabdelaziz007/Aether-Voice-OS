# tests/unit/test_jitter_buffer.py

import numpy as np
import pytest

from core.audio.capture import AdaptiveJitterBuffer

pytest.skip("AdaptiveJitterBuffer was removed and replaced by AudioJitterBuffer", allow_module_level=True)


def test_jitter_buffer_stabilizes_bursts():
    """Test jitter buffer smooths out bursty input"""
    jb = AdaptiveJitterBuffer(
        target_latency_ms=60.0,
        max_latency_ms=200.0,
        sample_rate=16000,
    )

    # Simulate bursty writes (network jitter)
    chunk_size = 512
    for burst in [5, 0, 0, 3, 0, 0, 0, 7, 0]:  # Irregular arrivals
        for _ in range(burst):
            jb.write(np.random.randn(chunk_size).astype(np.int16) * 1000)

        # Always read same amount
        output = jb.read(chunk_size)
        assert len(output) == chunk_size  # Should never underrun after initial fill

def test_jitter_buffer_handles_underrun():
    """Test buffer returns silence on underrun"""
    jb = AdaptiveJitterBuffer(
        target_latency_ms=60.0,
        sample_rate=16000,
    )

    # Read without writing
    output = jb.read(512)

    assert len(output) == 512
    assert np.all(output == 0)  # Silence

def test_jitter_buffer_overflow():
    """Test buffer handles overflow correctly"""
    jb = AdaptiveJitterBuffer(
        target_latency_ms=60.0,
        max_latency_ms=200.0,
        sample_rate=16000,
    )

    # Write more than max capacity
    max_samples = int(200.0 * 16000 / 1000)
    huge_data = np.random.randn(max_samples * 2).astype(np.int16)

    jb.write(huge_data)

    # Should not crash, only keep most recent
    output = jb.read(512)
    assert len(output) == 512
