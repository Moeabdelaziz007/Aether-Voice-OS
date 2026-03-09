"""
Aether Voice OS — Audio Exceptions.

Centralized exception hierarchy for audio capture, playback, and processing.
"""


class AudioError(Exception):
    """Base exception for all audio-related errors."""

    pass


class AudioDeviceError(AudioError):
    """Base class for device-related errors."""

    pass


class AudioDeviceNotFoundError(AudioDeviceError):
    """No audio device available for capture/playback."""

    def __init__(self, message: str, device_type: str = "unknown", **kwargs):
        self.device_type = device_type
        super().__init__(message, **kwargs)


class DeviceDisconnectedError(AudioDeviceError):
    """Audio device disconnected during active session."""

    def __init__(self, message: str, device_name: str = None, **kwargs):
        self.device_name = device_name
        super().__init__(message, **kwargs)


class BufferOverflowError(AudioError):
    """Audio buffer overflow - data loss occurred."""

    def __init__(self, message: str, dropped_chunks: int = 0, **kwargs):
        self.dropped_chunks = dropped_chunks
        super().__init__(message, **kwargs)


class AECConvergenceError(AudioError):
    """AEC filter failed to converge or diverged."""

    def __init__(self, message: str, erle_db: float = 0.0, **kwargs):
        self.erle_db = erle_db
        super().__init__(message, **kwargs)


class AudioPipelineError(AudioError):
    """Critical error in audio pipeline requiring restart."""

    pass
