import asyncio
import time
from typing import Optional

import numpy as np
import structlog

from core.infra.event_bus import EventBus, TelemetryEvent

logger = structlog.get_logger("AetherOS.Telemetry.Stream")


class AudioTelemetryStream:
    """
    Analyzes real-time PCM audio segments (15Hz)
    to power paralinguistic visualizations in the Aether HUD.
    """

    def __init__(self, event_bus: EventBus, interval_sec: float = 0.066):
        self._bus = event_bus
        self._interval = interval_sec
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._current_buffer = bytearray()

    def feed_audio(self, pcm_data: bytes):
        self._current_buffer.extend(pcm_data)

    async def start(self):
        if self._running:
            return
        self._running = True
        self._loop_task = asyncio.create_task(self._analysis_loop())
        logger.info("Telemetry stream started.")

    async def stop(self):
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
        logger.info("Telemetry stream stopped.")

    async def _analysis_loop(self):
        while self._running:
            start_time = time.time()
            if self._current_buffer:
                audio_np = np.frombuffer(self._current_buffer, dtype=np.int16).astype(np.float32) / 32768.0
                self._current_buffer = bytearray()

                # Paralinguistics Calculation
                volume = np.sqrt(np.mean(audio_np**2)) if len(audio_np) > 0 else 0
                zero_crossings = np.nonzero(np.diff(np.sign(audio_np)))[0]
                pitch_est = len(zero_crossings) / (len(audio_np) / 16000) / 2 if len(audio_np) > 0 else 0

                spectrum = np.abs(np.fft.rfft(audio_np))
                freqs = np.fft.rfftfreq(len(audio_np), 1 / 16000)
                centroid = np.sum(freqs * spectrum) / np.sum(spectrum) if np.sum(spectrum) > 0 else 0

                await self._bus.publish(
                    TelemetryEvent(
                        timestamp=time.time(),
                        source="AudioTelemetry",
                        latency_budget=200,
                        metric_name="paralinguistics",
                        value=volume,
                        metadata={
                            "volume": float(volume),
                            "pitch_hz": float(pitch_est),
                            "spectral_centroid": float(centroid),
                        },
                    )
                )
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, self._interval - elapsed))
