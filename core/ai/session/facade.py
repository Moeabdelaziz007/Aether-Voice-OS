from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from core.ai.genetic import AgentDNA
    from core.infra.transport.gateway import AetherGateway

from google import genai
from google.genai import types

from core.ai.generative_init import get_genai_client
from core.ai.handover_protocol import HandoverContext
from core.ai.thalamic import ThalamicGate
from core.identity.package import SoulManifest
from core.infra.config import AIConfig
from core.utils.errors import AIConnectionError, AISessionExpiredError

from .caching import AetherContextCacheManager
from .config_builder import build_session_config
from .handover_bridge import (
    build_system_instruction,
    clear_handover_context,
    complete_handover_acknowledgment,
    export_handover_state,
    format_handover_context_for_instruction,
    inject_handover_context,
    restore_handover_state,
)
from .io_loops import drain_output, handle_usage, receive_loop, send_loop
from .sensory_manager import SensoryManager
from .tool_dispatch import handle_tool_call
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class GeminiLiveSession:
    """
    Bidirectional audio session with Gemini Live API.
    A unified, high-performance orchestrator for Aether's AI consciousness.
    """

    def __init__(
        self,
        config: AIConfig,
        gateway: "AetherGateway",
        audio_in_queue: Optional[asyncio.Queue[dict[str, object]]] = None,
        audio_out_queue: Optional[asyncio.Queue[bytes]] = None,
        on_interrupt: Optional[Callable] = None,
        on_tool_call: Optional[Callable] = None,
        tool_router: Optional[Any] = None,
        soul_manifest: Optional["SoulManifest"] = None,
        scheduler: Optional[Any] = None,
        agent_registry: Optional[Any] = None,
        firebase: Optional[Any] = None,
    ) -> None:
        self._config = config
        self._soul = soul_manifest
        self._in_queue = audio_in_queue
        self._out_queue = audio_out_queue
        self._gateway = gateway
        self._on_interrupt = on_interrupt
        self._on_tool_call = on_tool_call
        self._tool_router = tool_router
        self._scheduler = scheduler
        self._agent_registry = agent_registry
        self._firebase = firebase
        if self._scheduler:
            self._scheduler.set_echo_callback(self._inject_echo)

        self._client: Optional[genai.Client] = None
        self._session = None
        self._running = False

        # Modular Components
        self._tool_registry = ToolRegistry()
        self._sensory = SensoryManager(self, gateway)
        
        from .forge_orchestrator import ForgeOrchestrator
        self._forge = ForgeOrchestrator(self)

        # Session State
        self._output_queue_drops = 0
        self._active_handoffs: dict[str, dict] = {}
        self._injected_handover_context: Optional[HandoverContext] = None
        self._handover_acknowledgments: Dict[str, str] = {}
        self._start_time: datetime = datetime.now()
        
        # Caching & Neural Memory
        self._cache_manager = AetherContextCacheManager(config.api_key)
        self._cached_content_name: Optional[str] = None
        
        # Reliability & Budget
        self._retry_count = 0
        self._max_retries = 3
        self._token_budget = 50000 
        self._tokens_used = 0
        
        # Firestore Evidence Logger
        try:
            from google.cloud import firestore
            self._db = firestore.Client(project=os.environ.get("FIRESTORE_PROJECT"))
        except Exception as e:
            logger.warning("Failed to initialize Firestore client: %s", e)
            self._db = None

    def is_ready(self) -> bool:
        return self._running and self._session is not None

    def _build_session_config(self) -> types.LiveConnectConfig:
        return build_session_config(self)

    async def connect(self) -> None:
        while self._retry_count < self._max_retries:
            try:
                self._client = get_genai_client(
                    api_key=self._config.api_key,
                    api_version=self._config.api_version
                )
                from core.infra.config import GeminiModel
                self._config.model = self._config.model or GeminiModel.LIVE_FLASH
                logger.info(
                    "Connecting to Gemini Live (Attempt %d): model=%s version=%s",
                    self._retry_count + 1,
                    self._config.model.value,
                    self._config.api_version,
                )
                return
            except Exception as exc:
                self._retry_count += 1
                wait = 2 ** self._retry_count
                logger.warning("Connection failed, retrying in %ds... (%s)", wait, exc)
                await asyncio.sleep(wait)
        raise AIConnectionError("Max retries exceeded for Gemini Live connection")

    async def run(self) -> None:
        if not self._client:
            raise AIConnectionError("Call connect() before run()")

        config = self._build_session_config()
        self._running = True

        try:
            async with self._client.aio.live.connect(model=self._config.model.value, config=config) as session:
                self._session = session
                logger.info("✦ Gemini Live session established")

                # Neural Spine: Warm up context cache if mission is heavy
                if self._soul and hasattr(self._soul, "memories") and len(self._soul.memories) > 5:
                    logger.info("A2A [NEURAL] MISSION COMPLEXITY DETECTED. Warming cache...")
                    try:
                        memories = [m.get("content", str(m)) for m in self._soul.memories]
                        self._cached_content_name = await self._cache_manager.create_memory_cache(
                            model_name=self._config.model.value,
                            system_instruction=self._build_system_instruction(),
                            memories=memories
                        )
                    except Exception as e:
                        logger.error("Failed to warm context cache: %s", e)

                try:
                    self._thalamic_gate = ThalamicGate(session)
                    await self._thalamic_gate.start()
                except Exception as e:
                    logger.error("Failed to wire Thalamic Gate: %s", e)

                async with asyncio.TaskGroup() as tg:
                    # Note: send_loop might not be needed for audio if using direct injection,
                    # but kept for text/tools. receive_loop is still needed for output.
                    if self._in_queue:
                        tg.create_task(send_loop(self, session))
                    tg.create_task(receive_loop(self, session))

                    # Start specialized sensory loops via SensoryManager
                    tg.create_task(self._sensory.start_loops(session))

        except Exception as exc:
            if isinstance(exc, asyncio.CancelledError):
                logger.info("Session cancelled (shutdown)")
            else:
                logger.error("Session error: %s", exc, exc_info=True)
                raise AISessionExpiredError(f"Gemini session terminated: {exc}") from exc
        finally:
            if hasattr(self, "_thalamic_gate"):
                self._thalamic_gate.stop()
            self._sensory.stop()
            self._session = None
            self._running = False
            logger.info("Gemini Live session closed")

    def _handle_usage(self, response: types.LiveConnectResponse) -> None:
        handle_usage(self, response)

    async def _handle_tool_call(self, session, tool_call) -> None:
        await handle_tool_call(self, session, tool_call)

    def _drain_output(self) -> None:
        drain_output(self)

    async def stop(self) -> None:
        self._running = False
        self._sensory.stop()
        logger.info("Gemini session stop requested")

    async def inject_dna_update(self, dna: AgentDNA, rationales: List[str]) -> None:
        if not self._session or not self._running:
            return
        dna_dict = dna.to_dict()
        instr = (
            f"[SYSTEM: DNA MUTATION ACTIVE. Behavioral traits updated: "
            f"Verbosity={dna_dict['verbosity']:.2f}, Empathy={dna_dict['empathy']:.2f}, "
            f"Proactivity={dna_dict['proactivity']:.2f}. "
            f"Rationale: {'; '.join(rationales)}. Adapt your tone immediately.]"
        )
        try:
            await self._session.send_realtime_input(text=instr)
            logger.info("⚡ Session: Injected Hot-DNA update instruction.")
        except Exception as e:
            logger.error("Failed to inject DNA update: %s", e)

    async def send_text(self, text: str) -> bool:
        if not self._session or not self._running:
            return False
        try:
            await self._session.send_realtime_input(text=text)
            return True
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False

    def _build_system_instruction(self) -> str:
        return build_system_instruction(self)

    def _format_handover_context_for_instruction(self) -> str:
        return format_handover_context_for_instruction(self)

    def inject_handover_context(self, context: HandoverContext, visual_frames: List[bytes] = None) -> bool:
        self._injected_handover_context = context
        if visual_frames:
            asyncio.create_task(self._inject_frames(visual_frames))
        if self._db:
            try:
                self._db.collection("handover_traces").add({
                    "session_id": id(self),
                    "target_soul": context.target_soul,
                    "timestamp": datetime.now(),
                    "frame_count": len(visual_frames) if visual_frames else 0,
                    "tokens_used_at_handover": self._tokens_used
                })
            except Exception as e:
                logger.error("Firestore log failed: %s", e)
        return inject_handover_context(self, context)

    def track_tokens(self, tokens: int) -> None:
        self._tokens_used += tokens
        if self._tokens_used > self._token_budget:
            logger.warning("Token budget exceeded: %d / %d", self._tokens_used, self._token_budget)

    async def _inject_frames(self, frames: List[bytes]):
        if not self._session or not self._running:
            return
        for f in frames:
            try:
                await self._session.send_realtime_input(video=types.Blob(data=f, mime_type="image/webp"))
            except Exception as e:
                logger.error("Failed to inject visual frames: %s", e)

    def clear_handover_context(self) -> None:
        clear_handover_context(self)

    async def _inject_echo(self, echo: str) -> None:
        if not self._session or not self._running:
            return
        try:
            await self._session.send_realtime_input(text=f"[thought: {echo}]")
        except Exception as e:
            logger.error("Echo failed: %s", e)

    def get_handover_acknowledgment(self, handover_id: str) -> Optional[str]:
        return self._handover_acknowledgments.get(f"ack-{handover_id}")

    def is_handover_acknowledged(self, handover_id: str) -> bool:
        return self.get_handover_acknowledgment(handover_id) is not None

    def get_active_handover(self) -> Optional[HandoverContext]:
        return self._injected_handover_context

    def complete_handover_acknowledgment(self, handover_id: str, success: bool, message: str = "") -> bool:
        return complete_handover_acknowledgment(self, handover_id, success, message)

    def export_handover_state(self) -> Dict[str, Any]:
        return export_handover_state(self)

    def restore_handover_state(self, state: Dict[str, Any]) -> bool:
        return restore_handover_state(self, state)

