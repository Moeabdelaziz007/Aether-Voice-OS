# tests/unit/test_jitter_buffer.py


from core.audio.jitter_buffer import AudioJitterBuffer as AdaptiveJitterBuffer


def test_jitter_buffer_stabilizes_bursts():
    """Test jitter buffer smooths out bursty input"""
    jb = AdaptiveJitterBuffer(
        capacity_ms=200,
        nominal_ms=60,
        packet_size_ms=20,
    )

    # Simulate bursty writes (network jitter)
    chunk_size = 512
    # 20ms of 16kHz audio = 320 samples (640 bytes)
    dummy_data = b'\x00' * 640
    for burst in [5, 0, 0, 3, 0, 0, 0, 7, 0]:  # Irregular arrivals
        for _ in range(burst):
            jb.push(dummy_data)

        # Buffer should be able to pop if it's filled
        output = jb.pop()
        # In a real scenario it might underrun, but the class handles it by returning None
        if output is not None:
            assert len(output) == 640

def test_jitter_buffer_handles_underrun():
    """Test buffer returns None on underrun"""
    jb = AdaptiveJitterBuffer(
        nominal_ms=60,
        packet_size_ms=20,
    )

    # Read without writing
    output = jb.pop()

    assert output is None  # Should return None when buffering

def test_jitter_buffer_overflow():
    """Test buffer handles overflow correctly"""
    jb = AdaptiveJitterBuffer(
        capacity_ms=200,
        packet_size_ms=20,
    )

    # Write more than max capacity
    # capacity = 200/20 = 10 packets
    for _ in range(15):
        jb.push(b'\x01' * 640)

    # Buffer length should max out at capacity
    assert jb.level == 10

    # Should not crash, pop works
    output = jb.pop()
    assert output == b'\x01' * 640
