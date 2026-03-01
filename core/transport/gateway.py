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

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator
    from core.tools.router import ToolRouter

import websockets
from google.genai import types
from websockets.asyncio.server import Server, ServerConnection

from core.ai.session import GeminiLiveSession
from core.transport.messages import (
    AckMessage,
    ChallengeMessage,
    ErrorMessage,
    MessageType,
)
from core.transport.bus import GlobalBus
from core.transport.session_state import (
    SessionMetadata,
    SessionState,
    SessionStateManager,
)
from core.utils.config import AIConfig, GatewayConfig
from core.utils.errors import HandshakeError, HandshakeTimeoutError
from core.utils.telemetry import get_tracer

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
        tool_router: ToolRouter,
        hive: HiveCoordinator,
    ) -> None:
        self._gateway_config = gateway_config
        self._ai_config = ai_config
        self._tool_router = tool_router
        self._hive = hive
        self._hive.set_pre_warm_callback(self.pre_warm_soul)

        # Global State Bus
        self._bus = GlobalBus(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
        )

        # Session State Manager (Single Source of Truth)
        self._state_manager = SessionStateManager(
            broadcast_callback=self.broadcast,
            bus=self._bus,
        )

        # Legacy session reference (now managed by state manager)
        self._server: Optional[Server] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._session_restart_event = asyncio.Event()

        # Audio queues are now owned by the gateway
        self._audio_in: asyncio.Queue[dict[str, object]] = asyncio.Queue(
            maxsize=self._ai_config.audio.mic_queue_max
        )
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=15)

        # Client management
        self._clients: dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()

        # Speculative Pre-warming
        self._pre_warmed_session: Optional[GeminiLiveSession] = None
        self._pre_warm_lock = asyncio.Lock()

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
        This runs in the background to hide connection latency.
        """
        async with self._pre_warm_lock:
            if self._pre_warmed_session:
                if self._pre_warmed_session._soul.name == soul_name:
                    logger.debug("Soul %s already pre-warmed", soul_name)
                    return
                # Cancel previous pre-warm if different soul
                await self._pre_warmed_session.stop()
                self._pre_warmed_session = None

            logger.info("⚡ Speculative Pre-warm: Initializing '%s' in background...", soul_name)
            try:
                target_soul = self._hive._registry.get(soul_name)
                session = GeminiLiveSession(
                    config=self._ai_config,
                    audio_in_queue=self._audio_in,
                    audio_out_queue=self._audio_out,
                    on_interrupt=self._on_interrupt,
                    on_tool_call=self._on_tool_call,
                    tool_router=self._tool_router,
                    soul_manifest=target_soul.manifest,
                    gateway=self,
                )

                # Inject handover context if available
                pending = self._hive.get_pending_handover_for_target(soul_name)
                if pending:
                    session.inject_handover_context(pending)

                # Start connection in background
                # Note: We don't await connect() here to non-block the main flow
                asyncio.create_task(session.connect())
                self._pre_warmed_session = session
            except Exception as e:
                logger.error("Failed to pre-warm soul %s: %s", soul_name, e)

    async def run(self) -> None:
        """Start the WebSocket server and the main session management loop."""
        
        # Connect to Global Bus
        await self._bus.connect()

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
            soul_name = active_soul.manifest.name

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
                if self._pre_warmed_session and self._pre_warmed_session._soul.name == soul_name:
                    logger.info("🚀 Using pre-warmed session for %s (Latency reduction: ~800ms)", soul_name)
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
                        on_interrupt=self._on_interrupt,
                        on_tool_call=self._on_tool_call,
                        tool_router=self._tool_router,
                        soul_manifest=active_soul.manifest,
                        gateway=self,
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
                        logger.error("✦ Critical: Expert '%s' failed to stabilize. Rolling back...", soul_name)
                        
                        # Recover last handover ID from hive for context restoration
                        # We use the private access here as Gateway and Hive are tightly coupled in the core engine
                        fail_handover_id = getattr(self._hive, "_last_handover_id", None)
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

                async with asyncio.TaskGroup() as tg:
                    session_task = tg.create_task(session.run(), name="gemini-session")
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
        """
        Challenge-response authentication.
        """
        # Generate challenge
        challenge_bytes = os.urandom(32)
        challenge = ChallengeMessage(challenge=challenge_bytes.hex())

        await ws.send(challenge.model_dump_json())

        # Wait for response with timeout
        try:
            raw = await asyncio.wait_for(
                ws.recv(),
                timeout=self._gateway_config.handshake_timeout_s,
            )
        except asyncio.TimeoutError:
            raise HandshakeTimeoutError(
                f"Client did not respond within "
                f"{self._gateway_config.handshake_timeout_s}s"
            )

        try:
            resp = json.loads(raw)
        except json.JSONDecodeError:
            raise HandshakeError("Invalid handshake response format")

        client_id = resp.get("client_id")
        if not client_id:
            raise HandshakeError("Missing client_id in response")

        signature = resp.get("signature", "")
        capabilities = resp.get("capabilities", [])

        if not self._verify_signature(challenge_bytes, signature, client_id):
            raise HandshakeError(f"Invalid signature from {client_id}")

        # Create session
        session = ClientSession(client_id, ws, capabilities)

        async with self._lock:
            self._clients[client_id] = session

        # Send ACK
        ack = AckMessage(
            session_id=session.session_id,
            granted_capabilities=capabilities,
            tick_interval_s=self._gateway_config.tick_interval_s,
        )
        await ws.send(ack.model_dump_json())

        return client_id

    def _verify_signature(
        self,
        challenge: bytes,
        signature: str,
        client_id: str,
    ) -> bool:
        """
        Verify an Ed25519 signature.

        Attempts to find a public key for the client_id in the registry,
        or falls back to treat client_id as a hex public key.
        """
        from core.utils.security import verify_signature

        # 1. Try to find the Soul in the registry
        try:
            soul = self._hive._registry.get(client_id)
            if soul.manifest.public_key:
                return verify_signature(soul.manifest.public_key, signature, challenge)
        except Exception:
            pass

        # 2. Ephemeral/Direct Mode: If client_id is a 64-char hex string,
        # treat as pubkey
        is_hex = all(c in "0123456789abcdef" for c in client_id.lower())
        if len(client_id) == 64 and is_hex:
            return verify_signature(client_id, signature, challenge)

        # 3. Global Auth Fallback (Development)
        global_key = os.environ.get("AETHER_GLOBAL_PUBLIC_KEY")
        if global_key:
            return verify_signature(global_key, signature, challenge)

        return False

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

        elif msg_type == MessageType.DISCONNECT.value:
            async with self._lock:
                session = self._clients.pop(client_id, None)
            if session:
                await session.ws.close()

        else:
            logger.debug("Unhandled message type: %s from %s", msg_type, client_id)

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
            dead: list[str] = []
            for cid, session in self._clients.items():
                try:
                    await session.ws.send(data)
                except websockets.exceptions.ConnectionClosed:
                    dead.append(cid)
            for cid in dead:
                self._clients.pop(cid, None)

    async def broadcast_binary(self, data: bytes) -> None:
        """Broadcast raw binary data to all connected clients."""
        async with self._lock:
            dead: list[str] = []
            for cid, session in self._clients.items():
                try:
                    await session.ws.send(data)
                except websockets.exceptions.ConnectionClosed:
                    dead.append(cid)
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
        if self._session:
            await self._session.stop()
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Gateway stopped")
