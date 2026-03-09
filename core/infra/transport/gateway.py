"""
Aether Voice OS — WebSocket Gateway.

Manages external client connections via WebSocket.
Handles Ed25519 challenge-response authentication,
capability negotiation, and heartbeat ticking.

This is the Single Source of Truth for the AI session.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from typing import TYPE_CHECKING, Any, Optional

from core.ai.agents.registry import AgentRegistry, AgentMetadata
from core.ai.agents.forge import AgentForge

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator
    from core.tools.router import ToolRouter

import websockets
from google.genai import types
from websockets.asyncio.server import Server, ServerConnection

from core.ai.session import GeminiLiveSession
from core.infra.config import AIConfig, GatewayConfig
from core.infra.telemetry import get_tracer

# New Decentralized Services
from core.infra.transport.auth import AuthService
from core.infra.transport.bus import GlobalBus
from core.infra.transport.intent import IntentBroker
from core.infra.transport.messages import (
    AckMessage,
    ChallengeMessage,
    ErrorMessage,
    MessageType,
)
from core.infra.transport.session_manager import SessionManager
from core.infra.transport.session_state import (
    SessionMetadata,
    SessionState,
    SessionStateManager,
)
from core.utils.errors import HandshakeError

logger = logging.getLogger(__name__)

tracer = get_tracer()


class ClientSession:
    """Tracks a connected and authenticated client."""

    def __init__(
        self,
        client_id: str,
        ws: ServerConnection,
        capabilities: list[str],
    ) -> None:
        self.client_id = client_id
        self.session_id = str(uuid.uuid4())
        self.ws = ws
        self.capabilities = capabilities
        self.last_pong: float = time.monotonic()
        self.connected_at: float = time.monotonic()


class AetherGateway:
    """
    WebSocket gateway for Aether Voice OS.

    This is the Single Source of Truth for the AI session.
    It owns the GeminiLiveSession, audio queues, and manages
    the entire interaction lifecycle.
    """

    def __init__(
        self,
        gateway_config: GatewayConfig,
        ai_config: AIConfig,
        audio_config: Any,
        tool_router: ToolRouter,
        hive: HiveCoordinator,
    ) -> None:
        self._gateway_config = gateway_config
        self._ai_config = ai_config
        self._audio_config = audio_config
        self._tool_router = tool_router

        # 1. Specialized Managers
        self._registry = AgentRegistry()
        self._forge = AgentForge(api_key=self._ai_config.api_key)
        self._hive = hive
        self._hive.set_pre_warm_callback(self.pre_warm_soul)
        self._hive.set_inject_dna_callback(self.inject_dna_update)

        # Global State Bus
        self._bus = GlobalBus()

        # Session State Manager (Single Source of Truth)
        self._state_manager = SessionStateManager(
            broadcast_callback=self.broadcast, bus=self._bus
        )

        # Legacy session reference (now managed by state manager)
        self._server: Optional[Server] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._session_restart_event = asyncio.Event()

        # Decentralized Logic Brackets
        self._auth = AuthService(
            registry=self._hive._registry,
            secret_key=os.environ.get("AETHER_JWT_SECRET")
            or os.environ.get("GOOGLE_API_KEY")
            or "",
        )
        self._intent_broker = IntentBroker()

        # Audio queues
        self._audio_in: asyncio.Queue[dict[str, object]] = asyncio.Queue(
            maxsize=self._audio_config.mic_queue_max
        )
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=15)

        # Session Manager handles the Gemini lifecycle internally
        self._session_manager = SessionManager(
            engine_session=None  # Will be set during loop
        )

        # Client management
        self._clients: dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()

        # Speculative Pre-warming Lock
        self._pre_warm_lock = asyncio.Lock()
        self._pre_warmed_session: Optional[GeminiLiveSession] = None

    @property
    def audio_in_queue(self) -> asyncio.Queue[dict[str, object]]:
        """Input audio queue (mic → Gemini)."""
        return self._audio_in

    @property
    def audio_out_queue(self) -> asyncio.Queue[bytes]:
        """Output audio queue (Gemini → speaker)."""
        return self._audio_out

    @property
    def session_state_manager(self) -> SessionStateManager:
        """Access the session state manager."""
        return self._state_manager

    @property
    def session_state(self) -> SessionState:
        """Current session state."""
        return self._state_manager.state

    def get_session(self) -> Optional[GeminiLiveSession]:
        """
        Get the current Gemini Live session instance.

        This is the controlled access point for session.
        Engine should use this instead of direct _session access.
        """
        return self._state_manager.session

    async def send_text(self, text: str) -> bool:
        """
        Send text input to the active Gemini session.

        Args:
            text: Text to send to Gemini

        Returns:
            True if sent successfully, False otherwise
        """
        session = self._state_manager.session
        if not session or not session._session:
            logger.warning("Cannot send text: No active session")
            return False

        try:
            await session._session.send_realtime_input(
                parts=[types.Part.from_text(text)]
            )
            self._state_manager.increment_message_count()
            return True
        except Exception as e:
            logger.error("Failed to send text to session: %s", e)
            return False

    async def send_audio(
        self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"
    ) -> bool:
        """
        Send audio input to the active Gemini session.

        Args:
            audio_data: Raw audio bytes
            mime_type: MIME type of audio data

        Returns:
            True if sent successfully, False otherwise
        """
        session = self._state_manager.session
        if not session or not session._session:
            logger.warning("Cannot send audio: No active session")
            return False

        try:
            await session._session.send_realtime_input(
                audio={"data": audio_data, "mime_type": mime_type}
            )
            return True
        except Exception as e:
            logger.error("Failed to send audio to session: %s", e)
            return False

    async def interrupt(self) -> bool:
        """
        Interrupt the current Gemini session (barge-in).

        Returns:
            True if interrupt signaled successfully
        """
        session = self._state_manager.session
        if not session:
            logger.debug("No session to interrupt")
            return False

        # Trigger interrupt callback
        self._on_interrupt()

        # Drain audio output queue
        dropped = 0
        while not self._audio_out.empty():
            try:
                self._audio_out.get_nowait()
                dropped += 1
            except asyncio.QueueEmpty:
                break

        if dropped:
            logger.info("⚡ Gateway Interrupt: Dropped %d audio chunks", dropped)

        return True

    async def request_restart(self, reason: str = "System Requested") -> None:
        """Triggers a session restart/reconnection."""
        logger.info("🔄 Gateway Restart Requested: %s", reason)
        self._session_restart_event.set()

    async def request_handoff(self, target_soul: str, reason: str = "") -> bool:
        """
        Request a handoff to a different soul/expert using Deep Handover (ADK 2.0).

        Args:
            target_soul: Name of target soul package
            reason: Reason for handoff

        Returns:
            True if handoff initiated successfully
        """
        # Prepare deep handover
        success, context, message = self._hive.prepare_handoff(
            target_name=target_soul, task=reason, enable_negotiation=True
        )

        if success and context:
            # Commitment: Finalize the handover to switch the active soul in Hive
            self._hive.complete_handoff(context.handover_id)

            self._state_manager.increment_handoff_count()
            await self._state_manager.transition_to(
                SessionState.HANDING_OFF,
                f"Deep Handoff to {target_soul}: {reason} (ID: {context.handover_id})",
            )
            # Store the active handover ID in the session state metadata
            self._state_manager.update_metadata(
                {"active_handover_id": context.handover_id}
            )

            # Signal session restart
            self._session_restart_event.set()
            return True

        logger.error("⚡ Deep Handoff failed: %s", message)
        return False

    async def pre_warm_soul(self, soul_name: str) -> None:
        """
        Speculatively initialize a session for the next soul.
        This runs in the background to reduce latency during handoff.
        """
        async with self._pre_warm_lock:
            if self._pre_warmed_session:
                if self._pre_warmed_session._soul.name == soul_name:
                    logger.debug(f"✦ Pre-warm: Soul {soul_name} already pre-warmed.")
                    return
                # Stop the existing one if it's the wrong soul
                await self._pre_warmed_session.stop()
                self._pre_warmed_session = None

            logger.info(f"🚀 Gateway: Speculatively pre-warming Soul '{soul_name}'...")
            try:
                target_soul = self._hive._registry.get(soul_name)
                session = GeminiLiveSession(
                    config=self._ai_config,
                    audio_in_queue=self._audio_in,
                    audio_out_queue=self._audio_out,
                    gateway=self,
                    on_interrupt=self._on_interrupt,
                    on_tool_call=self._on_tool_call,
                    tool_router=self._tool_router,
                    soul_manifest=target_soul,
                )
                await session.connect()
                # We don't call session.run() yet, just connect()
                self._pre_warmed_session = session
                logger.info(f"✦ Pre-warm: Soul {soul_name} is CONNECTED and ready.")
            except Exception as e:
                logger.error(f"✦ Pre-warm failed for {soul_name}: {e}")
                self._pre_warmed_session = None

    async def forge_agent(self, description: str) -> None:
        """
        Triggered via IntentBroker to create a new specialized agent.
        """
        try:
            # 1. Forge the agent identity
            metadata = await self._forge.forge_agent(description)
            
            # 2. Register it in our hippocumpus
            self._registry.register_agent(metadata)
            
            # 3. Broadcast success to UI
            await self.broadcast("AGENT_FORGED", {
                "id": metadata.id,
                "name": metadata.name,
                "description": metadata.description
            })
            
            # 4. Proactively pre-warm this new agent
            await self.pre_warm_soul(metadata.id)
            
        except Exception as e:
            logger.error(f"❌ Gateway: Agent forging failed: {e}")
            await self.broadcast("AGENT_FORGE_FAILED", {"error": str(e)})

    async def inject_dna_update(self, dna: AgentDNA, rationales: List[str]) -> None:
        """
        Push a mid-session behavioral update to the active Gemini Live session.
        This provides zero-latency neural mutation by injecting instructions mid-stream.
        """
        session = self.get_session()
        if session:
            await session.inject_dna_update(dna, rationales)

    async def run(self) -> None:
        """Start the WebSocket server and the main session management loop."""

        # Connect to Global Bus
        await self._bus.connect()

        # Bridge frontend events from GlobalBus to WebSocket clients
        if self._bus:
            asyncio.create_task(
                self._bus.subscribe("frontend_events", self._handle_frontend_event)
            )

        # Initialize State Manager (Subscriptions)
        await self._state_manager.initialize()

        self._running = True
        self._server = await websockets.serve(
            self._handle_connection,
            self._gateway_config.host,
            self._gateway_config.port,
        )
        logger.info(
            "Gateway listening on ws://%s:%d",
            self._gateway_config.host,
            self._gateway_config.port,
        )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._tick_loop())
            tg.create_task(self._session_loop())
            # Server runs until cancelled
            await asyncio.Future()  # Block forever

    async def _session_loop(self) -> None:
        """Manages the Gemini session lifecycle and soul handoffs with state machine."""
        import uuid
        from datetime import datetime

        # Start health monitoring
        await self._state_manager.start_health_monitoring()

        while self._running:
            self._session_restart_event.clear()

            active_soul = self._hive.active_soul
            soul_name = active_soul.manifest.name if active_soul else "UnknownSoul"

            # Initialize session metadata
            session_metadata = SessionMetadata(
                session_id=str(uuid.uuid4()),
                soul_name=soul_name,
                started_at=datetime.now(),
            )

            # Transition to INITIALIZING
            await self._state_manager.transition_to(
                SessionState.INITIALIZING,
                f"Creating session for {soul_name}",
                metadata=session_metadata,
            )

            # Create session through state manager
            async with self._pre_warm_lock:
                if (
                    self._pre_warmed_session
                    and self._pre_warmed_session._soul.name == soul_name
                ):
                    logger.info(
                        "🚀 Using pre-warmed session for %s (Latency reduction: ~800ms)",
                        soul_name,
                    )
                    session = self._pre_warmed_session
                    self._pre_warmed_session = None
                else:
                    if self._pre_warmed_session:
                        await self._pre_warmed_session.stop()
                        self._pre_warmed_session = None

                    session = GeminiLiveSession(
                        config=self._ai_config,
                        audio_in_queue=self._audio_in,
                        audio_out_queue=self._audio_out,
                        gateway=self,
                        on_interrupt=self._on_interrupt,
                        on_tool_call=self._on_tool_call,
                        tool_router=self._tool_router,
                        soul_manifest=active_soul,
                    )

            # Inject pending handover context if available (if not already injected during pre-warming)
            pending_handover = self._hive.get_pending_handover_for_target(soul_name)
            if pending_handover and not session._injected_handover_context:
                logger.info(
                    "A2A [GATEWAY] Injecting Deep Handover context: %s (Task: %s)",
                    pending_handover.handover_id,
                    pending_handover.task[:50],
                )
                session.inject_handover_context(pending_handover)

            self._state_manager.set_session(session)

            try:
                if not session._running:
                    try:
                        # Safety: 10s watchdog for new expert arrival
                        await asyncio.wait_for(session.connect(), timeout=10.0)
                    except (asyncio.TimeoutError, Exception) as e:
                        logger.error(
                            "✦ Critical: Expert '%s' failed to stabilize. Rolling back...",
                            soul_name,
                        )

                        # Recover last handover ID from hive for context restoration
                        # We use the private access here as Gateway and Hive are tightly coupled in the core engine
                        fail_handover_id = getattr(
                            self._hive, "_last_handover_id", None
                        )
                        if fail_handover_id:
                            self._hive.rollback_handover(fail_handover_id)

                        await self._state_manager.transition_to(
                            SessionState.ERROR, f"Expert handshake timeout: {str(e)}"
                        )
                        # Trigger restart which will now pick up the rolled-back 'last_successful_soul'
                        self._session_restart_event.set()
                        continue

                # Transition to CONNECTED
                await self._state_manager.transition_to(
                    SessionState.CONNECTED, f"Session established for {soul_name}"
                )

                await self.broadcast("engine_state", {"state": "LISTENING"})
                logger.info(
                    "✦ Hive Active: Expert '%s' taking control (session: %s)",
                    soul_name,
                    session_metadata.session_id[:8],
                )

                self._session_manager._session = session
                async with asyncio.TaskGroup() as tg:
                    session_task = tg.create_task(
                        self._session_manager.start_session_loop(),
                        name="gemini-session",
                    )
                    restart_waiter = tg.create_task(
                        self._session_restart_event.wait(), name="restart-waiter"
                    )

                    done, pending = await asyncio.wait(
                        [session_task, restart_waiter],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for p in pending:
                        p.cancel()

                if self._session_restart_event.is_set():
                    logger.info("🔄 Hive Handoff: Preparing next expert...")
                    await self._state_manager.transition_to(
                        SessionState.HANDING_OFF, "Soul handoff initiated"
                    )
                    await session.stop()
                    await asyncio.sleep(1.0)  # Graceful cross-fade

                    # Transition to RESTARTING
                    await self._state_manager.transition_to(
                        SessionState.RESTARTING, "Preparing for next soul"
                    )
                else:
                    if not self._shutdown_event.is_set():
                        logger.warning(
                            "Session ended unexpectedly. Restarting in 5s..."
                        )
                        await self._state_manager.transition_to(
                            SessionState.ERROR, "Unexpected session termination"
                        )
                        await asyncio.sleep(5.0)

            except Exception as e:
                logger.error("Session loop error: %s", e, exc_info=True)
                await self._state_manager.transition_to(
                    SessionState.ERROR, f"Exception: {str(e)[:100]}"
                )
                if self._running:
                    await asyncio.sleep(5)  # Backoff before retrying
            finally:
                # Clear session on exit
                self._state_manager.set_session(None)

        # Stop health monitoring on exit
        await self._state_manager.stop_health_monitoring()

    def _on_interrupt(self) -> None:
        """Callback from session on barge-in."""
        # This can be proxied to the playback component
        # For now, just log it. The session itself handles draining its output queue.
        logger.info("⚡ Gateway received interrupt signal.")

    async def _on_tool_call(self, tool_name: str, args: dict, result: dict) -> None:
        """Callback from session for tool analytics."""
        # This could be used for logging or further processing.
        pass

    async def _handle_frontend_event(self, event_data: dict) -> None:
        """Bridge events from the GlobalBus to WebSocket clients."""
        try:
            event_type = event_data.get("type")
            if event_type:
                logger.debug("Bridging frontend event: %s", event_type)
                await self.broadcast(event_type, event_data)
        except Exception as e:
            logger.error("Error bridging frontend event: %s", e)

    async def _handle_connection(self, ws: ServerConnection) -> None:
        """Handle a new WebSocket connection."""
        client_id: Optional[str] = None
        try:
            client_id = await self._handshake(ws)
            logger.info("Client authenticated: %s", client_id)

            async for raw_msg in ws:
                if isinstance(raw_msg, bytes):
                    await self._route_binary(client_id, raw_msg)
                else:
                    try:
                        msg = json.loads(raw_msg)
                        await self._route_message(client_id, msg)
                    except json.JSONDecodeError:
                        await self._send_error(ws, 400, "Invalid JSON")
                    except Exception as exc:
                        logger.error("Message handling error: %s", exc)
                        await self._send_error(ws, 500, str(exc))

        except HandshakeError as exc:
            logger.warning("Handshake failed: %s", exc)
            await self._send_error(ws, 401, str(exc), fatal=True)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected: %s", client_id or "unknown")
        finally:
            if client_id:
                async with self._lock:
                    self._clients.pop(client_id, None)

    async def _handshake(self, ws: ServerConnection) -> str:
        """Challenge-response authentication delegated to AuthService."""
        challenge_bytes = os.urandom(32)
        challenge = ChallengeMessage(challenge=challenge_bytes.hex())
        await ws.send(challenge.model_dump_json())

        try:
            raw = await asyncio.wait_for(
                ws.recv(), timeout=self._gateway_config.handshake_timeout_s
            )
            resp = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError):
            raise HandshakeError("Handshake timed out or malformed")

        client_id = resp.get("client_id")
        token = resp.get("token")
        id_token = resp.get("id_token")
        signature = resp.get("signature")

        if id_token:
            decoded = self._auth.verify_firebase_token(id_token)
            if not decoded:
                raise HandshakeError("Invalid Firebase ID Token")
            # If client_id not provided, use Firebase UID
            if not client_id:
                client_id = decoded.get("uid")
        elif token:
            if not self._auth.verify_jwt(token):
                raise HandshakeError("Invalid JWT")
        elif signature:
            if not self._auth.verify_signature(
                challenge_bytes.hex(), signature, client_id
            ):
                raise HandshakeError("Invalid Signature")
        else:
            raise HandshakeError("No authentication provided")

        session = ClientSession(
            client_id=client_id, ws=ws, capabilities=resp.get("capabilities", [])
        )
        async with self._lock:
            self._clients[client_id] = session

        ack = AckMessage(
            session_id=session.session_id,
            granted_capabilities=session.capabilities,
            tick_interval_s=self._gateway_config.tick_interval_s,
        )
        await ws.send(ack.model_dump_json())
        return client_id

    # Removed: Internal Auth methods replaced by AuthService delegate.

    async def _route_binary(self, client_id: str, data: bytes) -> None:
        """Route incoming binary audio chunks to the session's input queue."""
        try:
            await self._audio_in.put(
                {
                    "data": data,
                    "mime_type": (
                        f"audio/pcm;rate={self._gateway_config.receive_sample_rate}"
                    ),
                }
            )
        except Exception as exc:
            logger.error("Error routing binary audio: %s", exc)

    async def _route_message(self, client_id: str, msg: dict[str, Any]) -> None:
        """Route incoming messages by type."""
        msg_type = msg.get("type", "")

        if msg_type == MessageType.PONG.value:
            async with self._lock:
                if client_id in self._clients:
                    self._clients[client_id].last_pong = time.monotonic()

        elif msg_type == "INTENT":
            # Phase A: Handle V1.1 Intent Schema
            await self._handle_intent(client_id, msg)

        elif msg_type == "UI_STATE_SYNC":
            widgets = msg.get("payload", {}).get("active_widgets", [])
            self._state_manager.update_active_widgets(widgets)

        elif msg_type == MessageType.DISCONNECT.value:
            async with self._lock:
                session = self._clients.pop(client_id, None)
            if session:
                await session.ws.close()

        else:
            logger.debug("Unhandled message type: %s from %s", msg_type, client_id)

    async def _handle_intent(self, client_id: str, msg: dict[str, Any]) -> None:
        """Process structured intent via IntentBroker."""
        await self._intent_broker.handle_intent(client_id, json.dumps(msg), self)

    def _verify_payload_signature(
        self, payload: dict, signature: str, client_id: str
    ) -> bool:
        """Verify payload signature via AuthService."""
        return self._auth.verify_payload_signature(
            json.dumps(payload).encode(), signature, client_id
        )

    async def _tick_loop(self) -> None:
        """Send periodic heartbeats and prune dead clients."""
        while self._running:
            await asyncio.sleep(self._gateway_config.tick_interval_s)

            # Periodic cleanup of completed/failed handovers to prevent memory leaks
            self._hive.cleanup_handovers()

            now = time.monotonic()
            dead_clients: list[str] = []

            async with self._lock:
                for cid, session in self._clients.items():
                    # Check for dead clients
                    elapsed = now - session.last_pong
                    max_silence = (
                        self._gateway_config.tick_interval_s
                        * self._gateway_config.max_missed_ticks
                    )
                    if elapsed > max_silence:
                        dead_clients.append(cid)
                        continue

                    # Send tick
                    try:
                        tick_msg = json.dumps(
                            {
                                "type": MessageType.TICK.value,
                                "timestamp": now,
                            }
                        )
                        await session.ws.send(tick_msg)
                    except websockets.exceptions.ConnectionClosed:
                        dead_clients.append(cid)

                # Prune dead clients (outside iteration)
                for cid in dead_clients:
                    self._clients.pop(cid, None)
                    logger.info("Pruned dead client: %s", cid)

    async def broadcast(self, msg_type: str, payload: dict) -> None:
        """Broadcast a message to all connected clients."""
        data = json.dumps({"type": msg_type, "payload": payload})

        async with self._lock:
            active_sessions = list(self._clients.values())

        if not active_sessions:
            return

        async def _send(session):
            try:
                await session.ws.send(data)
                return None
            except websockets.exceptions.ConnectionClosed:
                return session.client_id
            except Exception as e:
                logger.debug("Broadcast error to %s: %s", session.client_id, e)
                return session.client_id

        try:
            async with asyncio.timeout(2.0):
                results = await asyncio.gather(*[_send(s) for s in active_sessions])
                dead = [r for r in results if r is not None]
                if dead:
                    async with self._lock:
                        for cid in dead:
                            self._clients.pop(cid, None)
        except TimeoutError:
            logger.warning("Gateway broadcast timeout — skipped")
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

    async def broadcast_binary(self, data: bytes) -> None:
        """Broadcast raw binary data to all connected clients."""
        async with self._lock:
            active_sessions = list(self._clients.values())

        if not active_sessions:
            return

        async def _send(session):
            try:
                await session.ws.send(data)
                return None
            except websockets.exceptions.ConnectionClosed:
                return session.client_id
            except Exception:
                return session.client_id

        results = await asyncio.gather(*[_send(s) for s in active_sessions])
        dead = [r for r in results if r is not None]
        if dead:
            async with self._lock:
                for cid in dead:
                    self._clients.pop(cid, None)

    async def _send_error(
        self,
        ws: ServerConnection,
        code: int,
        message: str,
        fatal: bool = False,
    ) -> None:
        """Send an error message to a client."""
        err = ErrorMessage(code=code, message=message, fatal=fatal)
        try:
            await ws.send(err.model_dump_json())
            if fatal:
                await ws.close()
        except websockets.exceptions.ConnectionClosed:
            pass

    async def stop(self) -> None:
        """Shut down the gateway."""
        self._running = False
        self._shutdown_event.set()
        session = self.get_session()
        if session:
            await session.stop()
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Gateway stopped")
