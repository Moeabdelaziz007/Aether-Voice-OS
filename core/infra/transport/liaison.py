"""
Connection Liaison — Component of the Aether Neural Spine.

Manages protocol-level aspects: WebSockets, authentication, and 
the low-level client registry.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import msgpack
import websockets
from websockets.asyncio.server import Server, ServerConnection

from core.infra.transport.auth import AuthService
from core.infra.transport.messages import (
    AckMessage,
    ChallengeMessage,
    ErrorMessage,
)
from core.utils.errors import HandshakeError

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator
    from core.infra.config import GatewayConfig

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
        self.use_msgpack = "msgpack" in capabilities


class ConnectionLiaison:
    """
    Handles WebSocket lifecycle, handshake, and message routing.
    """

    def __init__(
        self,
        config: GatewayConfig,
        hive: HiveCoordinator,
        message_router: Any,
        binary_router: Any,
    ) -> None:
        self._config = config
        self._hive = hive
        self._message_router = message_router
        self._binary_router = binary_router
        self._clients: Dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()
        self._auth = AuthService(
            registry=self._hive._registry,
            secret_key=os.environ.get("AETHER_JWT_SECRET"),
        )
        self._server: Optional[Server] = None
        self._running = False

    @property
    def clients(self) -> Dict[str, ClientSession]:
        return self._clients

    async def start(self, handler) -> None:
        self._running = True
        self._server = await websockets.serve(
            handler,
            self._config.host,
            self._config.port,
            process_request=self._health_check_handler
        )
        logger.info("Liaison listening on ws://%s:%d", self._config.host, self._config.port)

    async def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _health_check_handler(self, path, request_headers):
        headers = request_headers.headers if hasattr(request_headers, "headers") else request_headers
        if path == "/health":
            return (200, [("Content-Type", "text/plain")], b"OK\n")

        origin = headers.get("Origin")
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:1420",
            "tauri://localhost"
        ]
        if origin and origin not in allowed_origins:
            logger.warning("Rejecting connection from unauthorized origin: %s", origin)
            return (403, [("Content-Type", "text/plain")], b"Forbidden: Invalid Origin\n")
        return None

    async def handle_connection(self, ws: ServerConnection) -> None:
        client_id: Optional[str] = None
        try:
            client_id, use_msgpack = await self._handshake(ws)
            logger.info("Client connected: %s (Msgpack: %s)", client_id, use_msgpack)
            
            async for raw_msg in ws:
                if isinstance(raw_msg, bytes):
                    if use_msgpack:
                        try:
                            msg = msgpack.unpackb(raw_msg)
                            if isinstance(msg, dict) and "type" in msg:
                                await self._message_router(client_id, msg)
                                continue
                        except Exception as e:
                            logger.error("Msgpack unpack failed: %s", e)
                    await self._binary_router(client_id, raw_msg)
                else:
                    try:
                        msg = json.loads(raw_msg)
                        await self._message_router(client_id, msg)
                    except json.JSONDecodeError:
                        await self._send_error(ws, 400, "Invalid JSON")
                    except Exception as exc:
                        logger.error("Message handling error: %s", exc, exc_info=True)
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

    async def _handshake(self, ws: ServerConnection) -> Tuple[str, bool]:
        challenge_bytes = os.urandom(32)
        challenge = ChallengeMessage(challenge=challenge_bytes.hex())
        await ws.send(challenge.model_dump_json())

        try:
            raw = await asyncio.wait_for(
                ws.recv(), timeout=self._config.handshake_timeout_s
            )
            resp = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError):
            raise HandshakeError("Handshake timed out or malformed")

        client_id = resp.get("client_id")
        token = resp.get("token")
        id_token = resp.get("id_token")
        signature = resp.get("signature")
        capabilities = resp.get("capabilities", [])
        use_msgpack = "msgpack" in capabilities

        if id_token:
            decoded = self._auth.verify_firebase_token(id_token)
            if not decoded:
                raise HandshakeError("Invalid Firebase ID Token")
            if not client_id:
                client_id = decoded.get("uid")
        elif token:
            if not self._auth.verify_jwt(token):
                raise HandshakeError("Invalid JWT")
        elif signature:
            if not self._auth.verify_signature(challenge_bytes.hex(), signature, client_id):
                raise HandshakeError("Invalid Signature")
        else:
            raise HandshakeError("No authentication provided")

        session = ClientSession(client_id=client_id, ws=ws, capabilities=capabilities)
        async with self._lock:
            self._clients[client_id] = session

        ack = AckMessage(
            session_id=session.session_id,
            granted_capabilities=session.capabilities,
            tick_interval_s=self._config.tick_interval_s,
        )
        await ws.send(ack.model_dump_json())
        return client_id, use_msgpack

    async def broadcast(self, msg_type: str, payload: dict) -> None:
        msg_dict = {"type": msg_type, "payload": payload}
        json_data = json.dumps(msg_dict)
        msgpack_data = msgpack.packb(msg_dict)

        async with self._lock:
            active_sessions = list(self._clients.values())

        if not active_sessions:
            return

        async def _send(session: ClientSession):
            try:
                if session.use_msgpack:
                    await session.ws.send(msgpack_data)
                else:
                    await session.ws.send(json_data)
            except Exception:
                return session.client_id
            return None

        results = await asyncio.gather(*[_send(s) for s in active_sessions])
        dead = [r for r in results if r is not None]
        if dead:
            async with self._lock:
                for cid in dead:
                    self._clients.pop(cid, None)

    async def broadcast_binary(self, data: bytes) -> None:
        async with self._lock:
            active_sessions = list(self._clients.values())

        async def _send(session: ClientSession):
            try:
                await session.ws.send(data)
            except Exception:
                return session.client_id
            return None

        results = await asyncio.gather(*[_send(s) for s in active_sessions])
        dead = [r for r in results if r is not None]
        if dead:
            async with self._lock:
                for cid in dead:
                    self._clients.pop(cid, None)

    async def _send_error(self, ws: Optional[ServerConnection], code: int, message: str, fatal: bool = False) -> None:
        if not ws:
            return
        err = ErrorMessage(code=code, message=message if code < 500 else "Internal Error", fatal=fatal)
        try:
            await ws.send(err.model_dump_json())
            if fatal:
                await ws.close()
        except Exception:
            pass
