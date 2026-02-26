from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class LeakageDetector:
    """
    Detects if the microphone input is the user speaking or just speaker echo (leakage).
    Uses FFT correlation to compare the AI's recent outgoing spectrum with the incoming mic spectrum.
    """

    def __init__(self, sample_rate: int = 16000):
        self._sample_rate = sample_rate
        self._ai_spectrum = None

    def capture_ai_spectrum(self, ai_audio_chunk: bytes | np.ndarray) -> None:
        """Store the frequency spectrum of the AI's currently playing audio."""
        if len(ai_audio_chunk) == 0:
            self._ai_spectrum = None
            return

        if isinstance(ai_audio_chunk, bytes):
            pcm = np.frombuffer(ai_audio_chunk, dtype=np.int16)
        else:
            pcm = ai_audio_chunk

        # Avoid FFT on pure silence
        if np.max(np.abs(pcm)) < 10:
            self._ai_spectrum = None
            return

        self._ai_spectrum = np.abs(np.fft.rfft(pcm))

    def is_user_speaking(self, mic_audio_chunk: bytes | np.ndarray) -> bool:
        """
        Determines if the microphone audio is the user or echo.
        True = User is likely speaking
        False = It's highly likely just echo
        """
        if self._ai_spectrum is None:
            return True  # If AI isn't speaking or we have no data, assume user

        if isinstance(mic_audio_chunk, bytes):
            mic_pcm = np.frombuffer(mic_audio_chunk, dtype=np.int16)
        else:
            mic_pcm = mic_audio_chunk

        mic_spectrum = np.abs(np.fft.rfft(mic_pcm))

        # Ensure sizes match (padding if necessary, though they should be the same chunk size)
        min_len = min(len(self._ai_spectrum), len(mic_spectrum))
        if min_len == 0:
            return True

        ai_spec_cut = self._ai_spectrum[:min_len]
        mic_spec_cut = mic_spectrum[:min_len]

        # Prevent completely flat signals from causing NaNs in corrcoef
        if np.var(ai_spec_cut) < 1e-5 or np.var(mic_spec_cut) < 1e-5:
            return True

        # Calculate Pearson correlation coefficient between the two frequency spectrums
        correlation = np.corrcoef(ai_spec_cut, mic_spec_cut)[0, 1]

        # High correlation means the mic is just hearing what the speaker is outputting (Echo)
        is_echo = correlation > 0.7

        return not is_echo
