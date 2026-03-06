import numpy as np
import pytest

from core.audio.capture import SmoothMuter

# Constants
RAMP_SAMPLES = 256
CHUNK_SIZE = 128  # Smaller than ramp for multi-chunk testing
SAMPLE_RATE = 16000


@pytest.fixture
def muter():
    """Provides a SmoothMuter instance with a fixed ramp time."""
    return SmoothMuter(ramp_samples=RAMP_SAMPLES)


def generate_dc_signal(level: float, num_samples: int) -> np.ndarray:
    """Generates a DC signal (constant value) to make testing ramps easy."""
    return (np.full(num_samples, level) * 32767).astype(np.int16)


def test_muter_initial_state(muter):
    """Tests that the muter starts in an unmuted (pass-through) state."""
    signal = generate_dc_signal(0.5, CHUNK_SIZE)
    processed_signal = muter.process(signal)

    assert muter._current_gain == 1.0
    assert muter._target_gain == 1.0
    np.testing.assert_array_equal(signal, processed_signal)


def test_muter_mute_ramp(muter):
    """
    Tests the fade-out (mute) ramp over several chunks.
    """
    signal = generate_dc_signal(1.0, CHUNK_SIZE)

    # Initial state is 1.0
    assert muter._current_gain == 1.0

    # Initiate mute
    muter.mute()
    assert muter._target_gain == 0.0

    # --- Process first chunk ---
    chunk1 = muter.process(signal.copy())
    # Gain should have decreased
    assert muter._current_gain < 1.0
    assert muter._current_gain > 0.0
    # The output signal should be attenuated, check the last sample
    assert np.abs(chunk1[-1]) < np.abs(signal[-1])

    # --- Process second chunk ---
    muter.process(signal.copy())
    # RAMP_SAMPLES (256) is CHUNK_SIZE (128) * 2, so it should be at zero now.
    assert muter._current_gain == 0.0

    # --- Process third chunk (should be silent) ---
    chunk3 = muter.process(signal.copy())
    # The output should be all zeros
    np.testing.assert_array_equal(chunk3, np.zeros(CHUNK_SIZE, dtype=np.int16))

    # --- Process third chunk (should stay at zero) ---
    chunk3 = muter.process(signal.copy())
    assert muter._current_gain == 0.0
    np.testing.assert_array_equal(chunk3, np.zeros(CHUNK_SIZE, dtype=np.int16))


def test_muter_unmute_ramp(muter):
    """
    Tests the fade-in (unmute) ramp.
    """
    signal = generate_dc_signal(1.0, CHUNK_SIZE)

    # Start in a muted state
    muter._current_gain = 0.0
    muter._target_gain = 0.0

    # Initiate unmute
    muter.unmute()
    assert muter._target_gain == 1.0

    # --- Process first chunk ---
    chunk1 = muter.process(signal.copy())
    assert muter._current_gain > 0.0
    assert muter._current_gain < 1.0
    assert np.max(np.abs(chunk1)) > 0
    assert np.max(np.abs(chunk1)) < np.max(np.abs(signal))

    # --- Process second chunk ---
    muter.process(signal.copy())
    # Should be at full gain now
    assert muter._current_gain == 1.0

    # --- Process third chunk (should stay at 1.0) ---
    chunk3 = muter.process(signal.copy())
    assert muter._current_gain == 1.0
    np.testing.assert_array_equal(chunk3, signal)


def test_smoothness_of_ramp_to_prevent_clicks():
    """
    Verifies that the gain ramp is smooth by checking the maximum sample-to-sample
    difference. A large jump indicates a click.
    """
    # Use a longer ramp and chunk to get a good measurement
    muter = SmoothMuter(ramp_samples=1024)
    chunk_size = 2048
    signal = generate_dc_signal(1.0, chunk_size)

    # Mute
    muter.mute()
    processed_signal = muter.process(signal).astype(np.float32)

    # Calculate the first difference (sample-to-sample change)
    diffs = np.diff(processed_signal)

    # The maximum change should be very small relative to the signal's max value
    max_diff = np.max(np.abs(diffs))
    max_signal_val = np.max(np.abs(signal))

    # A click would be a significant fraction of the signal's amplitude.
    # The ramped change should be much smaller. The theoretical max change for
    # a DC signal is max_val / ramp_samples.
    expected_max_diff = max_signal_val / muter._ramp_samples

    print(f"Max sample-to-sample diff: {max_diff:.2f}")
    print(f"Expected max diff: {expected_max_diff:.2f}")

    # Allow a small tolerance
    assert max_diff < expected_max_diff * 1.5, (
        "Ramp is not smooth, potential for clicks"
    )


# ============================================
# ADD: New tests from the requirements
# ============================================


def test_mute_creates_smooth_ramp():
    """Verify mute creates fade-out without clicks"""
    muter = SmoothMuter(ramp_samples=256)

    # Generate test signal
    signal = np.ones(1024, dtype=np.int16) * 10000

    # Apply mute
    muter.mute()
    result = muter.process(signal)

    # Verify: should ramp from ~1.0 to 0.0
    assert result[0] > result[-1]  # Fade out
    assert result[-1] < 100  # Should be near zero at end

    # Verify no discontinuities (clicks)
    diff = np.diff(result.astype(np.float64))
    max_step = np.max(np.abs(diff))
    assert max_step < 500, f"Discontinuity detected: {max_step}"


def test_unmute_creates_smooth_ramp():
    """Verify unmute creates fade-in without clicks"""
    muter = SmoothMuter(ramp_samples=256)
    muter.mute()
    muter.process(np.zeros(100, dtype=np.int16))  # Process while muted

    muter.unmute()
    signal = np.ones(1024, dtype=np.int16) * 10000
    result = muter.process(signal)

    # Should ramp from 0 to full volume
    assert result[0] < result[-1]
    assert result[-1] > 9000  # Near full volume


def test_ramp_samples_affects_speed():
    """Verify ramp_samples parameter affects ramp duration"""
    muter_short = SmoothMuter(ramp_samples=64)
    muter_long = SmoothMuter(ramp_samples=512)

    signal = np.ones(2048, dtype=np.int16) * 10000

    muter_short.mute()
    result_short = muter_short.process(signal.copy())

    muter_long.mute()
    result_long = muter_long.process(signal.copy())

    # Short ramp should reach zero faster
    zero_idx_short = np.where(result_short == 0)[0]
    zero_idx_long = np.where(result_long == 0)[0]

    if len(zero_idx_short) > 0 and len(zero_idx_long) > 0:
        assert zero_idx_short[0] < zero_idx_long[0]
