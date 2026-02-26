"""
Aether Voice OS — Vision Tool.

Provides Gemini with spatial and visual awareness of the user's desktop.
When the user asks "What's on my screen?" or "Can you see what I'm doing?",
this tool triggers a silent macOS screen capture, returning the file path
so the core session can inject it into the multimodal stream.
"""

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


async def take_screenshot(**kwargs) -> dict:
    """
    Captures the current desktop screen.

    Returns a dictionary containing the path to the screenshot,
    which the Aether core engine intercepts to inject visual
    context into the Gemini Live session.
    """
    snapshot_path = f"/tmp/aether_vision_snapshot_{int(time.time())}.jpg"

    try:
        # Fast, silent capture via macOS native screencapture
        subprocess.run(
            ["screencapture", "-x", "-C", "-t", "jpg", snapshot_path],
            check=True,
            capture_output=True,
        )
        logger.info("Vision Tool: Captured screen -> %s", snapshot_path)
    except subprocess.CalledProcessError as e:
        logger.error("Vision Tool: Failed to capture screen: %s", e.stderr.decode())
        return {"error": "Failed to capture the screen locally."}

    # Returning this special dictionary format signals to core.ai.session.py
    # to read the file and send it as a types.Part.from_bytes(...) payload.
    return {
        "status": "success",
        "screenshot_path": snapshot_path,
        "message": "Screenshot captured. The image has been injected into your context stream. Please analyze it.",
    }


def get_tools() -> list[dict]:
    """
    Module-level tool registration.
    """
    return [
        {
            "name": "take_screenshot",
            "description": (
                "Takes a live snapshot of the user's entire desktop screen. "
                "Call this when the user asks 'what am I looking at?', 'read my screen', "
                "or asks about visual context. The image will be provided to you instantly."
            ),
            "parameters": {},
            "handler": take_screenshot,
        }
    ]
