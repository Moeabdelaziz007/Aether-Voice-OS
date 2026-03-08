import logging
from typing import Any, Dict, Optional

import jwt

from firebase_admin import auth as firebase_auth
from core.services.registry import AetherRegistry
from core.utils.security import verify_signature

logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles all cryptographic verification and JWT decoding for AetherOS Gateway.
    Fulfills V3.1 Security Standards.
    """

    def __init__(self, registry: AetherRegistry, secret_key: str):
        self._registry = registry
        self._secret_key = secret_key

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JSON Web Token."""
        try:
            return jwt.decode(token, self._secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.warning("AuthService: JWT token expired.")
        except jwt.InvalidTokenError:
            logger.warning("AuthService: Invalid JWT token.")
        except Exception as e:
            logger.error(f"AuthService: JWT verification error: {e}")
        return None

    def verify_firebase_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify a Firebase ID Token using the Admin SDK."""
        try:
            # Re-use the existing firebase-admin app
            decoded_token = firebase_auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.warning(f"AuthService: Firebase token verification failed: {e}")
            return None

    def verify_signature(self, challenge: str, signature: str, client_id: str) -> bool:
        """
        Verify a cryptographic signature for a challenge (Ed25519).
        Requires client public key from registry.
        """
        try:
            # 1. Try to find the package in the registry for its public key
            if hasattr(self._registry, "get_package_by_client_id"):
                pkg = self._registry.get_package_by_client_id(client_id)
                if pkg and pkg.manifest.public_key:
                    return verify_signature(pkg.manifest.public_key, signature, bytes.fromhex(challenge))

            # 2. Ephemeral/Direct Mode Fallback (match Gateway logic)
            is_hex = all(c in "0123456789abcdef" for c in client_id.lower())
            if len(client_id) == 64 and is_hex:
                return verify_signature(client_id, signature, bytes.fromhex(challenge))

            return False
        except Exception as e:
            logger.error(f"AuthService: Signature verification error: {e}")
            return False

    def verify_payload_signature(
        self, payload: bytes, signature: str, client_id: str
    ) -> bool:
        """Verify the signature of a raw binary payload."""
        # Implementation extracted from gateway.py legacy code
        return self.verify_signature(
            payload.decode("utf-8", errors="ignore"), signature, client_id
        )
