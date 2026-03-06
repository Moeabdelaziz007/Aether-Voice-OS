"""
Aether Voice OS — Audio Capture.

Captures PCM audio from the system microphone via PyAudio using
high-performance C-callbacks and implements the "Thalamic Gate" —
a software-defined Acoustic Echo Cancellation (AEC) layer.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Optional

import numpy as np
import pyaudio

from core.audio.jitter_buffer import AdaptiveJitterBuffer
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.audio.processing import AdaptiveVAD, SilentAnalyzer
from core.audio.state import audio_state
from core.infra.config import AudioConfig
from core.utils.errors import AudioDeviceNotFoundError

__all__ = ["AdaptiveJitterBuffer", "AudioCapture", "SmoothMuter"]

logger = logging.getLogger(__name__)


class SmoothMuter:
    """Applies graceful, ramped gain modifications to avoid pops/clicks."""

    def __init__(self, ramp_samples: int = 256) -> None:
        """Initializes the SmoothMuter.

        Args:
            ramp_samples (int): The number of samples over which to apply the
                gain ramp, controlling the speed of the fade in/out.
        """
        self._ramp_samples = ramp_samples
        self._current_gain = 1.0
        self._target_gain = 1.0

    def process(self, pcm_chunk: np.ndarray) -> np.ndarray:
        """Apply gain ramp smoothly over the chunk.

        This method calculates and applies a linear gain ramp to the incoming
        audio chunk to smoothly transition between volume levels, preventing
        audible clicks or pops.

        Args:
            pcm_chunk: A numpy array of int16 PCM audio data.

        Returns:
            A numpy array of int16 PCM audio data with the gain applied.
        """
        if self._current_gain == self._target_gain:
            if self._current_gain == 1.0:
                return pcm_chunk.copy()
            elif self._current_gain == 0.0:
                return np.zeros_like(pcm_chunk)
            return (pcm_chunk * self._current_gain).astype(np.int16)

        chunk_len = len(pcm_chunk)
        if chunk_len == 0:
            return pcm_chunk

        if self._ramp_samples <= 0:
            self._current_gain = self._target_gain
            return (pcm_chunk * self._current_gain).astype(np.int16)

        if abs(self._current_gain - self._target_gain) < 1e-5:
            self._current_gain = self._target_gain
            return (pcm_chunk * self._current_gain).astype(np.int16)

        # Recursive Exponential Filter (EMA) gain ramping
        # alpha determines the speed of convergence. 
        # We want to reach ~99% of target in self._ramp_samples.
        alpha = np.exp(np.log(0.01) / self._ramp_samples)
        
        gains = np.zeros(chunk_len, dtype=np.float32)
        current = self._current_gain
        for i in range(chunk_len):
            current = current * alpha + self._target_gain * (1 - alpha)
            gains[i] = current
            
        self._current_gain = float(current)
        
        # Snap to target if we are effectively there
        if abs(self._current_gain - self._target_gain) < 1e-3:
            self._current_gain = self._target_gain
            
        return (pcm_chunk * gains).astype(np.int16)

    def mute(self) -> None:
        """Initiates a smooth fade-out to silence."""
        self._target_gain = 0.0

    def unmute(self) -> None:
        """Initiates a smooth fade-in to full volume."""
        self._target_gain = 1.0


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
        """Initializes the AudioCapture service.

        This class is responsible for capturing audio from the microphone,
        running the "Thalamic Gate" AEC logic, and pushing the resulting
        audio data to a queue for downstream processing.

        Args:
            config: The audio configuration object.
            output_queue: The asyncio queue to which captured audio chunks are sent.
            analyzer: An optional SilentAnalyzer for classifying silence types.
            vad_engine: An optional AdaptiveVAD engine for voice activity detection.
            paralinguistic_analyzer: An optional analyzer for affective computing.
            on_affective_data: An optional callback to handle affective features.
        """
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
        self._leakage_task: Optional[asyncio.Task] = None
        self._last_pcm_chunk: Optional[np.ndarray] = None
        self._chunk_lock = threading.Lock()

        from core.audio.leakage import LeakageDetector
        from core.audio.state import HysteresisGate

        self._hysteresis = HysteresisGate()
        self._leakage = LeakageDetector()
        self._smooth_muter = SmoothMuter()

        # Delay Compensation Counters
        self._audio_latency_ms = 50  # hardware latency approximation
        self._latency_samples = int(
            self._audio_latency_ms * self._config.send_sample_rate // 1000
        )
        self._mute_delay_remaining = 0
        self._unmute_delay_remaining = 0

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
        Analyzes energy and gates microphone input based on AI state and Leakage.
        """
        pcm_chunk = np.frombuffer(in_data, dtype=np.int16)

        # 1. Leakage & Correlation check (is it just echo?)
        # Store for background processing
        with self._chunk_lock:
            self._last_pcm_chunk = pcm_chunk

        # Fetch pre-computed score from background pulse
        is_user = self._leakage.last_score < 0.7

        # 2. Base Hysteresis update on AI state
        ai_playing_base = self._hysteresis.update(audio_state.is_playing)

        # 3. Delay Compensation (Hardware Latency & Echo fade-out)
        if audio_state.just_started_playing:
            self._mute_delay_remaining = self._latency_samples
        if audio_state.just_stopped_playing:
            self._unmute_delay_remaining = int(
                self._latency_samples * 1.5
            )  # grace period for echo to die

        if self._mute_delay_remaining > 0:
            self._mute_delay_remaining = max(
                0, self._mute_delay_remaining - frame_count
            )
            ai_playing_compensated = False
        elif self._unmute_delay_remaining > 0:
            self._unmute_delay_remaining = max(
                0, self._unmute_delay_remaining - frame_count
            )
            ai_playing_compensated = True
        else:
            ai_playing_compensated = ai_playing_base

        # 4. Final Thalamic Mute Decision
        # If AI is deemed playing AND we are sure it's not the user talking
        should_mute = ai_playing_compensated and not is_user

        if should_mute:
            self._smooth_muter.mute()
        else:
            self._smooth_muter.unmute()

        # Apply Graceful Ramp
        processed_chunk = self._smooth_muter.process(pcm_chunk)

        # Update VAD logic
        if should_mute and self._smooth_muter._current_gain < 0.1:
            # Force VAD to false and energy to 0 to prevent barge-in triggers
            from core.audio.processing import HyperVADResult

            vad = HyperVADResult(
                is_soft=False,
                is_hard=False,
                energy_rms=0.0,
                sample_count=len(processed_chunk),
            )
            # Reconstruct in_data with zeros if fully muted
            in_data = b"\x00" * len(in_data)
        else:
            from core.audio.processing import energy_vad

            # HyperVAD Logic: Dual-Threshold (mu + sigma) + Multi-Feature
            vad = energy_vad(processed_chunk, adaptive_engine=self._vad)
            in_data = processed_chunk.tobytes()

        # Update shared state for brain-sync
        audio_state.last_rms = vad.energy_rms
        audio_state.is_soft = vad.is_soft
        audio_state.is_hard = vad.is_hard

        zero_crossings = np.where(np.diff(np.sign(processed_chunk)))[0]
        audio_state.last_zcr = (
            len(zero_crossings) / len(processed_chunk)
            if len(processed_chunk) > 0
            else 0
        )

        # Architecture of Silence: Classify silence if no clear speech
        if not vad.is_hard:
            audio_state.silence_type = self._analyzer.classify(
                processed_chunk, vad.energy_rms
            ).value
        else:
            audio_state.silence_type = "speech"

        if self._paralinguistic_analyzer and self._on_affective_data:
            if vad.is_hard or vad.energy_rms < 0.05:
                features = self._paralinguistic_analyzer.analyze(
                    processed_chunk, vad.energy_rms
                )
                if self._loop and not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(self._on_affective_data, features)

        # Push to queue if hard speech detected or AI is silent (ambient feed)
        if vad.is_hard or not should_mute:
            msg = {
                "data": in_data,
                "mime_type": f"audio/pcm;rate={self._config.send_sample_rate}",
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
        self._leakage_task = asyncio.create_task(self._leakage_pulse_loop())

    async def _leakage_pulse_loop(self) -> None:
        """Background loop to compute leakage scores without blocking audio IO."""
        logger.debug("Leakage pulse loop started")
        while self._running:
            # Sync spectrum from global state
            if audio_state.ai_spectrum is not None:
                self._leakage.capture_ai_spectrum(audio_state.ai_spectrum)

            pcm = None
            with self._chunk_lock:
                if self._last_pcm_chunk is not None:
                    pcm = self._last_pcm_chunk.copy()
            
            if pcm is not None:
                # Perform the heavy FFT + Correlation here
                self._leakage.calculate_score(pcm)
            
            # Pulse every 20ms or so (matches typical frame sizes)
            await asyncio.sleep(0.02)

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
        if self._leakage_task:
            self._leakage_task.cancel()
            self._leakage_task = None
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
