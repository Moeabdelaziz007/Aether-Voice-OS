"""
Aether Voice OS — Paralinguistic Verification.
"""

import numpy as np
import pytest

from core.audio.paralinguistics import ParalinguisticAnalyzer


@pytest.mark.asyncio
async def test_sentiment_analytics_logic():
    analyzer = ParalinguisticAnalyzer(sample_rate=16000)

    # 1. Simulate "Dull/Monotone" Audio (Low frequency, static)
    # 100Hz Sine wave
    t = np.linspace(0, 0.1, 1600)
    dull_pcm = (np.sin(2 * np.pi * 100 * t) * 10000).astype(np.int16)

    res_dull = analyzer.analyze(dull_pcm, 0.05)
    print(
        f"\nDull Audio: Pitch={res_dull.pitch_estimate:.2f}, "
        f"Engagement={res_dull.engagement_score:.2f}"
    )

    # 2. Simulate "Bright/Excited" Audio (Rising frequency, high pitch)
    # 400Hz Sine wave
    excited_pcm = (np.sin(2 * np.pi * 400 * t) * 20000).astype(np.int16)

    res_excited = analyzer.analyze(excited_pcm, 0.15)
    print(
        f"Excited Audio: Pitch={res_excited.pitch_estimate:.2f}, "
        f"Engagement={res_excited.engagement_score:.2f}"
    )

    # 3. Simulate "Expressive" Audio (Randomized pitch variance)
    # Note: Autocorrelation-based pitch might struggle with pure white noise,
    # but we test the variance history logic.
    for _ in range(10):
        varied_pitch = np.random.randint(200, 300)
        varied_pcm = (np.sin(2 * np.pi * varied_pitch * t) * 15000).astype(np.int16)
        analyzer.analyze(varied_pcm, 0.1)

    res_varied = analyzer.analyze(excited_pcm, 0.1)
    print(
        f"Varied Audio: Variance={res_varied.rms_variance:.2f}, "
        f"Engagement={res_varied.engagement_score:.2f}"
    )

    # Assertions
    assert res_excited.engagement_score >= res_dull.engagement_score
    assert res_varied.rms_variance > 0
    print("\n✅ Paralinguistic Analytics: Logic Verified")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_sentiment_analytics_logic())
