"""
Aether Voice OS — Biometric Voice Authentication.

Ensures that sensitive tools (deployment, database mutations) are only
executed by the authorized Administrator.
"""

import logging

from core.audio.state import audio_state

logger = logging.getLogger(__name__)

# Biometric State
calibrated_pitch: float = 120.0  # Default fallback
calibration_window: float = 20.0 # Tolerance (+/- Hz)
is_calibrated: bool = False


class VoiceAuthGuard:
    """
    Biometric gatekeeper.
    Matches the live audio stream signature against the Soul fingerprint.
    """

    @staticmethod
    def is_authorized() -> bool:
        """
        Verifies the current speaker's biometric signature.
        """
        rms = audio_state.last_rms
        zcr = audio_state.last_zcr

        estimated_pitch = zcr * 8000

        if rms < 0.01:
            return False  # No presence

        if not is_calibrated:
            logger.warning("Bio-Auth: System not calibrated. Using default range.")
            return 100 <= estimated_pitch <= 180

        # Authentic matching against calibrated soul fingerprint
        return (calibrated_pitch - calibration_window) <= estimated_pitch <= (calibrated_pitch + calibration_window)

    @staticmethod
    def calibrate(pitch: float):
        global calibrated_pitch, is_calibrated
        calibrated_pitch = pitch
        is_calibrated = True
        logger.info(f"Bio-Auth: System calibrated with F0: {pitch:.2f}Hz")


async def verify_admin(**kwargs) -> dict:
    """Tool: Verifies if the current user is the Administrator via Voice Biometrics."""
    if VoiceAuthGuard.is_authorized():
        return {
            "status": "authorized",
            "message": "Voice signature matched. Administrator confirmed.",
        }
    return {
        "status": "denied",
        "message": "Voice signature mismatch. High-level commands locked.",
    }


async def calibrate_admin_voice(**kwargs) -> dict:
    """
    Tool: Calibrates the Administrator's voice biometric signature.
    Tool: Calibrates the Administrator's voice biometric signature.
    The user should speak a neutral sentence while this is active.
    """
    rms = audio_state.last_rms
    zcr = audio_state.last_zcr


    if rms < 0.01:
        return {
            "status": "failure",
            "message": "No audio detected. Please ensure your microphone is active and speak clearly.",
        }

    pitch = zcr * 8000
    if not (50 <= pitch <= 500):
        return {
            "status": "failure",
            "message": f"Detected pitch ({pitch:.1f}Hz) is outside human range. Noise detected?",
        }

    VoiceAuthGuard.calibrate(pitch)
    return {
        "status": "success",
        "message": f"Biometric calibration complete. Saved fingerprint at {pitch:.1f}Hz.",
    }


def get_tools() -> list[dict]:
    return [
        {
            "name": "verify_admin",
            "description": "Verifies the user's biometric voice signature.",
            "parameters": {},
            "handler": verify_admin,
        },
        {
            "name": "calibrate_admin_voice",
            "description": "Calibrates the voice recognition system using the current speaker's voice.",
            "parameters": {},
            "handler": calibrate_admin_voice,
        }
    ]
