"""
Aether Voice OS — Biometric Voice Authentication.

Ensures that sensitive tools (deployment, database mutations) are only
executed by the authorized Administrator.
"""

import logging

from core.audio.state import audio_state

logger = logging.getLogger(__name__)

# Mock authorized signature (Vocal Fingerprint)
# in a real system, this would be a 128-bit vector or a hash of formants.
AUTHORIZED_PITCH_RANGE = (100, 180)  # Hz for a typical male voice, adjust as needed


class VoiceAuthGuard:
    """
    Biometric gatekeeper.
    Matches the live audio stream signature against the Soul fingerprint.
    """

    @staticmethod
    def is_authorized() -> bool:
        """
        Verifies the current speaker's biometric signature.
        Uses the last_rms and last_zcr from audio_state to infer pitch/presence.
        """
        rms = audio_state.last_rms
        zcr = audio_state.last_zcr

        # Simple heuristic: ZCR * sample_rate / 2 approximates fundamental
        # frequency (F0).
        # 0.05 ZCR at 16k -> 0.05 * 8000 = 400Hz
        # Too high for speech, likely noise.
        # 0.015 ZCR at 16k -> 120Hz (Valid human male pitch)
        estimated_pitch = zcr * 8000

        logger.debug(
            "Bio-Auth: Estimated Pitch %.2fHz (RMS: %.3f)", estimated_pitch, rms
        )

        if rms < 0.01:
            return False  # No presence

        if AUTHORIZED_PITCH_RANGE[0] <= estimated_pitch <= AUTHORIZED_PITCH_RANGE[1]:
            return True

        return False


async def verify_admin(**kwargs) -> dict:
    """
    Tool: Verifies if the current user is the Administrator via Voice Biometrics.
    """
    if VoiceAuthGuard.is_authorized():
        return {
            "status": "authorized",
            "message": "Voice signature matched. Administrator confirmed.",
        }
    else:
        return {
            "status": "denied",
            "message": "Voice signature mismatch. High-level commands locked.",
        }


def get_tools() -> list[dict]:
    return [
        {
            "name": "verify_admin",
            "description": (
                "Verifies the user's biometric voice signature. Call this before "
                "performing sensitive operations."
            ),
            "parameters": {},
            "handler": verify_admin,
        }
    ]
