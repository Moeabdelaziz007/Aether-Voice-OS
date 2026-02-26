import asyncio
import unittest

import numpy as np

from core.audio.playback import AudioPlayback
from core.audio.processing import SilenceType, SilentAnalyzer
from core.audio.state import audio_state
from core.tools.voice_auth import VoiceAuthGuard
from core.utils.config import AudioConfig


class TestCyberneticCore(unittest.TestCase):
    def setUp(self):
        self.config = AudioConfig()
        self.queue = asyncio.Queue()

    def test_silence_classification(self):
        """Verify that SilentAnalyzer distinguishes void from breathing."""
        analyzer = SilentAnalyzer()

        # 1. Simulate Void (Absolute zero)
        pcm_void = np.zeros(1600, dtype=np.int16)
        res_void = analyzer.classify(pcm_void, 0.0)
        self.assertEqual(res_void, SilenceType.VOID)

        # 2. Simulate Thinking/Presence (Low RMS, Low ZCR)
        # Random noise with low RMS
        pcm_thinking = (np.random.normal(0, 100, 1600)).astype(np.int16)
        res_thinking = analyzer.classify(pcm_thinking, 0.005)
        self.assertIn(res_thinking, [SilenceType.THINKING, SilenceType.BREATHING])

    def test_audio_ducking_gain(self):
        """Verify that playback gain can be set for ducking."""
        playback = AudioPlayback(self.config, self.queue)
        playback.set_gain(0.2)
        self.assertEqual(playback._gain, 0.2)
        playback.set_gain(1.5)  # Should cap at 1.0
        self.assertEqual(playback._gain, 1.0)

    def test_voice_biometrics(self):
        """Verify that voice auth detects pitch-based signatures."""
        # Mocking audio_state
        audio_state.last_rms = 0.05

        # Authorized case: ~120Hz (Male pitch)
        audio_state.last_zcr = 0.015
        self.assertTrue(VoiceAuthGuard.is_authorized())

        # Unauthorized case: ~400Hz (High pitch/noise)
        audio_state.last_zcr = 0.05
        self.assertFalse(VoiceAuthGuard.is_authorized())

    def test_ambient_heartbeat_freq(self):
        """Verify that heartbeat frequency can be adjusted."""
        playback = AudioPlayback(self.config, self.queue)
        playback.set_heartbeat(60.0)
        self.assertEqual(playback._heartbeat_freq, 60.0)


if __name__ == "__main__":
    unittest.main()
