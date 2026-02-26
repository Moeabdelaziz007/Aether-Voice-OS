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

from core.audio.processing import energy_vad, SilentAnalyzer, SilenceType, AdaptiveVAD
from core.audio.state import audio_state
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.config import AudioConfig
from core.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Microphone (C-Callback) → asyncio.Queue (Downstream).
    Direct Event-Loop Injection architecture eliminates thread-hopping latency.

    The "Thalamic Gate" logic resides in the callback to minimize 
    latency between echo detection and suppression.
    """

    def __init__(
        self,
        config: AudioConfig,
        output_queue: asyncio.Queue[dict[str, object]],
        analyzer: Optional[SilentAnalyzer] = None,
        vad_engine: Optional[AdaptiveVAD] = None,
        paralinguistic_analyzer: Optional[ParalinguisticAnalyzer] = None,
        on_affective_data: Optional[Callable[[ParalinguisticFeatures], Any]] = None,
    ) -> None:
        self._config = config
        self._async_queue = output_queue
        # We no longer need an intermediate queue.Queue
        self._pya: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._analyzer = analyzer or SilentAnalyzer()
        self._vad = vad_engine
        self._paralinguistic_analyzer = paralinguistic_analyzer
        self._on_affective_data = on_affective_data

    def _push_to_async_queue(self, msg: dict[str, object]) -> None:
        """Thread-safe injection into the asyncio event loop."""
        try:
            self._async_queue.put_nowait(msg)
        except asyncio.QueueFull:
            try:
                self._async_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            self._async_queue.put_nowait(msg)

    def _callback(
        self, in_data: bytes, frame_count: int, time_info: dict, status: int
    ) -> tuple[bytes | None, int]:
        """
        High-priority Thalamic Gate callback.
        Analyzes energy and gates microphone input based on AI state.
        """
        pcm_chunk = np.frombuffer(in_data, dtype=np.int16)
        # Thalamic Mute / AEC Proxy: 
        # If the AI is playing, we mute the microphone to prevent self-interruption (Echo).
        if is_playing:
            # Force VAD to false and energy to 0 to prevent barge-in triggers
            from core.audio.processing import HyperVADResult
            vad = HyperVADResult(is_soft=False, is_hard=False, energy_rms=0.0, sample_count=len(pcm_chunk))
            # Optional: Send zeros to the AI to maintain PCM continuity without noise
            in_data = b"\x00" * len(in_data)
        else:
            # HyperVAD Logic: Dual-Threshold (mu + sigma)
            vad = energy_vad(pcm_chunk, adaptive_engine=self._vad)
        
        # Update shared state for brain-sync
        audio_state.last_rms = vad.energy_rms
        audio_state.is_soft = vad.is_soft
        audio_state.is_hard = vad.is_hard
        
        zero_crossings = np.where(np.diff(np.sign(pcm_chunk)))[0]
        audio_state.last_zcr = len(zero_crossings) / len(pcm_chunk) if len(pcm_chunk) > 0 else 0
        
        # Architecture of Silence: Classify silence if no clear speech
        if not vad.is_hard:
            audio_state.silence_type = self._analyzer.classify(pcm_chunk, vad.energy_rms).value
        else:
            audio_state.silence_type = "speech"
            
            # Affective Analysis (Non-blocking trigger)
            if self._paralinguistic_analyzer and self._on_affective_data:
                features = self._paralinguistic_analyzer.analyze(pcm_chunk, vad.energy_rms)
                if self._loop and not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(self._on_affective_data, features)

        # Push to queue if hard speech detected or AI is silent (ambient feed)
        # Note: If is_playing is True, in_data is now silence (zeros), 
        # which satisfies the 'ambient feed' requirement safely.
        if vad.is_hard or not is_playing:
            msg = {
                "data": in_data,
                "mime_type": f"audio/pcm;rate={self._config.send_sample_rate}"
            }
            if self._loop and not self._loop.is_closed():
                self._loop.call_soon_threadsafe(self._push_to_async_queue, msg)
        
        return (None, pyaudio.paContinue)

    async def start(self) -> None:
        """Open the microphone with high-performance callback."""
        self._loop = asyncio.get_running_loop()
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
            "⚡ Thalamic Capture Active: %s @ %dHz (Direct Async Injection)",
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
        Keeps the capture lifecycle active for the TaskGroup.
        Audio routing is now handled natively via call_soon_threadsafe.
        """
        if not self._stream:
            raise AudioDeviceNotFoundError("Call start() before run()")

        logger.info("Audio capture task active (Zero-latency direct injection)")

        while self._running:
            await asyncio.sleep(1.0)

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
