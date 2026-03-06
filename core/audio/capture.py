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
import time
from typing import Any, Callable, Optional

import numpy as np
import pyaudio

from core.audio.cortex import HAS_RUST_CORTEX, spectral_denoise
from core.audio.dynamic_aec import DynamicAEC
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.audio.processing import (
    AdaptiveVAD,
    HyperVADResult,
    SilentAnalyzer,
    energy_vad,
)
from core.audio.state import HysteresisGate, audio_state
from core.audio.telemetry import AudioTelemetryLogger
from core.infra.config import AudioConfig
from core.utils.errors import AudioDeviceNotFoundError

logger = logging.getLogger(__name__)


class AdaptiveJitterBuffer:
    """
    A software jitter buffer to smooth bursty playback/far-end arrivals,
    ensuring a stable reference signal for AEC to prevent convergence loss.
    """

    def __init__(
        self,
        target_latency_ms: float = 60.0,
        max_latency_ms: float = 200.0,
        sample_rate: int = 16000,
    ) -> None:
        self.sample_rate = sample_rate
        self.target_latency_samples = int(target_latency_ms * sample_rate / 1000)
        self.max_latency_samples = int(max_latency_ms * sample_rate / 1000)
        self.buffer = np.zeros(self.max_latency_samples, dtype=np.int16)
        self.write_idx = 0
        self.read_idx = 0
        self.size = 0

    def write(self, pcm_data: np.ndarray) -> None:
        """Append new far-end audio data."""
        data_len = len(pcm_data)
        if data_len == 0:
            return

        if data_len >= self.max_latency_samples:
            pcm_data = pcm_data[-self.max_latency_samples :]
            data_len = self.max_latency_samples

        end_idx = self.write_idx + data_len
        if end_idx <= self.max_latency_samples:
            self.buffer[self.write_idx : end_idx] = pcm_data
        else:
            overflow = end_idx - self.max_latency_samples
            first_part = data_len - overflow
            self.buffer[self.write_idx : self.max_latency_samples] = pcm_data[
                :first_part
            ]
            self.buffer[:overflow] = pcm_data[first_part:]

        self.write_idx = end_idx % self.max_latency_samples
        self.size = min(self.size + data_len, self.max_latency_samples)

        if self.size == self.max_latency_samples:
            self.read_idx = self.write_idx

    def read(self, num_samples: int) -> np.ndarray:
        """Read contiguous block of samples, zero-padding on underrun."""
        out = np.zeros(num_samples, dtype=np.int16)

        if self.size == 0:
            return out

        read_len = min(num_samples, self.size)
        end_idx = self.read_idx + read_len

        if end_idx <= self.max_latency_samples:
            out[:read_len] = self.buffer[self.read_idx : end_idx]
        else:
            overflow = end_idx - self.max_latency_samples
            first_part = read_len - overflow
            out[:first_part] = self.buffer[self.read_idx : self.max_latency_samples]
            out[first_part:read_len] = self.buffer[:overflow]

        self.read_idx = end_idx % self.max_latency_samples
        self.size -= read_len

        return out


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
        self._on_audio_telemetry = None
        self._last_telemetry_time = 0.0
        self._state_lock = threading.Lock()

        # Performance Telemetry Logger
        self._telemetry_logger: Optional[AudioTelemetryLogger] = None

        self._hysteresis = HysteresisGate()
        # Dynamic AEC replaces LeakageDetector with adaptive echo cancellation
        self._dynamic_aec = DynamicAEC(
            sample_rate=self._config.send_sample_rate,
            frame_size=self._config.chunk_size,
            filter_length_ms=self._config.aec_filter_length_ms,
            step_size=self._config.aec_step_size,
            convergence_threshold_db=self._config.aec_convergence_threshold_db,
        )
        self._smooth_muter = SmoothMuter()

        # Delay Compensation Counters (kept for hardware latency, AEC handles echo path)
        self._audio_latency_ms = 50  # hardware latency approximation
        self._latency_samples = int(
            self._audio_latency_ms * self._config.send_sample_rate // 1000
        )
        self._mute_delay_remaining = 0
        self._unmute_delay_remaining = 0

        # Adaptive Jitter Buffer for AEC reference signal
        self._jitter_buffer = AdaptiveJitterBuffer(
            target_latency_ms=self._config.jitter_buffer_target_ms,
            max_latency_ms=self._config.jitter_buffer_max_ms,
            sample_rate=self._config.send_sample_rate,
        )

    def set_telemetry_logger(self, logger: AudioTelemetryLogger) -> None:
        """Attach a telemetry logger for performance tracking."""
        self._telemetry_logger = logger

    def update_config(self, config: AudioConfig) -> None:
        """Update audio configuration dynamically during runtime."""
        # Update AEC parameters
        self._dynamic_aec.update_parameters(
            step_size=config.aec_step_size,
            filter_length_ms=config.aec_filter_length_ms,
            convergence_threshold_db=config.aec_convergence_threshold_db,
        )

        # Update jitter buffer parameters
        # Note: Jitter buffer recreation would be needed for target/max changes
        # For now, we'll just log the change
        logger.info(
            f"Audio config updated: jitter_target={config.jitter_buffer_target_ms}ms"
        )

        # Update mute/unmute delays
        self._latency_samples = int(
            self._audio_latency_ms * config.send_sample_rate // 1000
        )
        self._mute_delay_remaining = min(
            self._mute_delay_remaining, config.mute_delay_samples
        )
        self._unmute_delay_remaining = min(
            self._unmute_delay_remaining, config.unmute_delay_samples
        )

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
        # Start telemetry frame tracking
        if self._telemetry_logger:
            self._telemetry_logger.start_frame()

        time.perf_counter()
        pcm_chunk = np.frombuffer(in_data, dtype=np.int16)

        # 1. Dynamic AEC Processing
        # Read bit-perfect far-end (AI output) reference from shared PCM buffer
        # Write any new data to our jitter buffer
        new_far_end = audio_state.far_end_pcm.read_last(len(pcm_chunk))
        if len(new_far_end) > 0:
            self._jitter_buffer.write(new_far_end)

        # Read exactly chunk size from jitter buffer
        far_end_ref = self._jitter_buffer.read(len(pcm_chunk))

        aec_start = time.perf_counter()
        cleaned_chunk, aec_state = self._dynamic_aec.process_frame(
            pcm_chunk, far_end_ref
        )
        aec_latency_ms = (time.perf_counter() - aec_start) * 1000

        # 1.5 ✦ Aether Cortex Acceleration (Rust Spectral Denoise)
        if HAS_RUST_CORTEX:
            # Apply Rust-accelerated spectral denoising for cleaner output
            # spectral_denoise expects int16 and returns dict with 'samples'
            result = spectral_denoise(cleaned_chunk, noise_floor=0.02)
            cleaned_chunk = np.array(result["samples"], dtype=np.int16)

        # Update global AEC state for monitoring
        audio_state.update_aec_state(
            converged=aec_state.converged,
            convergence_progress=aec_state.convergence_progress,
            erle_db=aec_state.erle_db,
            delay_ms=aec_state.estimated_delay_ms,
            double_talk=aec_state.double_talk_detected,
        )

        # Record AEC metrics to telemetry
        if self._telemetry_logger:
            self._telemetry_logger.record_aec(
                latency_ms=aec_latency_ms,
                erle_db=aec_state.erle_db,
                converged=aec_state.converged,
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
        vad_start = time.perf_counter()
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
        vad_latency_ms = (time.perf_counter() - vad_start) * 1000

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

        # Telemetry Broadcast: Throttle to ~15Hz
        now = time.monotonic()
        if now - self._last_telemetry_time >= 1.0 / 15.0:
            self._last_telemetry_time = now
            if (
                getattr(self, "_on_audio_telemetry", None)
                and self._loop
                and not self._loop.is_closed()
            ):
                payload = {
                    "rms": float(vad.energy_rms),
                    "gain": float(self._smooth_muter._current_gain),
                    "aec_converged": audio_state.aec_converged,
                    "aec_erle": round(audio_state.aec_erle_db, 1),
                    "aec_delay_ms": round(audio_state.aec_delay_ms, 1),
                    "silence_type": audio_state.silence_type,
                    "zcr": round(audio_state.last_zcr, 3),
                }
                asyncio.run_coroutine_threadsafe(
                    self._on_audio_telemetry("audio_telemetry", payload), self._loop
                )

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

        # End telemetry frame tracking
        if self._telemetry_logger:
            self._telemetry_logger.record_vad(
                latency_ms=vad_latency_ms,
                is_speech=vad.is_hard,
                is_soft=vad.is_soft,
                rms_energy=vad.energy_rms,
            )
            self._telemetry_logger.end_frame()

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
            raise RuntimeError("Call start() before run()")

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
