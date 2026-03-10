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
        
        # Sensory Queues
        self._audio_in: asyncio.Queue[dict[str, object]] = asyncio.Queue(
            maxsize=self._config.mic_queue_max
        )
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=15)
        
        # Vision Buffer
        self._frame_buffer_cache: List[bytes] = []
        self._max_frame_cache = 5
        
        # Spatial Intelligence
        self._spatial_cortex = SpatialCortexAgent()
        
        # State Tracking
        self._last_vad_state = False
        self._running = False

    @property
    def audio_in(self) -> asyncio.Queue[dict[str, object]]:
        return self._audio_in

    @property
    def audio_out(self) -> asyncio.Queue[bytes]:
        return self._audio_out

    @property
    def frame_buffer(self) -> List[bytes]:
        return self._frame_buffer_cache

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def push_audio(self, data: bytes) -> None:
        await self._audio_in.put({
            "data": data,
            "mime_type": f"audio/pcm;rate={self._gateway_config.receive_sample_rate}",
        })

    def push_vision_frame(self, frame_bytes: bytes) -> None:
        self._frame_buffer_cache.append(frame_bytes)
        if len(self._frame_buffer_cache) > self._max_frame_cache:
            self._frame_buffer_cache.pop(0)

    async def get_spatial_pulse(self, client_id: str) -> dict:
        return await self._spatial_cortex.map_vision_to_spatial({
            "timestamp": time.time(),
            "client_id": client_id
        })

    async def _vad_loop(self) -> None:
        while self._running:
            await asyncio.sleep(0.05)
            try:
                if audio_state is None:
                    continue

                current_vad = (
                    audio_state.aec_double_talk
                    if hasattr(audio_state, "aec_double_talk")
                    else audio_state.is_hard
                )
                
                if current_vad != self._last_vad_state:
                    self._last_vad_state = current_vad
                    energy_db = 20 * math.log10(max(0.0001, audio_state.last_rms))
                    
                    await self._broadcast("vad", {
                        "active": current_vad,
                        "energy_db": float(energy_db),
                        "ts_ms": int(time.time() * 1000)
                    })
            except Exception as e:
                logger.error("Error in perception VAD loop: %s", e)
