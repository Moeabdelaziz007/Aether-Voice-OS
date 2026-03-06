"""
Aether Voice OS — Audio State Manager

Thread-safe audio state management replacing global variables.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np


class PlaybackState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    MUTED = "muted"


@dataclass
class AECState:
    converged: bool = False
    convergence_progress: float = 0.0
    erle_db: float = 0.0
    estimated_delay_ms: float = 0.0
    double_talk_detected: bool = False
    filter_ready: bool = False


@dataclass
class VADState:
    is_speech: bool = False
    is_soft_speech: bool = False
    energy_rms: float = 0.0
    adaptive_threshold: float = 0.02


@dataclass
class SessionState:
    session_id: Optional[str] = None
    is_active: bool = False
    start_time: float = 0.0
    last_activity: float = 0.0
    reconnect_count: int = 0


@dataclass
class AudioStats:
    frames_processed: int = 0
    frames_dropped: int = 0
    total_latency_ms: float = 0.0
    capture_queue_drops: int = 0


class AudioStateManager:
    """
    Thread-safe audio state manager.

    Replaces global audio_state with a proper class that:
    - Uses locks for thread safety
    - Provides atomic updates
    - Supports state snapshots
    - Emits change events
    """

    def __init__(self, buffer_capacity: int = 16000 * 10):
        self._lock = threading.RLock()

        # Playback state
        self._is_playing = False
        self._just_started_playing = False
        self._just_stopped_playing = False
        self._playback_start_time: Optional[float] = None

        # AEC state
        self._aec_state = AECState)

        # VAD state
        self._vad_state = VADState)

        # Session state
        self._session_state = SessionState)

        # Audio stats
        self._stats = AudioStats)

        # Far-end PCM buffer (AI output)
        self._far_end_buffer = np.zeros(buffer_capacity, dtype=np.int16)
        self._far_end_write_pos = 0
        self._far_end_count = 0
        self._buffer_capacity = buffer_capacity

        # Last RMS for monitoring
        self._last_rms = 0.0

    # ═══════════════════════════════════════════════════════════════
    # Playback State
    # ═══════════════════════════════════════════════════════════════

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return self._is_playing

    @property
    def just_started_playing(self) -> bool:
        with self._lock:
            val = self._just_started_playing
            self._just_started_playing = False
            return val

    @property
    def just_stopped_playing(self) -> bool:
        with self._lock:
            val = self._just_stopped_playing
            self._just_stopped_playing = False
            return val

    def set_playing(self, playing: bool) -> None:
        with self._lock:
            if playing and not self._is_playing:
                self._just_started_playing = True
                self._playback_start_time = time.time()
            elif not playing and self._is_playing:
                self._just_stopped_playing = True
                self._playback_start_time = None
            self._is_playing = playing

    # ═══════════════════════════════════════════════════════════════
    # AEC State
    # ═══════════════════════════════════════════════════════════════

    @property
    def aec_converged(self) -> bool:
        with self._lock:
            return self._aec_state.converged

    @property
    def aec_state(self) -> AECState:
        with self._lock:
            return AECState
                converged=self._aec_state.converged,
                convergence_progress=self._aec_state.convergence_progress,
                erle_db=self._aec_state.erle_db,
                estimated_delay_ms=self._aec_state.estimated_delay_ms,
                double_talk_detected=self._aec_state.double_talk_detected,
                filter_ready=self._aec_state.filter_ready,
            )

    def update_aec_state(
        self,
        converged: Optional[bool] = None,
        convergence_progress: Optional[float] = None,
        erle_db: Optional[float] = None,
        delay_ms: Optional[float] = None,
        double_talk: Optional[bool] = None,
    ) -> None:
        with self._lock:
            if converged is not None:
                self._aec_state.converged = converged
            if convergence_progress is not None:
                self._aec_state.convergence_progress = convergence_progress
            if erle_db is not None:
                self._aec_state.erle_db = erle_db
            if delay_ms is not None:
                self._aec_state.estimated_delay_ms = delay_ms
            if double_talk is not None:
                self._aec_state.double_talk_detected = double_talk

    # ═══════════════════════════════════════════════════════════════
    # VAD State
    # ═══════════════════════════════════════════════════════════════

    @property
    def last_rms(self) -> float:
        with self._lock:
            return self._last_rms

    @last_rms.setter
    def last_rms(self, value: float) -> None:
        with self._lock:
            self._last_rms = value

    @property
    def double_talk(self) -> bool:
        with self._lock:
            return self._aec_state.double_talk_detected

    def update_vad_state(
        self,
        is_speech: Optional[bool] = None,
        is_soft: Optional[bool] = None,
        energy_rms: Optional[float] = None,
    ) -> None:
        with self._lock:
            if is_speech is not None:
                self._vad_state.is_speech = is_speech
            if is_soft is not None:
                self._vad_state.is_soft_speech = is_soft
            if energy_rms is not None:
                self._vad_state.energy_rms = energy_rms

    # ═══════════════════════════════════════════════════════════════
    # Far-End Buffer (PCM Ring Buffer)
    # ═══════════════════════════════════════════════════════════════

    def write_far_end(self, data: np.ndarray) -> None:
        with self._lock:
            n = len(data)
            if n >= self._buffer_capacity:
                self._far_end_buffer[:] = data[-self._buffer_capacity :]
                self._far_end_write_pos = 0
                self._far_end_count = self._buffer_capacity
                return

            for i, sample in enumerate(data):
                pos = (self._far_end_write_pos + i) % self._buffer_capacity
                self._far_end_buffer[pos] = sample

            self._far_end_write_pos = (
                self._far_end_write_pos + n
            ) % self._buffer_capacity
            self._far_end_count = min(self._far_end_count + n, self._buffer_capacity)

    def read_far_end_last(self, n: int) -> np.ndarray:
        with self._lock:
            n = min(n, self._far_end_count)
            if n == 0:
                return np.array([], dtype=np.int16)

            start = (self._far_end_write_pos - n) % self._buffer_capacity
            if start + n <= self._buffer_capacity:
                return self._far_end_buffer[start : start + n].copy()
            else:
                return np.concatenate(
                    [
                        self._far_end_buffer[start:],
                        self._far_end_buffer[: n - (self._buffer_capacity - start)],
                    ]
                )

    @property
    def far_end_pcm(self):
        return _FarEndBufferProxy(self)


class _FarEndBufferProxy:
    """Proxy for far-end buffer that delegates to AudioStateManager."""

    def __init__(self, manager: AudioStateManager):
        self._manager = manager

    def write(self, data: np.ndarray) -> None:
        self._manager.write_far_end(data)

    def read_last(self, n: int) -> np.ndarray:
        return self._manager.read_far_end_last(n)


# ═══════════════════════════════════════════════════════════════════
# Global instance (for backwards compatibility during migration)
# ═══════════════════════════════════════════════════════════════════

audio_state_manager = AudioStateManager)


# Proxy class for backwards compatibility with existing audio_state
class AudioStateProxy:
    """Backwards-compatible proxy for global audio_state."""

    def __init__(self, manager: AudioStateManager):
        self._manager = manager

    @property
    def is_playing(self) -> bool:
        return self._manager.is_playing

    @is_playing.setter
    def is_playing(self, value: bool) -> None:
        self._manager.set_playing(value)

    @property
    def just_started_playing(self) -> bool:
        return self._manager.just_started_playing

    @property
    def just_stopped_playing(self) -> bool:
        return self._manager.just_stopped_playing

    @property
    def far_end_pcm(self):
        return self._manager.far_end_pcm

    @property
    def last_rms(self) -> float:
        return self._manager.last_rms

    @last_rms.setter
    def last_rms(self, value: float) -> None:
        self._manager.last_rms = value

    @property
    def double_talk(self) -> bool:
        return self._manager.double_talk

    @property
    def capture_queue_drops(self) -> int:
        return self._manager._stats.capture_queue_drops

    @capture_queue_drops.setter
    def capture_queue_drops(self, value: int) -> None:
        with self._manager._lock:
            self._manager._stats.capture_queue_drops = value

    def update_aec_state(self, **kwargs) -> None:
        self._manager.update_aec_state(**kwargs)


# Global audio_state instance (backwards compatible)
audio_state = AudioStateProxyaudio_state_manager)
