"""
Aether Voice OS — Audio Capture.

Captures PCM audio from the system microphone via PyAudio using
high-performance C-callbacks and implements the "Thalamic Gate" — 
a software-defined Acoustic Echo Cancellation (AEC) layer.
"""
from __future__ import annotations

import asyncio
import logging
import queue
from typing import Optional

import numpy as np
import pyaudio

from core.audio.processing import energy_vad
from core.audio.state import audio_state
from core.config import AudioConfig
from core.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Microphone (C-Callback) → queue.Queue (Buffer) → asyncio.Queue (Downstream).

    The "Thalamic Gate" logic resides in the callback to minimize 
    latency between echo detection and suppression.
    """

    def __init__(
        self,
        config: AudioConfig,
        output_queue: asyncio.Queue[dict[str, object]],
    ) -> None:
        self._config = config
        self._async_queue = output_queue
        self._buffer: queue.Queue[bytes] = queue.Queue(maxsize=100)
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False

    def _callback(
        self, in_data: bytes, frame_count: int, time_info: dict, status: int
    ) -> tuple[bytes | None, int]:
        """
        High-priority Thalamic Gate callback.
        Analyzes energy and gates microphone input based on AI state.
        """
        # 1. Convert byte buffer to NumPy for DSP analysis
        pcm_chunk = np.frombuffer(in_data, dtype=np.int16)
        
        # 2. Check Thalamic State (is the AI currently speaking?)
        is_playing = audio_state.is_playing
        
        # 3. Dynamic Thresholding (AEC Simulation)
        # Normal threshold: 0.02 (Standard sensitivity)
        # Busy threshold: 0.15 (Suppresses AI echo from speakers)
        threshold = 0.15 if is_playing else 0.02
        
        vad = energy_vad(pcm_chunk, threshold=threshold)
        
        # 4. Gate Control
        # We pass the audio forward if:
        # a) It contains clear speech (突破 thershold)
        # b) The AI is silent (Thalamu is clear)
        if vad.is_speech or not is_playing:
            try:
                self._buffer.put_nowait(in_data)
            except queue.Full:
                # Overflow protection
                pass
        
        # We always return (None, paContinue) because we handle the 
        # actual data transfer via the thread-safe buffer queue.
        return (None, pyaudio.paContinue)

    async def start(self) -> None:
        """Open the microphone with high-performance callback."""
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
            "⚡ Thalamic Capture Active: %s @ %dHz (Callback Mode)",
            mic_info.get("name", "unknown"),
            self._config.send_sample_rate,
        )

        self._stream = self._pya.open(
            format=pyaudio.paInt16,
            channels=self._config.channels,
            rate=self._config.send_sample_rate,
            input=True,
            input_device_index=int(mic_info["index"]),
            stream_callback=self._callback,
            frames_per_buffer=self._config.chunk_size,
        )
        self._running = True

    async def run(self) -> None:
        """
        Feeds processed audio from the buffer to the asyncio queue.
        """
        if not self._stream:
            raise AudioDeviceNotFoundError("Call start() before run()")

        logger.info("Audio capture feeder running")

        while self._running:
            try:
                # 1. Wait for gated audio from callback
                data = await asyncio.to_thread(self._buffer.get)
                
                # 2. Package for AI session (Blob format)
                msg = {"data": data, "mime_type": f"audio/pcm;rate={self._config.send_sample_rate}"}
                
                # 3. Push to asyncio queue with overflow protection
                try:
                    self._async_queue.put_nowait(msg)
                except asyncio.QueueFull:
                    # Drop oldest to maintain real-time flow
                    try:
                        self._async_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    self._async_queue.put_nowait(msg)
                    
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Capture feeder error: %s", exc)
                await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Release audio resources."""
        self._running = False
        if self._stream:
            self._stream.stop_stream()
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
