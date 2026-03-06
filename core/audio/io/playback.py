"""
Aether Voice OS — Audio Playback.

Consumes PCM audio from an asyncio.Queue and writes it
to the system speaker via PyAudio using a high-performance
C-thread callback. Supports interruption by draining the queue.

Output sample rate is 24kHz (Gemini native audio output).
"""

from __future__ import annotations

import asyncio
import logging
import queue
from typing import Optional

import pyaudio

from core.audio.state.state import audio_state
from core.infra.config import AudioConfig
from core.utils.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class AudioPlayback:
    """
    asyncio.Queue (AI) → queue.Queue (Buffer) → Speaker (C-Callback).

    Supports instant interruption: when `interrupt()` is called,
    both the asyncio and thread-safe queues are drained.
    """

    def __init__(
        self,
        config: AudioConfig,
        input_queue: asyncio.Queue[bytes],
        on_audio_tx: Optional[callable] = None,
    ) -> None:
        self._config = config
        self._async_queue = input_queue
        self._on_audio_tx = on_audio_tx
        self._buffer: queue.Queue[bytes] = queue.Queue(maxsize=100)
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False
        self._gain = 1.0  # Linear gain for ducking (1.0 = Max, 0.2 = Ducked)
        self._heartbeat_freq = 50.0  # Hz (Subliminal Hum)
        self._phase = 0.0

    def set_gain(self, gain: float) -> None:
        """Adjust output volume level (0.0 to 1.0)."""
        self._gain = max(0.0, min(gain, 1.0))
        logger.debug("Playback Gain adjusted: %.2f", self._gain)

    def set_heartbeat(self, freq: float) -> None:
        """Adjust the subliminal heart rate (40Hz = Calm, 60Hz = Stress)."""
        self._heartbeat_freq = freq

    def _callback(
        self, in_data: bytes | None, frame_count: int, time_info: dict, status: int
    ) -> tuple[bytes | None, int]:
        """PyAudio callback running in a high-priority C-thread."""
        import numpy as np

        try:
            data = self._buffer.get_nowait()
            audio_state.set_playing(True)

            pcm = np.frombuffer(data, dtype=np.int16).astype(np.float32)

            # 1. Apply linear gain for ducking
            if self._gain < 0.99:
                pcm *= self._gain

            # 2. Mix Ambient Heartbeat (Subliminal status)
            t = np.arange(len(pcm)) / 16000.0
            heartbeat = 500.0 * np.sin(
                2 * np.pi * self._heartbeat_freq * (t + self._phase)
            )
            pcm += heartbeat
            self._phase = (self._phase + t[-1]) % 1.0

            # 3. Feed AEC reference buffer (24kHz -> 16kHz resampling)
            if len(pcm) > 0:
                t_old = np.arange(len(pcm))
                t_new = np.arange(0, len(pcm), 1.5)  # 24/16 = 1.5 ratio
                pcm_16k = np.interp(t_new, t_old, pcm).astype(np.int16)
                audio_state.far_end_pcm.write(pcm_16k)
                # Capture AI spectrum for legacy monitoring
                audio_state.ai_spectrum = np.abs(np.fft.rfft(pcm))

            data = pcm.astype(np.int16).tobytes()
            return (data, pyaudio.paContinue)
        except queue.Empty:
            audio_state.set_playing(False)
            # Return silence (frame_count * 2 bytes for 16-bit mono)
            return (b"\x00" * (frame_count * 2), pyaudio.paContinue)

    async def start(self) -> None:
        """Open the speaker output stream with callback."""
        self._pya = pyaudio.PyAudio()

        try:
            self._pya.get_default_output_device_info()
        except IOError as exc:
            raise AudioDeviceNotFoundError(
                "No default output device found.",
                cause=exc,
            ) from exc

        # Open stream in callback mode
        self._stream = self._pya.open(
            format=pyaudio.paInt16,
            channels=self._config.channels,
            rate=self._config.receive_sample_rate,
            output=True,
            stream_callback=self._callback,
            frames_per_buffer=1024,  # Standard Gemini buffer
        )

        self._running = True
        logger.info(
            "⚡ Thalamic Playback Active: Speaker opened @ %dHz (Callback Mode)",
            self._config.receive_sample_rate,
        )

    async def run(self) -> None:
        """
        Feeds the thread-safe buffer from the asyncio queue.
        This provides backpressure to the AI session.
        """
        if not self._stream:
            raise AudioDeviceNotFoundError("Call start() before run()")

        logger.info("Audio playback feeder running")

        while self._running:
            try:
                # 1. Get audio from AI session (asyncio)
                audio_bytes = await self._async_queue.get()

                # 1.5 Mirror to UI (WebSockets) if connected
                if self._on_audio_tx:
                    try:
                        await self._on_audio_tx(audio_bytes)
                    except Exception as e:
                        logger.debug("Failed to mirror audio to UI: %s", e)

                # 2. Push to thread-safe buffer with lightweight async spinlock.
                while self._running:
                    try:
                        self._buffer.put_nowait(audio_bytes)
                        break
                    except queue.Full:
                        await asyncio.sleep(0.005)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Playback feeder error: %s", exc)
                await asyncio.sleep(0.1)

    def interrupt(self) -> None:
        """
        Drain all queues to stop audio immediately.
        Prevents 'zombie' audio chunks from playing after barge-in.
        """
        dropped = 0

        # 1. Drain asyncio queue
        while not self._async_queue.empty():
            try:
                self._async_queue.get_nowait()
                dropped += 1
            except asyncio.QueueEmpty:
                break

        # 2. Drain thread-safe buffer
        while not self._buffer.empty():
            try:
                self._buffer.get_nowait()
                dropped += 1
            except queue.Empty:
                break

        audio_state.set_playing(False)

        if dropped:
            logger.info("⚡ Thalamic Drain: Dropped %d chunks", dropped)

    async def stop(self) -> None:
        """Release speaker resources."""
        self._running = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._pya:
            self._pya.terminate()
            self._pya = None
        logger.info("Audio playback stopped")
