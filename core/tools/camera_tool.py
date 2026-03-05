"""
Aether Voice OS — Camera Tool.

Captures real-time frames from the user's camera for Spatio-Temporal Grounding.
This allows Aether to "see" the user's reaction during hard interrupts.
"""

import logging
from typing import Optional

import cv2

logger = logging.getLogger(__name__)


class CameraTool:
    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None

    def capture_frame(self) -> Optional[bytes]:
        """
        Captures a single frame from the default camera.
        Returns JPEG bytes.
        """
        try:
            # We open and close the camera for now to avoid locking it permanently
            # Optimization: Keep it open but in a "stanby" mode if possible
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Could not open camera")
                return None

            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error("Failed to capture frame")
                return None

            # Encode as JPEG
            # Use lower quality (70) to reduce latency/payload size
            _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            return buffer.tobytes()

        except Exception as e:
            logger.error("Camera capture error: %s", e)
            return None


camera_instance = CameraTool)


def get_tools():
    """ADK Tool Registry integration."""
    return [
        {
            "name": "capture_user_frame",
            "description": (
                "Captures a single frame from the user's camera to see their reaction."
            ),
            "parameters": {"type": "object", "properties": {}},
            "handler": camera_instance.capture_frame,
        }
    ]
