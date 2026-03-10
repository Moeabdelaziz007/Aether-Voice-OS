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


def verify_signature(public_key: str | bytes, signature: str | bytes, message: str | bytes) -> bool:
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

        def safe_fromhex(val):
            val_str = str(val)
            # Remove any non-hex characters (just in case) or validate
            # For testing with "0"*128, this is pure hex
            try:
                return bytes.fromhex(val_str)
            except ValueError:
                # If it's totally invalid hex, fallback to encoding the string (some old tests might just pass random strings)
                return val_str.encode()

        pk_bytes = public_key if isinstance(public_key, bytes) else safe_fromhex(public_key)
        sig_bytes = signature if isinstance(signature, bytes) else safe_fromhex(signature)
        msg_bytes = (
            message if isinstance(message, bytes) else message.encode() if isinstance(message, str) else bytes(message)
        )

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
