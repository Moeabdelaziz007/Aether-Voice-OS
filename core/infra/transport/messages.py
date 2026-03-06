"""
Aether Voice OS — Gateway Messages.

Pydantic models for all WebSocket gateway message types.
Every message has a "type" discriminator field for routing.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """All known gateway message types."""

    # Handshake
    CONNECT_CHALLENGE = "connect.challenge"
    CONNECT_RESPONSE = "connect.response"
    CONNECT_ACK = "connect.ack"
    # Lifecycle
    TICK = "tick"
    PONG = "pong"
    DISCONNECT = "disconnect"
    # Data
    AUDIO_CHUNK = "audio.chunk"
    TRANSCRIPT = "transcript"
    INTERRUPT = "interrupt"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool_result"
    ENGINE_STATE = "engine_state"
    # UI
    UI_UPDATE = "ui.update"
    VAD_EVENT = "vad.event"
    # Error
    ERROR = "error"


class GatewayMessage(BaseModel):
    """Base message model — all messages must have a type."""

    type: MessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    client_id: Optional[str] = None
    timestamp: Optional[float] = None


class ChallengeMessage(BaseModel):
    """Server → Client: Ed25519 challenge."""

    type: MessageType = MessageType.CONNECT_CHALLENGE
    challenge: str  # hex-encoded random bytes
    version: str = "2.1"
    server_version: str = "2.1"


class ResponseMessage(BaseModel):
    """Client → Server: Signed challenge response."""

    type: MessageType = MessageType.CONNECT_RESPONSE
    client_id: str
    signature: str  # hex-encoded Ed25519 signature
    capabilities: list[str] = Field(default_factory=list)


class AckMessage(BaseModel):
    """Server → Client: Connection accepted."""

    type: MessageType = MessageType.CONNECT_ACK
    session_id: str
    granted_capabilities: list[str]
    tick_interval_s: float
    version: str = "2.1"


class ErrorMessage(BaseModel):
    """Server → Client: Error notification."""

    type: MessageType = MessageType.ERROR
    code: int
    message: str
    fatal: bool = False
