"""
Aether Voice OS — Exception Hierarchy.

Every exception carries structured context for observability.
Catch `AetherError` at the engine level for unified error handling.
"""
from __future__ import annotations

from typing import Any, Optional


class AetherError(Exception):
    """Base exception for all Aether OS errors."""

    def __init__(
        self,
        message: str,
        *,
        cause: Optional[Exception] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.context = context or {}
        self.__cause__ = cause
        super().__init__(message)


# --- Audio Layer ---

class AudioError(AetherError):
    """Errors in the audio capture/playback pipeline."""


class AudioDeviceNotFoundError(AudioError):
    """No suitable audio input/output device detected."""


class AudioOverflowError(AudioError):
    """Mic buffer overflow — chunks are being produced faster than consumed."""


# --- AI Layer ---

class AIError(AetherError):
    """Errors from the Gemini Live API integration."""


class AIConnectionError(AIError):
    """Failed to establish or maintain a Gemini Live session."""


class AISessionExpiredError(AIError):
    """The Live session timed out or was closed by the server."""


# --- Transport Layer ---

class TransportError(AetherError):
    """Errors in the WebSocket gateway."""


class HandshakeError(TransportError):
    """Client failed the Ed25519 challenge-response handshake."""


class HandshakeTimeoutError(HandshakeError):
    """Client did not respond to the challenge within the timeout."""


class CapabilityDeniedError(TransportError):
    """Client requested a capability it is not permitted to use."""


# --- Identity Layer ---

class IdentityError(AetherError):
    """Errors in the .ath package system."""


class PackageCorruptError(IdentityError):
    """SHA256 checksum verification failed for a package file."""


class PackageNotFoundError(IdentityError):
    """Requested package does not exist in the registry."""


class ManifestValidationError(IdentityError):
    """The manifest.json failed Pydantic validation."""
