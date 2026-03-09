import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class VisionPulseAgent:
    """
    Manages proactive visual perception and temporal grounding.
    Maintains a rolling buffer of screenshots and sends pulses to the AI session.
    """

    def __init__(self, max_frames: int = 15, pulse_interval: int = 10):
        self.max_frames = max_frames
        self.pulse_interval = pulse_interval
        self._frame_buffer: list[tuple[float, bytes]] = []
        self.last_pulse_time = 0

    async def capture_pulse(self) -> Optional[bytes]:
        """Captures a screenshot and adds it to the rolling buffer."""
        import base64

        from core.tools.vision_tool import take_screenshot

        res = await take_screenshot()
        if res.get("status") == "success":
            image_b64 = res["data"]
            image_bytes = base64.b64decode(image_b64)

            now = time.time()
            self._frame_buffer.append((now, image_bytes))
            if len(self._frame_buffer) > self.max_frames:
                self._frame_buffer.pop(0)

            return image_bytes
        return None

    def should_pulse(self) -> bool:
        """Determines if a proactive pulse should be sent."""
        return time.time() - self.last_pulse_time >= self.pulse_interval

    def record_pulse(self):
        """Updates the last pulse timestamp."""
        self.last_pulse_time = time.time()
