"""
Perception Pipeline — Component of the Aether Neural Spine.

Manages sensory data: audio streams, VAD, and vision frame correlation.
"""

from __future__ import annotations

import logging
import math
import time
from typing import TYPE_CHECKING, Any

from core.ai.agents.spatial_cortex import SpatialCortexAgent
from core.audio.state import audio_state

if TYPE_CHECKING:
    from core.infra.config import GatewayConfig

logger = logging.getLogger(__name__)


class PerceptionPipeline:
    """
    Orchestrates audio/visual sensory processing and VAD loops.
    """

    def __init__(self, config: Any, gateway_config: GatewayConfig, broadcast_callback: Any) -> None:
        self._config = config
        self._gateway_config = gateway_config
        self._broadcast = broadcast_callback
        
        # Spatial Intelligence
        self._spatial_cortex = SpatialCortexAgent()
        
        # State Tracking
        self._last_vad_state = False
        self._running = False

        # Active AI Session injection point for Zero-Friction streaming
        self._active_session: Any = None

    def set_active_session(self, session: Any) -> None:
        """Link the active Gemini Live session for direct byte injection."""
        self._active_session = session

    async def start(self) -> None:
        """Starts the sensory pipeline."""
        self._running = True
        logger.info("Sensory pipeline active.")

    async def stop(self) -> None:
        self._running = False
        logger.info("Sensory pipeline stopped.")

    async def push_audio(self, data: bytes) -> None:
        if not self._running:
            return

        # Zero-Friction Direct Streaming: Bypass queues completely
        if self._active_session and getattr(self._active_session, "_session", None):
            try:
                # Fire and forget direct byte streaming
                # Check for correct data dict format
                await self._active_session._session.send_realtime_input(
                    [{"mime_type": f"audio/pcm;rate={self._gateway_config.receive_sample_rate}", "data": data}]
                )
            except Exception as e:
                logger.error("Direct audio stream failed: %s", e)

        # Emit VAD events to the UI when voice activity state changes
        if audio_state is None:
            return

        # Single source of truth for VAD
        current_vad = getattr(audio_state, "is_hard", False)
        
        if current_vad != self._last_vad_state:
            self._last_vad_state = current_vad
            rms = getattr(audio_state, "last_rms", 0.0001)
            energy_db = 20 * math.log10(max(0.0001, rms))
            
            # Direct await for reliable state synchronization
            await self._broadcast("vad", {
                "active": current_vad,
                "energy_db": float(energy_db),
                "ts_ms": int(time.time() * 1000)
            })

    async def push_vision_frame(self, frame_bytes: bytes) -> None:
        if not self._running:
            return

        # Zero-Friction Direct Streaming for Vision
        if self._active_session and getattr(self._active_session, "_session", None):
            try:
                from google.genai import types
                await self._active_session._session.send_realtime_input(
                    [types.Blob(data=frame_bytes, mime_type="image/webp")]
                )
            except Exception as e:
                logger.error("Direct vision stream failed: %s", e)

    async def get_spatial_pulse(self, client_id: str) -> dict:
        return await self._spatial_cortex.map_vision_to_spatial({
            "timestamp": time.time(),
            "client_id": client_id
        })
