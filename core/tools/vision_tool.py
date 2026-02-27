"""
Aether Voice OS — Vision Tool.

Provides Gemini with spatial and visual awareness of the user's desktop.
When the user asks "What's on my screen?" or "Can you see what I'm doing?",
this tool triggers a silent macOS screen capture, returning the file path
so the core session can inject it into the multimodal stream.
"""

import base64
import logging

import mss
import mss.tools

logger = logging.getLogger(__name__)


async def take_screenshot(**kwargs) -> dict:
    """
    Captures the current desktop screen.

    Uses 'mss' for ultra-low latency (<70ms) capture directly to memory.
    Returns the Base64 encoded image data to be injected as inline data.
    """
    try:
        with mss.mss() as sct:
            # Capture the primary monitor (index 1)
            # Fallback to index 0 (all monitors) if index 1 is not available
            if len(sct.monitors) > 1:
                monitor = sct.monitors[1]
            else:
                monitor = sct.monitors[0]

            sct_img = sct.grab(monitor)

            # Convert raw pixels to PNG bytes in-memory
            png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)

            # Encode to Base64 for transport
            b64_data = base64.b64encode(png_bytes).decode("utf-8")

            logger.info("Vision Tool: Captured screen in-memory (Base64)")

            return {
                "status": "success",
                "mime_type": "image/png",
                "data": b64_data,
                "message": (
                    "Screen captured instantly. Visual data injected into context."
                ),
            }
    except Exception as e:
        logger.error("Vision Tool: Failed to capture screen: %s", str(e))
        return {"error": f"Failed to capture screen: {str(e)}"}


def get_tools() -> list[dict]:
    """
    Module-level tool registration.
    """
    return [
        {
            "name": "take_screenshot",
            "description": (
                "Takes a live snapshot of the user's entire desktop screen. "
                "Call this when the user asks 'what am I looking at?', "
                "'read my screen', or asks about visual context. The image will "
                "be provided to you instantly."
            ),
            "parameters": {},
            "handler": take_screenshot,
        }
    ]
