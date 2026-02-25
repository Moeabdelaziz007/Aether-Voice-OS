"""
Aether Voice OS — Audio Playback.

Consumes PCM audio from an asyncio.Queue and writes it
to the system speaker via PyAudio. Supports interruption
by draining the queue when the model is interrupted.

Output sample rate is 24kHz (Gemini native audio output).
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import pyaudio

from core.config import AudioConfig
from core.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class AudioPlayback:
    """
    asyncio.Queue → Speaker bridge.

    Supports instant interruption: when `interrupt()` is called,
    the output queue is drained and playback stops immediately.
    """

    def __init__(
        self,
        config: AudioConfig,
        input_queue: asyncio.Queue[bytes],
    ) -> None:
        self._config = config
        self._queue = input_queue
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False

    async def start(self) -> None:
        """Open the speaker output stream."""
        self._pya = pyaudio.PyAudio()

        try:
            self._pya.get_default_output_device_info()
        except IOError as exc:
            raise AudioDeviceNotFoundError(
                "No default output device found.",
                cause=exc,
            ) from exc

        self._stream = await asyncio.to_thread(
            self._pya.open,
            format=pyaudio.paInt16,
            channels=self._config.channels,
            rate=self._config.receive_sample_rate,
            output=True,
        )
        self._running = True
        logger.info("Speaker output opened @ %dHz", self._config.receive_sample_rate)

    async def run(self) -> None:
        """Continuous playback loop — blocks on queue, writes to speaker."""
        if not self._stream:
            raise AudioDeviceNotFoundError("Call start() before run()")

        logger.info("Audio playback running")

        while self._running:
            try:
                audio_bytes = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue  # Check self._running flag periodically
            except asyncio.CancelledError:
                break

            try:
                await asyncio.to_thread(self._stream.write, audio_bytes)
            except IOError as exc:
                logger.warning("Speaker write error: %s", exc)

    def interrupt(self) -> None:
        """
        Drain the playback queue to stop audio immediately.

        Called when Gemini sends `interrupted=True` (barge-in).
        This is the WhisperFlow-style zero-latency cut.
        """
        dropped = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                dropped += 1
            except asyncio.QueueEmpty:
                break
        if dropped:
            logger.info("Interrupted playback — drained %d chunks", dropped)

    async def stop(self) -> None:
        """Release speaker resources."""
        self._running = False
        if self._stream:
            self._stream.close()
            self._stream = None
        if self._pya:
            self._pya.terminate()
            self._pya = None
        logger.info("Audio playback stopped")
