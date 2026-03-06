from __future__ import annotations

import asyncio
import json
import logging
import os

import jwt

from core.infra.transport.client_registry import ClientSession
from core.infra.transport.messages import AckMessage, ChallengeMessage
from core.utils.errors import HandshakeError, HandshakeTimeoutError

logger = logging.getLogger(__name__)


async def perform_handshake(gateway, ws) -> str:
    challenge_bytes = os.urandom(32)
    challenge = ChallengeMessage(challenge=challenge_bytes.hex())
    await ws.send(challenge.model_dump_json())

    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=gateway._gateway_config.handshake_timeout_s)
    except asyncio.TimeoutError as exc:
        raise HandshakeTimeoutError() from exc

    try:
        resp = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HandshakeError() from exc

    client_id = resp.get("client_id")
    if not client_id:
        raise HandshakeError()

    capabilities = resp.get("capabilities", [])
    token = resp.get("token")
    if token:
        if not verify_jwt(token):
            raise HandshakeError()
    else:
        signature = resp.get("signature", "")
        if not gateway._verify_signature(challenge_bytes, signature, client_id):
            raise HandshakeError()

    session = ClientSession(client_id=client_id, ws=ws, capabilities=capabilities)
    async with gateway._lock:
        gateway._clients[client_id] = session

    ack = AckMessage(
        session_id=session.session_id,
        granted_capabilities=capabilities,
        tick_interval_s=gateway._gateway_config.tick_interval_s,
    )
    await ws.send(ack.model_dump_json())
    return client_id


def verify_jwt(token: str) -> bool:
    secret = os.environ.get("AETHER_JWT_SECRET") or os.environ.get("GOOGLE_API_KEY")
    if not secret:
        logger.warning("No secret available for JWT verification")
        return False
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        return True
    except jwt.PyJWTError as exc:
        logger.warning("JWT verification failed: %s", exc)
        return False
