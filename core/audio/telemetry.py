import numpy as np
import time
import asyncio
import logging
from typing import Optional
from core.infra.event_bus import EventBus, TelemetryEvent

logger = logging.getLogger("AetherOS.Telemetry")

# ==========================================
# 🌌 Audio Telemetry Engine
# Calculating paralinguistic features at 15Hz
# to power the Aether HUD visualization.
# ==========================================

class AudioTelemetry:
    """
    Analyzes PCM audio segments and broadcasts 
    mathematical paralinguistics into the Tier 3 Telemetry bus.
    """
    def __init__(self, event_bus: EventBus, interval_sec: float = 0.066): # ~15Hz
        self._bus = event_bus
        self._interval = interval_sec
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        
        # Internal Analysis Accumulator
        self._current_buffer = bytearray()

    def feed_audio(self, pcm_data: bytes):
        """Accumulate audio for the next analysis window."""
        self._current_buffer.extend(pcm_data)

    async def start(self):
        """Start the telemetry broadcast loop."""
        if self._running: return
        self._running = True
        self._loop_task = asyncio.create_task(self._analysis_loop())
        logger.info("[Telemetry] Broadcast loop started at 15Hz.")

    async def stop(self):
        """Stop the telemetry broadcast loop."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
        logger.info("[Telemetry] Broadcast loop stopped.")

    async def _analysis_loop(self):
        """Periodic analysis and event emission."""
        while self._running:
            start_time = time.time()
            
            if self._current_buffer:
                # 1. Convert bytearray to numpy
                audio_np = np.frombuffer(self._current_buffer, dtype=np.int16).astype(np.float32) / 32768.0
                self._current_buffer = bytearray() # Clear after read
                
                # 2. Calculate Paralinguistics
                # A. Volume (RMS)
                volume = np.sqrt(np.mean(audio_np**2)) if len(audio_np) > 0 else 0
                
                # B. Pitch (Simplified via zero-crossing rate)
                zero_crossings = np.nonzero(np.diff(np.sign(audio_np)))[0]
                pitch_est = len(zero_crossings) / (len(audio_np) / 16000) / 2 if len(audio_np) > 0 else 0
                
                # C. Spectral Centroid (Brightness/Timbre)
                spectrum = np.abs(np.fft.rfft(audio_np))
                freqs = np.fft.rfftfreq(len(audio_np), 1/16000)
                centroid = np.sum(freqs * spectrum) / np.sum(spectrum) if np.sum(spectrum) > 0 else 0

                # 3. Publish to Tier 3
                await self._bus.publish(TelemetryEvent(
                    timestamp=time.time(),
                    source="AudioTelemetry",
                    latency_budget=200, # Telemetry can tolerate more lag
                    metric_name="paralinguistics",
                    value=volume,
                    metadata={
                        "volume": float(volume),
                        "pitch_hz": float(pitch_est),
                        "spectral_centroid": float(centroid)
                    }
                ))

            # Maintain constant frequency
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, self._interval - elapsed))
