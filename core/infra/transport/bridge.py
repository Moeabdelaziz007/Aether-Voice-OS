"""
Neural Bridge — Component of the Aether Neural Spine.

Manages AI session lifecycle, soul transitions, and brain-state synchronization.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

from core.ai.session import GeminiLiveSession
from core.infra.transport.session_manager import SessionManager
from core.infra.transport.session_state import SessionMetadata, SessionState, SessionStateManager

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator
    from core.infra.config import AIConfig

logger = logging.getLogger(__name__)


class NeuralBridge:
    """
    Manages Gemini Live sessions, Expert (Soul) handoffs, and pre-warming.
    """

    def __init__(
        self,
        ai_config: AIConfig,
        hive: HiveCoordinator,
        tool_router: Any,
        bus: Any,
        broadcast_callback: Any,
        perception: Any,
        gateway: Any
    ) -> None:
        self._ai_config = ai_config
        self._hive = hive
        self._tool_router = tool_router
        self._bus = bus
        self._perception = perception
        self._gateway = gateway
        
        self._state_manager = SessionStateManager(
            broadcast_callback=broadcast_callback, bus=self._bus
        )
        self._session_manager = SessionManager(engine_session=None)
        self._warmed_souls: Dict[str, GeminiLiveSession] = {}
        self._pre_warm_lock = asyncio.Lock()
        self._session_restart_event = asyncio.Event()
        self._running = False

    @property
    def state_manager(self) -> SessionStateManager:
        return self._state_manager

    async def start(self) -> None:
        self._running = True
        await self._state_manager.initialize()
        await self._state_manager.start_health_monitoring()
        asyncio.create_task(self._session_loop())

    async def stop(self) -> None:
        self._running = False
        await self._state_manager.stop_health_monitoring()
        session = self._state_manager.session
        if session:
            await session.stop()
        async with self._pre_warm_lock:
            for s in self._warmed_souls.values():
                await s.stop()
            self._warmed_souls.clear()

    def request_restart(self) -> None:
        self._session_restart_event.set()

    async def pre_warm_soul(self, soul_name: str) -> None:
        async with self._pre_warm_lock:
            if not self._running or soul_name in self._warmed_souls:
                return
            
            if len(self._warmed_souls) >= 5:
                oldest = next(iter(self._warmed_souls))
                await self._warmed_souls.pop(oldest).stop()

            try:
                target_soul = self._hive._registry.get(soul_name)
                session = GeminiLiveSession(
                    config=self._ai_config,
                    audio_in_queue=self._perception.audio_in,
                    audio_out_queue=self._perception.audio_out,
                    gateway=self._gateway,
                    on_interrupt=self._on_interrupt,
                    on_tool_call=self._on_tool_call,
                    tool_router=self._tool_router,
                    soul_manifest=target_soul,
                )
                await session.connect()
                self._warmed_souls[soul_name] = session
                logger.info("✦ Pre-warm: Soul %s ready", soul_name)
            except Exception as e:
                logger.error("✦ Pre-warm failed for %s: %s", soul_name, e)

    async def _session_loop(self) -> None:
        while self._running:
            try:
                await self._run_iteration()
            except Exception as e:
                logger.error("Bridge iteration failed: %s", e, exc_info=True)
                await self._state_manager.transition_to(SessionState.ERROR, f"Iter: {str(e)[:50]}")
                await asyncio.sleep(5)

    async def _run_iteration(self) -> None:
        self._session_restart_event.clear()
        active_soul = self._hive.active_soul
        soul_name = active_soul.manifest.name if active_soul else "Unknown"

        metadata = SessionMetadata(
            session_id=str(uuid.uuid4()),
            soul_name=soul_name,
            started_at=datetime.now(),
        )

        await self._state_manager.transition_to(
            SessionState.INITIALIZING, f"Booting {soul_name}", metadata=metadata
        )

        async with self._pre_warm_lock:
            if soul_name in self._warmed_souls:
                session = self._warmed_souls.pop(soul_name)
            else:
                session = GeminiLiveSession(
                    config=self._ai_config,
                    audio_in_queue=self._perception.audio_in,
                    audio_out_queue=self._perception.audio_out,
                    gateway=self._gateway,
                    on_interrupt=self._on_interrupt,
                    on_tool_call=self._on_tool_call,
                    tool_router=self._tool_router,
                    soul_manifest=active_soul,
                )

        # Context Injection
        pending = self._hive.get_pending_handover_for_target(soul_name)
        if pending and not session._injected_handover_context:
            session.inject_handover_context(pending, visual_frames=list(self._perception.frame_buffer))
        
        self._state_manager.set_session(session)

        try:
            if not session.is_ready():
                await asyncio.wait_for(session.connect(), timeout=15.0)
            
            await self._state_manager.transition_to(SessionState.CONNECTED, f"Pulse: {soul_name}")
            await self._gateway.broadcast("engine_state", {"state": "LISTENING"})
            
            self._session_manager._session = session
            async with asyncio.TaskGroup() as tg:
                tg.create_task(session.run(), name="session-stream")
                tg.create_task(self._session_restart_event.wait(), name="restart-watch")

            if self._session_restart_event.is_set():
                await self._state_manager.transition_to(SessionState.HANDING_OFF, "Handoff")
                await session.stop()
                await asyncio.sleep(0.5)
        finally:
            self._state_manager.set_session(None)

    def _on_interrupt(self) -> None:
        logger.info("⚡ Neural Bridge: Barge-in detected.")
        # Drain audio out
        while not self._perception.audio_out.empty():
            try: self._perception.audio_out.get_nowait()
            except asyncio.QueueEmpty: break

    async def _on_tool_call(self, tool_name, args, result) -> None:
        pass
