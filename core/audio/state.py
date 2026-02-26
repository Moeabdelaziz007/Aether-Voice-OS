"""
Aether Voice OS — Shared Audio State.

Thread-safe singleton to manage global audio states (playback/capture)
across C-callback threads and the main asyncio event loop.
"""

import threading


import threading

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
    """Thread-safe singleton to track audio I/O state."""

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
                cls._instance.is_soft = False
                cls._instance.is_hard = False
                cls._instance.silence_type = "void"
                cls._instance._playing_lock = threading.Lock()
        return cls._instance

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
