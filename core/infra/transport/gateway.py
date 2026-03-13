"""
Aether Gateway v3.0 — The Neural Spine.

The central nervous system of the Aether Live Agent, coordinating 
transport (Liaison), sensory input (Perception), and AI cognition (Bridge).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from core.infra.transport.bridge import NeuralBridge
from core.infra.transport.liaison import ConnectionLiaison
from core.infra.transport.perception import PerceptionPipeline

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator
    from core.infra.config import AIConfig, GatewayConfig

logger = logging.getLogger(__name__)


class AetherGateway:
    """
    Orchestrates the Neural Spine: Liaison, Perception, and Bridge.
    """

    def __init__(
        self,
        config: GatewayConfig,
        ai_config: AIConfig,
        hive: HiveCoordinator,
        bus: Any,
        tool_router: Any,
    ) -> None:
        self.config = config
        self.ai_config = ai_config
        self.hive = hive
        self.bus = bus
        self.tool_router = tool_router

        # Neural Spine Components
        self.liaison = ConnectionLiaison(
            config=config,
            hive=hive,
            message_router=self._handle_message,
            binary_router=self._handle_binary,
        )
        self.perception = PerceptionPipeline(
            config=ai_config,
            gateway_config=config,
            broadcast_callback=self.broadcast
        )
        self.bridge = NeuralBridge(
            ai_config=ai_config,
            hive=hive,
            tool_router=tool_router,
            bus=bus,
            broadcast_callback=self.broadcast,
            perception=self.perception,
            gateway=self
        )

        self._running = False
        
        # O(1) Routing Map
        self._message_handlers = {
            "pre_warm_soul": self._on_pre_warm_soul,
            "request_state_sync": self._on_request_state_sync,
            "portal_input": self._on_portal_input,
            "tick": self._on_tick,
            "FORGE_COMMIT": self._on_forge_commit,
            "CLAW_INJECT": self._on_claw_inject,
        }

    async def start(self) -> None:
        """Bootstairs the entire Neural Spine."""
        self._running = True
        logger.info("Initializing Neural Spine...")
        
        await self.perception.start()
        await self.bridge.start()
        await self.liaison.start(self.liaison.handle_connection)
        
        logger.info("✦ Neural Spine Fully Operational.")

    async def stop(self) -> None:
        """Graceful shutdown of all subsystems."""
        self._running = False
        await self.liaison.stop()
        await self.bridge.stop()
        await self.perception.stop()
        logger.info("Neural Spine deactivated.")

    # --- Communication Interface ---

    async def broadcast(self, msg_type: str, payload: dict) -> None:
        """Broadcasts a JSON/Msgpack message to all connected clients."""
        await self.liaison.broadcast(msg_type, payload)

    async def broadcast_binary(self, data: bytes) -> None:
        """Broadcasts raw binary (usually audio) to all connected clients."""
        await self.liaison.broadcast_binary(data)

    # --- Routing Logic ---

    async def _handle_message(self, client_id: str, msg: dict) -> None:
        """Routes structured messages from clients with O(1) lookup."""
        m_type = msg.get("type")
        payload = msg.get("payload", {})

        handler = self._message_handlers.get(m_type)
        if handler:
            await handler(client_id, payload)
        else:
            logger.warning("Unknown message type received: %s", m_type)

    async def _on_pre_warm_soul(self, client_id: str, payload: dict) -> None:
        soul = payload.get("soul")
        if soul:
            await self.bridge.pre_warm_soul(soul)

    async def _on_request_state_sync(self, client_id: str, payload: dict) -> None:
        await self.bridge.state_manager.force_sync()

    async def _on_portal_input(self, client_id: str, payload: dict) -> None:
        # Emergency override logic
        pass

    async def _on_tick(self, client_id: str, payload: dict) -> None:
        """Echoes a tick message back for latency measurement."""
        await self.broadcast("tick", payload)

    async def _on_forge_commit(self, client_id: str, payload: dict) -> None:
        dna = payload.get("dna")
        if dna:
            await self.bridge.inject_dna_update(dna, ["User Forge Commitment"])

    async def _on_claw_inject(self, client_id: str, payload: dict) -> None:
        instructions = payload.get("instructions")
        if instructions:
            await self.bridge.inject_text_directive(instructions)

    async def _handle_binary(self, client_id: str, data: bytes) -> None:
        """Routes binary sensory data (audio/vision)."""
        # Header byte 0x01 = Audio, 0x02 = Vision
        if not data:
            return
        
        header = data[0]
        payload = data[1:]

        if header == 0x01: # Audio PCM
            await self.perception.push_audio(payload)
        elif header == 0x02: # Vision Frame
            self.perception.push_vision_frame(payload)

    # --- External Triggers (used by Hive/Bus/Bridge) ---

    def request_session_restart(self) -> None:
        """Triggers a Bridge restart (e.g. for Soul Handoff)."""
        self.bridge.request_restart()

    @property
    def session_state(self):
        """Bridge to the session state manager for external callers."""
        return self.bridge.state_manager
