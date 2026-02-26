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

from core.audio.state import audio_state
from core.config import AudioConfig
from core.errors import AudioDeviceNotFoundError

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
    ) -> None:
        self._config = config
        self._async_queue = input_queue
        self._buffer: queue.Queue[bytes] = queue.Queue(maxsize=100)
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False

    def _callback(
        self, in_data: bytes | None, frame_count: int, time_info: dict, status: int
    ) -> tuple[bytes | None, int]:
        """PyAudio callback running in a high-priority C-thread."""
        try:
            # Gemini typically sends chunks of 1024 or 2048 samples.
            # We fetch one chunk from the buffer.
            data = self._buffer.get_nowait()
            audio_state.set_playing(True)
            
            # If the chunk size doesn't match frame_count exactly, 
            # we might need to handle residue, but usually they align in this pipeline.
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
            frames_per_buffer=1024, # Standard Gemini buffer
        )
        
        self._running = True
        logger.info(
            "⚡ Thalamic Playback Active: Speaker opened @ %dHz (Callback Mode)", 
            self._config.receive_sample_rate
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
                
                # 2. Push to thread-safe buffer with lightweight async spinlock (Zero thread overhead)
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
