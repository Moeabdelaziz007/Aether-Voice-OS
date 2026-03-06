"""
Aether Voice OS — Spectral Analysis Module.

Provides STFT, Bark-scale frequency band analysis, and spectral feature extraction
for advanced audio processing including echo cancellation and voice activity detection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import fft

logger = logging.getLogger(__name__)


@dataclass
class SpectralFeatures:
    """Container for spectral feature extraction results."""

    centroid: float  # Spectral centroid (brightness)
    flatness: float  # Spectral flatness (tonal vs noise)
    rolloff: float  # Spectral rolloff frequency
    flux: float  # Spectral flux (change between frames)
    bark_bands: np.ndarray  # Energy per Bark band


class STFT:
    """Short-Time Fourier Transform with configurable parameters."""

    def __init__(
        self,
        n_fft: int = 512,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        window: str = "hann",
    ) -> None:
        """Initialize STFT processor.

        Args:
            n_fft: FFT size (default: 512)
            hop_length: Hop between frames (default: n_fft // 4)
            win_length: Window length (default: n_fft)
            window: Window type ('hann', 'hamming', 'blackman')
        """
        self.n_fft = n_fft
        self.hop_length = hop_length or n_fft // 4
        self.win_length = win_length or n_fft

        # Create window function
        if window == "hann":
            self.window = np.hanning(self.win_length)
        elif window == "hamming":
            self.window = np.hamming(self.win_length)
        elif window == "blackman":
            self.window = np.blackman(self.win_length)
        else:
            self.window = np.ones(self.win_length)

        # Pre-compute for efficiency
        self._window_norm = np.sum(self.window**2)

    def transform(self, x: np.ndarray) -> np.ndarray:
        """Compute STFT of input signal.

        Args:
            x: Input time-domain signal (1D array)

        Returns:
            Complex STFT matrix (freq_bins x time_frames)
        """
        # Pad signal for centering
        pad_width = self.n_fft // 2
        x_padded = np.pad(x, (pad_width, pad_width), mode="constant")

        # Create frames using sliding window
        n_frames = 1 + (len(x_padded) - self.n_fft) // self.hop_length
        frames = np.lib.stride_tricks.as_strided(
            x_padded,
            shape=(n_frames, self.n_fft),
            strides=(self.hop_length * x_padded.itemsize, x_padded.itemsize),
        )

        # Apply window and FFT
        windowed = frames * self.window
        stft_matrix = fft.rfft(windowed, axis=1)

        return stft_matrix.T  # (freq_bins x time_frames)

    def inverse(
        self, stft_matrix: np.ndarray, length: Optional[int] = None
    ) -> np.ndarray:
        """Compute inverse STFT.

        Args:
            stft_matrix: Complex STFT matrix (freq_bins x time_frames)
            length: Expected output length

        Returns:
            Reconstructed time-domain signal
        """
        n_frames = stft_matrix.shape[1]

        # IFFT per frame
        frames = fft.irfft(stft_matrix, axis=0, n=self.n_fft)

        # Overlap-add synthesis
        expected_signal_len = self.n_fft + self.hop_length * (n_frames - 1)
        signal = np.zeros(expected_signal_len)
        window_sum = np.zeros(expected_signal_len)

        for i in range(n_frames):
            sample = i * self.hop_length
            signal[sample : sample + self.n_fft] += frames[:, i] * self.window
            window_sum[sample : sample + self.n_fft] += self.window**2

        # Normalize by window sum (avoid division by zero)
        signal = np.where(window_sum > 1e-10, signal / window_sum, signal)

        # Remove padding
        signal = signal[self.n_fft // 2 :]
        if length is not None:
            signal = signal[:length]

        return signal


class BarkScale:
    """Bark-scale frequency band analysis for psychoacoustic modeling."""

    # Bark band edges (in Bark units)
    BARK_EDGES = np.array(
        [
            0,
            50,
            100,
            150,
            200,
            250,
            300,
            350,
            400,
            450,
            510,
            570,
            635,
            700,
            770,
            840,
            920,
            1000,
            1080,
            1170,
            1270,
            1370,
            1480,
            1600,
            1720,
            1850,
            2000,
            2150,
            2320,
            2500,
            2700,
            2900,
            3150,
            3400,
            3700,
            4000,
            4400,
            4800,
            5300,
            5800,
            6400,
            7000,
            7700,
            8500,
            9500,
            10500,
            12000,
            13500,
            15500,
            20000,
        ]
    )

    def __init__(self, sample_rate: int = 16000, n_fft: int = 512):
        """Initialize Bark-scale analyzer.

        Args:
            sample_rate: Audio sample rate in Hz
            n_fft: FFT size
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.n_bands = len(self.BARK_EDGES) - 1

        # Compute frequency bins
        self.freqs = fft.rfftfreq(n_fft, 1.0 / sample_rate)

        # Create Bark band mapping
        self.bark_map = self._create_bark_mapping()

    def _hz_to_bark(self, hz: np.ndarray) -> np.ndarray:
        """Convert Hz to Bark scale (Traunmüller formula)."""
        return 26.81 * hz / (1960 + hz) - 0.53

    def _create_bark_mapping(self) -> np.ndarray:
        """Create mapping from FFT bins to Bark bands."""
        bark_freqs = self._hz_to_bark(self.freqs)
        bark_edges = self._hz_to_bark(self.BARK_EDGES)

        mapping = np.zeros(len(self.freqs), dtype=np.int32)
        for i, bark in enumerate(bark_freqs):
            # Find which Bark band this frequency belongs to
            band = np.searchsorted(bark_edges, bark) - 1
            mapping[i] = max(0, min(band, self.n_bands - 1))

        return mapping

    def analyze(self, magnitude_spectrum: np.ndarray) -> np.ndarray:
        """Compute energy per Bark band.

        Args:
            magnitude_spectrum: Magnitude spectrum (n_freq_bins,)

        Returns:
            Energy per Bark band (n_bands,)
        """
        # Square to get power
        power = magnitude_spectrum**2

        # Sum power within each Bark band
        bark_energy = np.zeros(self.n_bands)
        for i in range(self.n_bands):
            mask = self.bark_map == i
            if np.any(mask):
                bark_energy[i] = np.sum(power[mask])

        return bark_energy

    def get_band_centers(self) -> np.ndarray:
        """Get center frequencies of each Bark band in Hz."""
        return (self.BARK_EDGES[:-1] + self.BARK_EDGES[1:]) / 2


class SpectralAnalyzer:
    """Comprehensive spectral feature extraction."""

    def __init__(self, sample_rate: int = 16000, n_fft: int = 512):
        """Initialize spectral analyzer.

        Args:
            sample_rate: Audio sample rate in Hz
            n_fft: FFT size for analysis
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.stft = STFT(n_fft=n_fft)
        self.bark = BarkScale(sample_rate, n_fft)

        # Previous spectrum for flux calculation
        self._prev_spectrum: Optional[np.ndarray] = None
        self._prev_magnitude: Optional[np.ndarray] = None

    def extract_features(self, x: np.ndarray) -> SpectralFeatures:
        """Extract comprehensive spectral features.

        Args:
            x: Input audio signal (time-domain)

        Returns:
            SpectralFeatures dataclass with all extracted features
        """
        # Compute STFT
        stft_matrix = self.stft.transform(x)

        # Use middle frame for analysis
        mid_frame = stft_matrix[:, stft_matrix.shape[1] // 2]
        magnitude = np.abs(mid_frame)

        # Frequency bins
        freqs = fft.rfftfreq(self.n_fft, 1.0 / self.sample_rate)

        # Spectral centroid (brightness)
        spectral_sum = np.sum(magnitude)
        if spectral_sum > 1e-10:
            centroid = np.sum(freqs * magnitude) / spectral_sum
        else:
            centroid = 0.0

        # Spectral flatness (geometric mean / arithmetic mean)
        # Add small epsilon to avoid log(0)
        magnitude_eps = magnitude + 1e-10
        geometric_mean = np.exp(np.mean(np.log(magnitude_eps)))
        arithmetic_mean = np.mean(magnitude)
        if arithmetic_mean > 1e-10:
            flatness = geometric_mean / arithmetic_mean
        else:
            flatness = 0.0

        # Spectral rolloff (frequency below which 85% of energy resides)
        cumsum = np.cumsum(magnitude)
        threshold = 0.85 * cumsum[-1]
        rolloff_idx = np.searchsorted(cumsum, threshold)
        rolloff = freqs[min(rolloff_idx, len(freqs) - 1)]

        # Spectral flux (change from previous frame)
        if self._prev_magnitude is not None:
            # Ensure same length
            min_len = min(len(magnitude), len(self._prev_magnitude))
            flux = np.sum(
                np.maximum(0, magnitude[:min_len] - self._prev_magnitude[:min_len])
            )
        else:
            flux = 0.0

        # Bark band analysis
        bark_bands = self.bark.analyze(magnitude)

        # Store for next frame
        self._prev_magnitude = magnitude.copy()

        return SpectralFeatures(
            centroid=centroid,
            flatness=flatness,
            rolloff=rolloff,
            flux=flux,
            bark_bands=bark_bands,
        )

    def compute_coherence(
        self, x: np.ndarray, y: np.ndarray, n_frames: int = 4
    ) -> float:
        """Compute magnitude-squared coherence between two signals.

        Args:
            x: First signal (reference)
            y: Second signal (target)
            n_frames: Number of frames to average

        Returns:
            Magnitude-squared coherence [0, 1]
        """
        # Ensure same length
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]

        # Compute STFT
        X = self.stft.transform(x)
        Y = self.stft.transform(y)

        # Use most recent frames
        n_available = min(n_frames, X.shape[1], Y.shape[1])
        if n_available < 2:
            return 0.0

        X = X[:, -n_available:]
        Y = Y[:, -n_available:]

        # Cross-power and auto-power spectra
        S_xy = np.mean(X * np.conj(Y), axis=1)
        S_xx = np.mean(np.abs(X) ** 2, axis=1)
        S_yy = np.mean(np.abs(Y) ** 2, axis=1)

        # Magnitude-squared coherence
        denominator = S_xx * S_yy
        valid = denominator > 1e-10
        coherence = np.zeros_like(S_xy, dtype=np.float64)
        coherence[valid] = np.abs(S_xy[valid]) ** 2 / denominator[valid]

        # Average coherence across frequency
        mean_coherence = np.mean(coherence)

        return float(np.clip(mean_coherence, 0.0, 1.0))

    def reset(self) -> None:
        """Reset internal state."""
        self._prev_spectrum = None
        self._prev_magnitude = None
        fft.clear_fft_cache()


def gcc_phat(
    x: np.ndarray,
    y: np.ndarray,
    sample_rate: int = 16000,
    max_delay: Optional[int] = None,
) -> tuple[int, float]:
    """Generalized Cross-Correlation with Phase Transform (GCC-PHAT).

    Estimates time delay between two signals using GCC-PHAT algorithm.

    Args:
        x: Reference signal
        y: Target signal
        sample_rate: Sample rate in Hz
        max_delay: Maximum delay to search (samples),
            None for half signal length

    Returns:
        Tuple of (delay_samples, confidence)
    """
    # Make signals same length
    n = min(len(x), len(y))
    if n < 2:
        return 0, 0.0

    x = x[:n]
    y = y[:n]

    # FFT parameters
    n_fft = 2 ** int(np.ceil(np.log2(2 * n - 1)))

    # Compute FFT
    X = np.fft.fft(x, n_fft)
    Y = np.fft.fft(y, n_fft)

    # Cross-power spectrum
    R = X * np.conj(Y)

    # PHAT weighting (whitening)
    R_magnitude = np.abs(R)
    eps = 1e-10
    R_phat = R / (R_magnitude + eps)

    # Inverse FFT to get cross-correlation
    cc = np.fft.ifft(R_phat)
    cc = np.real(cc)

    # Note: original implementation did NOT use fftshift, we are restoring it to original

    # Keep only valid delay range
    max_shift = max_delay if max_delay is not None else n // 2
    max_shift = min(max_shift, n_fft // 2)

    # Find peak in cross-correlation
    zero_idx = 0  # FFT output is 0 to n_fft-1
    search_start = max(0, zero_idx - max_shift)
    search_end = min(n_fft, zero_idx + max_shift + 1)

    search_region = cc[search_start:search_end]
    peak_idx = np.argmax(np.abs(search_region))
    delay = peak_idx - (zero_idx - search_start)

    # Calculate confidence (peak prominence)
    peak_value = np.abs(search_region[peak_idx])
    mean_value = np.mean(np.abs(search_region))
    confidence = peak_value / (mean_value + eps)
    confidence = min(confidence / 3.0, 1.0)  # Normalize to [0, 1]

    return int(delay), float(confidence)


def erle(
    mic_signal: np.ndarray, error_signal: np.ndarray, frame_size: int = 256
) -> float:
    """Compute Echo Return Loss Enhancement (ERLE).

    ERLE measures the echo cancellation performance in dB.
    Higher values indicate better echo suppression.

    Args:
        mic_signal: Microphone signal (with echo)
        error_signal: Error signal (after echo cancellation)
        frame_size: Frame size for computing ERLE

    Returns:
        ERLE in dB (higher is better, typically 10-40 dB)
    """
    # Compute power in frames
    n_frames = len(mic_signal) // frame_size
    if n_frames == 0:
        return 0.0

    mic_power = 0.0
    error_power = 0.0

    for i in range(n_frames):
        start = i * frame_size
        end = start + frame_size
        mic_frame = mic_signal[start:end]
        error_frame = error_signal[start:end]

        mic_power += np.mean(mic_frame**2)
        error_power += np.mean(error_frame**2)

    mic_power /= n_frames
    error_power /= n_frames

    # Avoid log of zero
    eps = 1e-10
    mic_power = max(mic_power, eps)
    error_power = max(error_power, eps)

    erle_db = 10.0 * np.log10(mic_power / error_power)

    return float(erle_db)
