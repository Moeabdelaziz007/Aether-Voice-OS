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


def verify_signature(
    public_key: str | bytes, signature: str | bytes, message: str | bytes
) -> bool:
    """
    Verify an Ed25519 signature using PyNaCl.

    Args:
        public_key: The 32-byte public key (hex string or bytes).
        signature: The 64-byte signature (hex string or bytes).
        message: The raw message bytes or string that was signed.

    Returns:
        True if the signature is valid, False otherwise.
    """
    try:
        # Convert hex inputs to bytes if needed
        import nacl.encoding

        pk_bytes = (
            public_key if isinstance(public_key, bytes) else bytes.fromhex(public_key)
        )
        sig_bytes = (
            signature if isinstance(signature, bytes) else bytes.fromhex(signature)
        )
        msg_bytes = (
            message
            if isinstance(message, bytes)
            else message.encode()
            if isinstance(message, str)
            else message
        )

        # In gateway handshake, challenge is sent as hex string, but signature expects bytes of challenge
        if isinstance(message, str) and len(message) == 64 and all(c in "0123456789abcdefABCDEF" for c in message):
            msg_bytes = bytes.fromhex(message)

        verify_key = nacl.signing.VerifyKey(pk_bytes)
        verify_key.verify(msg_bytes, sig_bytes)
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
