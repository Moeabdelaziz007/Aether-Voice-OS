"""
Perception Pipeline — Component of the Aether Neural Spine.

Manages sensory data: audio streams, VAD, and vision frame correlation.
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
from typing import TYPE_CHECKING, Any, List

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
        
        # Sensory Queues (internal)
        self._audio_in: asyncio.Queue[dict] = asyncio.Queue(maxsize=100)
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)
        
        # Vision Buffer
        import collections
        self._frame_buffer: collections.deque[bytes] = collections.deque(maxlen=10)
        
        # Spatial Intelligence
        self._spatial_cortex = SpatialCortexAgent()
        
        # State Tracking
        self._last_vad_state = False
        self._running = False

    @property
    def audio_in(self) -> asyncio.Queue[dict]:
        return self._audio_in

    @property
    def audio_out(self) -> asyncio.Queue[bytes]:
        return self._audio_out

    @property
    def frame_buffer(self) -> Any:
        return self._frame_buffer

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

        await self._audio_in.put({
            "data": data,
            "mime_type": f"audio/pcm;rate={self._gateway_config.receive_sample_rate}",
        })

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

    def push_vision_frame(self, frame_bytes: bytes) -> None:
        self._frame_buffer.append(frame_bytes)

    async def get_spatial_pulse(self, client_id: str) -> dict:
        return await self._spatial_cortex.map_vision_to_spatial({
            "timestamp": time.time(),
            "client_id": client_id
        })
