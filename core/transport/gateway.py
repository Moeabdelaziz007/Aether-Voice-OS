"""
Aether Voice OS — WebSocket Gateway.

Manages external client connections via WebSocket.
Handles Ed25519 challenge-response authentication,
capability negotiation, and heartbeat ticking.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from typing import Any, Optional

import websockets
from websockets.asyncio.server import Server, ServerConnection

from core.config import GatewayConfig
from core.errors import HandshakeError, HandshakeTimeoutError
from core.transport.messages import (
    AckMessage,
    ChallengeMessage,
    ErrorMessage,
    MessageType,
)

logger = logging.getLogger(__name__)


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

    External consumers (UIs, debug tools, edge clients) connect here
    to receive audio levels, VAD events, and send control commands.
    """

    def __init__(
        self, config: GatewayConfig, on_audio_rx: Optional[callable] = None
    ) -> None:
        self._config = config
        self._on_audio_rx = on_audio_rx
        self._clients: dict[str, ClientSession] = {}
        self._server: Optional[Server] = None
        self._running = False
        self._lock = asyncio.Lock()

    async def run(self) -> None:
        """Start the WebSocket server and run forever."""
        self._running = True
        self._server = await websockets.serve(
            self._handle_connection,
            self._config.host,
            self._config.port,
        )
        logger.info(
            "Gateway listening on ws://%s:%d",
            self._config.host,
            self._config.port,
        )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._tick_loop())
            # Server runs until cancelled
            await asyncio.Future()  # Block forever

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

        1. Server sends random challenge
        2. Client signs with Ed25519 private key
        3. Server verifies signature
        """
        # Generate challenge
        challenge_bytes = os.urandom(32)
        challenge = ChallengeMessage(challenge=challenge_bytes.hex())

        await ws.send(challenge.model_dump_json())

        # Wait for response with timeout
        try:
            raw = await asyncio.wait_for(
                ws.recv(),
                timeout=self._config.handshake_timeout_s,
            )
        except asyncio.TimeoutError:
            raise HandshakeTimeoutError(
                f"Client did not respond within {self._config.handshake_timeout_s}s"
            )

        try:
            resp = json.loads(raw)
        except json.JSONDecodeError:
            raise HandshakeError("Invalid handshake response format")

        client_id = resp.get("client_id")
        if not client_id:
            raise HandshakeError("Missing client_id in response")

        # TODO: Real Ed25519 verification against known public keys
        # For now, accept any client that follows the protocol
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
            tick_interval_s=self._config.tick_interval_s,
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

        Production: look up client's public key and verify.
        Current: accept if the client followed the protocol.
        """
        # TODO: Implement real Ed25519 verification with cryptography lib
        return bool(signature)

    async def _route_binary(self, client_id: str, data: bytes) -> None:
        """Route incoming binary audio chunks."""
        # Simple binary pass-through directly to the engine's audio queue
        if self._on_audio_rx:
            try:
                # To maintain engine compatibility, we wrap the raw PCM bytes
                # in the dict format expected by GeminiLiveSession's input queue.
                # However, we skip JSON decoding overhead here.
                await self._on_audio_rx(
                    {
                        "data": data,
                        "mime_type": f"audio/pcm;rate={self._config.receive_sample_rate}",
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
            await asyncio.sleep(self._config.tick_interval_s)

            now = time.monotonic()
            dead_clients: list[str] = []

            async with self._lock:
                for cid, session in self._clients.items():
                    # Check for dead clients
                    elapsed = now - session.last_pong
                    max_silence = (
                        self._config.tick_interval_s * self._config.max_missed_ticks
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
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Gateway stopped")
