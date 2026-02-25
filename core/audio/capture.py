"""
Aether Voice OS — Audio Capture.

Captures PCM audio from the system microphone via PyAudio
and pushes chunks into an asyncio.Queue for downstream consumption.

Runs as an independent async task inside the engine's TaskGroup.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import pyaudio

from core.config import AudioConfig
from core.errors import AudioDeviceNotFoundError, AudioOverflowError

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Microphone → asyncio.Queue bridge.

    Reads PCM frames from PyAudio in a background thread
    (via asyncio.to_thread) to avoid blocking the event loop.
    """

    def __init__(
        self,
        config: AudioConfig,
        output_queue: asyncio.Queue[dict[str, object]],
    ) -> None:
        self._config = config
        self._queue = output_queue
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False

    async def start(self) -> None:
        """Open the microphone and begin capturing."""
        self._pya = pyaudio.PyAudio()

        try:
            mic_info = self._pya.get_default_input_device_info()
        except IOError as exc:
            raise AudioDeviceNotFoundError(
                "No default input device found. Check your microphone.",
                cause=exc,
                context={"available_devices": self._list_devices()},
            ) from exc

        logger.info(
            "Opening mic: %s @ %dHz, chunk=%d",
            mic_info.get("name", "unknown"),
            self._config.send_sample_rate,
            self._config.chunk_size,
        )

        self._stream = await asyncio.to_thread(
            self._pya.open,
            format=pyaudio.paInt16,
            channels=self._config.channels,
            rate=self._config.send_sample_rate,
            input=True,
            input_device_index=int(mic_info["index"]),
            frames_per_buffer=self._config.chunk_size,
        )
        self._running = True

    async def run(self) -> None:
        """
        Continuous capture loop.

        Reads audio in a thread and pushes Blob-ready dicts
        into the output queue. Back-pressure is handled by
        the queue's maxsize — if the consumer is slow, old
        chunks are dropped (lossy, not blocking).
        """
        if not self._stream:
            raise AudioDeviceNotFoundError("Call start() before run()")

        logger.info("Audio capture running")
        kwargs = {"exception_on_overflow": False} if __debug__ else {}

        while self._running:
            try:
                data = await asyncio.to_thread(
                    self._stream.read, self._config.chunk_size, **kwargs
                )
            except IOError as exc:
                logger.warning("Audio read overflow: %s", exc)
                continue

            msg = {"data": data, "mime_type": "audio/pcm"}

            try:
                self._queue.put_nowait(msg)
            except asyncio.QueueFull:
                # Drop oldest chunk to prevent blocking
                try:
                    self._queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                self._queue.put_nowait(msg)
                logger.debug("Mic queue full — dropped oldest chunk")

    async def stop(self) -> None:
        """Release audio resources."""
        self._running = False
        if self._stream:
            self._stream.close()
            self._stream = None
        if self._pya:
            self._pya.terminate()
            self._pya = None
        logger.info("Audio capture stopped")

    def _list_devices(self) -> list[str]:
        """List available audio device names for error context."""
        if not self._pya:
            return []
        return [
            str(self._pya.get_device_info_by_index(i).get("name", f"device-{i}"))
            for i in range(self._pya.get_device_count())
        ]
