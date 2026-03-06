from __future__ import annotations

import logging
import threading

import numpy as np

logger = logging.getLogger(__name__)


class LeakageDetector:
    """
    Detects if the microphone input is the user speaking or just speaker echo
    (leakage). Uses FFT correlation to compare the AI's recent outgoing spectrum
    with the incoming mic spectrum.
    """

    def __init__(self, sample_rate: int = 16000):
        self._sample_rate = sample_rate
        self._ai_spectrum = None
        self._last_score = 0.0
        self._lock = threading.Lock()

    @property
    def last_score(self) -> float:
        """The Pearson correlation coefficient from the last analysis."""
        with self._lock:
            return self._last_score

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

        with self._lock:
            self._ai_spectrum = np.abs(np.fft.rfft(pcm))

    def calculate_score(self, mic_audio_chunk: bytes | np.ndarray) -> float:
        """
        Calculates the correlation score between the mic input and the AI audio.
        1.0 means perfect echo, 0.0 means no correlation.
        """
        if isinstance(mic_audio_chunk, bytes):
            mic_pcm = np.frombuffer(mic_audio_chunk, dtype=np.int16)
        else:
            mic_pcm = mic_audio_chunk

        with self._lock:
            ai_spectrum = self._ai_spectrum

        if ai_spectrum is None:
            with self._lock:
                self._last_score = 0.0
            return 0.0

        mic_spectrum = np.abs(np.fft.rfft(mic_pcm))

        min_len = min(len(ai_spectrum), len(mic_spectrum))
        if min_len == 0:
            return 0.0

        ai_spec_cut = ai_spectrum[:min_len]
        mic_spec_cut = mic_spectrum[:min_len]

        if np.var(ai_spec_cut) < 1e-5 or np.var(mic_spec_cut) < 1e-5:
            score = 0.0
        else:
            # Correlation coefficient
            score = float(np.corrcoef(ai_spec_cut, mic_spec_cut)[0, 1])
            if np.isnan(score):
                score = 0.0

        with self._lock:
            self._last_score = score
        return score
