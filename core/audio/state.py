"""
Aether Voice OS — Shared Audio State.

Thread-safe singleton to manage global audio states (playback/capture)
across C-callback threads and the main asyncio event loop.
"""

import threading

from core.audio.processing import RingBuffer


class HysteresisGate:
    """Adaptive hysteresis for audio gating to prevent rapid toggling (clicks)."""

    def __init__(self):
        self._mute_state = False
        self._mute_confidence = 0.0  # 0.0 to 1.0

    def update(self, is_playing: bool) -> bool:
        """Update confidence with hysteresis and return the target mute state."""
        if is_playing:
            self._mute_confidence += 0.3  # Fast attack (mute quickly)
        else:
            self._mute_confidence -= 0.1  # Slow release (unmute slowly)

        # Clamp between 0.0 and 1.0
        self._mute_confidence = max(0.0, min(1.0, self._mute_confidence))

        # Apply Thresholding
        self._mute_state = self._mute_confidence > 0.5

        return self._mute_state


class AudioState:
    """Thread-safe singleton to track audio I/O state.

    Concurrency model:
    - _lock protects shared AEC and state fields during composite updates.
    - _playing_lock isolates playback transition flags to avoid races with the
      playback callback thread.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioState, cls).__new__(cls)
                cls._instance.is_playing = False
                cls._instance.just_started_playing = False
                cls._instance.just_stopped_playing = False
                cls._instance.ai_spectrum = None
                cls._instance.is_capturing = False
                cls._instance.last_rms = 0.0
                cls._instance.last_zcr = 0.0
                # Telemetry counters (hot-path safe ints; best-effort updates)
                cls._instance.capture_queue_drops = 0
                cls._instance.is_soft = False
                cls._instance.is_hard = False
                cls._instance.silence_type = "void"
                cls._instance.capture_queue_drops = 0
                cls._instance._playing_lock = threading.Lock()
                # AEC (Acoustic Echo Cancellation) state
                cls._instance.aec_converged = False
                cls._instance.aec_convergence_progress = 0.0  # 0.0 to 1.0
                cls._instance.aec_erle_db = 0.0  # Echo Return Loss Enhancement
                cls._instance.aec_delay_ms = 0.0  # Estimated echo delay
                cls._instance.aec_double_talk = False  # Double-talk detection
                # Reference buffer for loopback AEC (2 seconds @ 16kHz)
                cls._instance.far_end_pcm = RingBuffer(32000)
                cls._instance.far_end_pcm = RingBuffer(32000)
        return cls._instance

    def update_aec_state(
        self,
        converged: bool = False,
        convergence_progress: float = 0.0,
        erle_db: float = 0.0,
        delay_ms: float = 0.0,
        double_talk: bool = False,
    ) -> None:
        """Update AEC state parameters atomically.

        Args:
            converged: Whether AEC filter has converged
            convergence_progress: Convergence progress 0.0 to 1.0
            erle_db: Echo Return Loss Enhancement in dB
            delay_ms: Estimated echo delay in milliseconds
            double_talk: Whether double-talk is detected
        """
        with self._lock:
            self.aec_converged = converged
            self.aec_convergence_progress = max(0.0, min(1.0, convergence_progress))
            self.aec_erle_db = erle_db
            self.aec_delay_ms = delay_ms
            self.aec_double_talk = double_talk

    def get_aec_state(self) -> dict:
        """Get current AEC state as dictionary."""
        with self._lock:
            return {
                "converged": self.aec_converged,
                "convergence_progress": self.aec_convergence_progress,
                "erle_db": self.aec_erle_db,
                "delay_ms": self.aec_delay_ms,
                "double_talk": self.aec_double_talk,
            }

    def set_playing(self, playing: bool):
        """Atomic update for playback state with transition flags."""
        with self._playing_lock:
            if playing and not self.is_playing:
                self.just_started_playing = True
                self.just_stopped_playing = False
            elif not playing and self.is_playing:
                self.just_started_playing = False
                self.just_stopped_playing = True
            else:
                self.just_started_playing = False
                self.just_stopped_playing = False

            self.is_playing = playing


# Global singleton
audio_state = AudioState()
audio_state = AudioState()
