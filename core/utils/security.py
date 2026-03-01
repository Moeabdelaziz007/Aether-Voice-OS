"""
Aether Voice OS — Security & Cryptography Utilities.

Provides verified Ed25519 signature verification and biometric
hashing helpers.
"""

from __future__ import annotations

import logging

import nacl.exceptions
import nacl.signing

logger = logging.getLogger(__name__)


def verify_signature(public_key_hex: str, signature_hex: str, message: bytes) -> bool:
    """
    Verify an Ed25519 signature using PyNaCl.

    Args:
        public_key_hex: The 32-byte public key in hex format.
        signature_hex: The 64-byte signature in hex format.
        message: The raw bytes that were signed.

    Returns:
        True if the signature is valid, False otherwise.
    """
    try:
        verify_key = nacl.signing.VerifyKey(
            public_key_hex, encoder=nacl.encoding.HexEncoder
        )
        verify_key.verify(message, signature_hex, encoder=nacl.encoding.HexEncoder)
        return True
    except (nacl.exceptions.BadSignatureError, Exception) as exc:
        logger.warning("Signature verification failed: %s", exc)
        return False


def generate_keypair() -> tuple[str, str]:
    """
    Generate a new Ed25519 keypair for a new Soul.

    Returns:
        A tuple of (public_key_hex, private_key_hex).
    """
    signing_key = nacl.signing.SigningKey.generate()
    public_key = signing_key.verify_key
    return (
        public_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8"),
        signing_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8"),
    )
