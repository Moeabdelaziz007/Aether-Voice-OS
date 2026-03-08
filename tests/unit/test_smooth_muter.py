import numpy as np
import pytest

from core.audio.capture import SmoothMuter


def test_smooth_muter_linear_vs_exponential():
    """Verify that SmoothMuter applies an exponential-like ramp."""
    # Using a larger ramp for observation
    muter = SmoothMuter(ramp_samples=100)
    
    # Create 100 samples of constant audio
    pcm = np.full(100, 1000, dtype=np.int16)
    
    # Start at 1.0, target 0.0 (mute)
    muter.mute()
    processed = muter.process(pcm)
    
    # In an exponential decay, the first step should be a larger drop 
    # than the last step if it were linear, but here it's more about 
    # the curve shape.
    
    # Check that it actually reduced volume
    assert np.all(processed <= pcm)
    assert processed[-1] < processed[0]
    
    # Verify it reached near-epsilon or target
    # With 100 samples and 100 ramp_samples, it should hit ~0.01 (99% decay)
    assert muter._current_gain == pytest.approx(0.01, abs=1e-3)

def test_smooth_muter_unmute():
    """Verify unmute ramp (attack)."""
    muter = SmoothMuter(ramp_samples=100)
    muter._current_gain = 0.0
    muter.unmute()
    
    pcm = np.full(100, 1000, dtype=np.int16)
    processed = muter.process(pcm)
    
    assert np.all(processed >= 0)
    assert processed[0] > 0
    # Should be ~99% of 1000
    assert processed[-1] == pytest.approx(990, abs=5)
    assert muter._current_gain == pytest.approx(0.99, abs=0.01)

def test_smooth_muter_no_ramp():
    """Verify behavior when ramp is 0 (instant switch)."""
    muter = SmoothMuter(ramp_samples=0)
    muter.mute()
    
    pcm = np.full(100, 1000, dtype=np.int16)
    processed = muter.process(pcm)
    
    assert np.all(processed == 0)
    assert muter._current_gain == pytest.approx(0.0)
