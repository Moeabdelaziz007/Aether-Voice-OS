"""
Aether Voice OS — Shared Audio State.

Thread-safe singleton to manage global audio states (playback/capture) 
across C-callback threads and the main asyncio event loop.
"""
import threading

class AudioState:
    """Thread-safe singleton to track audio I/O state."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioState, cls).__new__(cls)
                cls._instance.is_playing = False
                cls._instance.is_capturing = False
                cls._instance._playing_lock = threading.Lock()
        return cls._instance

    def set_playing(self, playing: bool):
        """Atomic update for playback state."""
        with self._playing_lock:
            self.is_playing = playing

# Global singleton
audio_state = AudioState()
