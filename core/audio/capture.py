"""
Aether Voice OS — Audio Capture.

Captures PCM audio from the system microphone via PyAudio using
high-performance C-callbacks and implements the "Thalamic Gate" —
a software-defined Acoustic Echo Cancellation (AEC) layer.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Callable, Optional

import numpy as np
import pyaudio

from core.audio.cortex import AECBridge
from core.audio.dynamic_aec import DynamicAEC
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.audio.processing import (
    AdaptiveVAD,
    HyperVADResult,
    SilentAnalyzer,
    energy_vad,
)
from core.audio.state import HysteresisGate, audio_state
from core.infra.config import AudioConfig
from core.utils.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class SmoothMuter:
    """Applies graceful, ramped gain modifications to avoid pops/clicks.

    Design goals:
    - No discontinuities at chunk boundaries (avoid clicks/pops)
    - Deterministic ramps that land exactly on the target gain
    - Minimal per-callback allocation / branching
    """

    def __init__(self, ramp_samples: int = 256) -> None:
        """Initializes the SmoothMuter.

        Args:
            ramp_samples: Number of samples over which to apply a full 0→1 or 1→0 ramp.
        """
        self._ramp_samples = max(1, int(ramp_samples))
        self._current_gain = 1.0
        self._target_gain = 1.0

    def process(self, pcm_chunk: np.ndarray) -> np.ndarray:
        """Apply gain ramp smoothly over the chunk.

        Returns a new int16 array (never returns the original buffer) to avoid
        unexpected aliasing.
        """
        chunk_len = len(pcm_chunk)
        if chunk_len == 0:
            return pcm_chunk

        # Fast paths
        if self._current_gain == self._target_gain:
            if self._current_gain == 1.0:
                return pcm_chunk.copy()
            if self._current_gain == 0.0:
                return np.zeros_like(pcm_chunk)
            return (pcm_chunk.astype(np.float32) * self._current_gain).astype(np.int16)

        start = float(self._current_gain)
        target = float(self._target_gain)

        # How many samples remain to reach the target, based on a linear ramp
        # of length `self._ramp_samples` for a full-scale delta of 1.0.
        delta = target - start
        remaining = int(np.ceil(abs(delta) * self._ramp_samples))

        # Optional: Keep a very tiny snap just for IEEE float math drift
        if abs(self._current_gain - self._target_gain) < 1e-4:
            self._current_gain = self._target_gain

        if remaining <= 0:
            self._current_gain = target
            gains = np.full(chunk_len, target, dtype=np.float32)
        else:
            ramp_len = min(chunk_len, remaining)

            # Use endpoint=True so the last sample of the ramp hits the exact
            # intermediate value (or the target if ramp completes in this chunk).
            ramp = np.linspace(
                start,
                start + delta * (ramp_len / remaining),
                ramp_len,
                dtype=np.float32,
            )

            gains = np.empty(chunk_len, dtype=np.float32)
            gains[:ramp_len] = ramp

            if ramp_len < chunk_len:
                # Ramp completed inside this chunk → hold exactly at target.
                if ramp_len == remaining:
                    gains[ramp_len:] = target
                    self._current_gain = target
                else:
                    hold = float(gains[ramp_len - 1])
                    gains[ramp_len:] = hold
                    self._current_gain = hold
            else:
                # Ramp continues in next chunk.
                self._current_gain = float(gains[-1])

        return (pcm_chunk.astype(np.float32) * gains).astype(np.int16)

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
        self._state_lock = threading.Lock()

        self._hysteresis = HysteresisGate()
        # Dynamic AEC replaces LeakageDetector with adaptive echo cancellation
        self._dynamic_aec = DynamicAEC(
            sample_rate=self._config.send_sample_rate,
            frame_size=self._config.chunk_size,
            filter_length_ms=100.0,
            step_size=0.5,
            convergence_threshold_db=15.0,
        )
        self._aec_bridge = AECBridge(filter_size=self._config.chunk_size)
        self._smooth_muter = SmoothMuter()

        # Delay Compensation Counters (kept for hardware latency, AEC handles echo path)
        self._audio_latency_ms = 50  # hardware latency approximation
        self._latency_samples = int(
            self._audio_latency_ms * self._config.send_sample_rate // 1000
        )
        self._mute_delay_remaining = 0
        self._unmute_delay_remaining = 0

        # Far-end buffer for AEC reference signal
        self._far_end_buffer = np.array([], dtype=np.int16)

    def _push_to_async_queue(self, msg: dict[str, object]) -> None:
        """Thread-safe injection into the asyncio event loop.

        On overflow we drop the oldest message to keep latency bounded.
        """
        try:
            self._async_queue.put_nowait(msg)
        except asyncio.QueueFull:
            # Telemetry: count capture queue drops.
            try:
                audio_state.capture_queue_drops += 1
            except Exception:
                # audio_state may be a mock in tests or older state object
                pass

            try:
                self._async_queue.get_nowait()
                if hasattr(audio_state, "capture_queue_drops"):
                    audio_state.capture_queue_drops += 1
            except asyncio.QueueEmpty:
                pass

            try:
                self._async_queue.put_nowait(msg)
            except asyncio.QueueFull:
                # If we still can't enqueue, drop this message as well.
                try:
                    audio_state.capture_queue_drops += 1
                except Exception:
                    pass

    def _callback(
        self, in_data: bytes, frame_count: int, time_info: dict, status: int
    ) -> tuple[bytes | None, int]:
        """
        High-priority Thalamic Gate callback.
        Analyzes energy and gates microphone input based on AI state and Leakage.
        """
        pcm_chunk = np.frombuffer(in_data, dtype=np.int16)

        # 1. Dynamic AEC Processing
        # Read bit-perfect far-end (AI output) reference from shared PCM buffer
        # This replaces the placeholder ai_spectrum logic for 10x precision.
        far_end_ref = audio_state.far_end_pcm.read_last(len(pcm_chunk))

        # Pad with zeros if reference buffer is underrun (startup/jitter)
        if len(far_end_ref) < len(pcm_chunk):
            padding = np.zeros(len(pcm_chunk) - len(far_end_ref), dtype=np.int16)
            far_end_ref = np.concatenate([far_end_ref, padding])

        cleaned_chunk, aec_state = self._dynamic_aec.process_frame(
            pcm_chunk, far_end_ref
        )

        # 1.5 ✦ Aether Cortex Acceleration (Rust Pass)
        # This will evolve to replace dynamic_aec.process_frame for ultra-low latency
        if self._aec_bridge.use_rust:
            # Note: Rust implementation expects float32/f32
            cleaned_float = cleaned_chunk.astype(np.float32) / 32768.0
            ref_float = far_end_ref.astype(np.float32) / 32768.0
            accelerated = self._aec_bridge.process(cleaned_float, ref_float)
            cleaned_chunk = (accelerated * 32768.0).astype(np.int16)

        # Update global AEC state for monitoring
        audio_state.update_aec_state(
            converged=aec_state.converged,
            convergence_progress=aec_state.convergence_progress,
            erle_db=aec_state.erle_db,
            delay_ms=aec_state.estimated_delay_ms,
            double_talk=aec_state.double_talk_detected,
        )

        # Check if user is speaking (post-AEC analysis)
        is_user = self._dynamic_aec.is_user_speaking(cleaned_chunk)

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

        # Apply Graceful Ramp to AEC-cleaned audio
        processed_chunk = self._smooth_muter.process(cleaned_chunk)

        # Update VAD logic
        if should_mute and self._smooth_muter._current_gain < 0.1:
            # Force VAD to false and energy to 0 to prevent barge-in triggers
            vad = HyperVADResult(
                is_soft=False,
                is_hard=False,
                energy_rms=0.0,
                sample_count=len(processed_chunk),
            )
            # Reconstruct in_data with zeros if fully muted
            in_data = b"\x00" * len(in_data)
        else:
            # HyperVAD Logic: Dual-Threshold (mu + sigma) + Multi-Feature
            vad = energy_vad(processed_chunk, adaptive_engine=self._vad)
            in_data = processed_chunk.tobytes()

        # Update shared state for brain-sync
        audio_state.last_rms = vad.energy_rms
        audio_state.is_soft = vad.is_soft
        audio_state.is_hard = vad.is_hard

        # Low-allocation ZCR (zero-crossing rate) calculation.
        # Count sign changes without building diff/sign/where intermediate arrays.
        if len(processed_chunk) > 1:
            prev = processed_chunk[:-1]
            curr = processed_chunk[1:]
            # Crossing when sign differs or either is zero.
            crossings = ((prev >= 0) != (curr >= 0)) | (prev == 0) | (curr == 0)
            audio_state.last_zcr = float(
                np.count_nonzero(crossings) / len(processed_chunk)
            )
        else:
            audio_state.last_zcr = 0.0

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
