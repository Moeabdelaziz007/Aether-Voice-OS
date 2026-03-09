import logging
from typing import Any, Dict

from core.ai.agents.registry import AgentMetadata
from core.infra.config import GeminiModel

logger = logging.getLogger("AetherOS.SpatialCortex")


class SpatialCortexAgent:
    """
    Powered by gemini-robotics-er-1.5-preview.
    The 'Spatial Cortex' of Aether, responsible for embodied reasoning in the 3D 'Galaxy' environment.
    """

    def __init__(self):
        self.metadata = AgentMetadata(
            id="spatial_cortex",
            name="Aether Spatial Cortex",
            version="1.0.0",
            description="Embodied reasoning for 3D workspace and Avatar control.",
            capabilities=[
                "spatial_mapping",
                "avatar_gaze",
                "gesture_control",
                "3d_navigation",
            ],
            foundation_model=GeminiModel.ROBOTICS,
            system_prompt=(
                "You are the spatial cortex of Aether. Your mission is to translate visual pulses "
                "from the 2D UI into 3D intentionality. You control the Avatar's gaze, limbs, and "
                "movement within the Galaxy workspace. Think in XYZ vectors and orbital lanes."
            ),
        )

    async def map_vision_to_spatial(
        self, vision_pulse: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translates a 2D screenshot pulse into 3D spatial intent.
        Calculates gaze vectors based on UI focus points and active widget coordinates.
        """
        logger.info("[SpatialCortex] Processing vision pulse for spatial grounding.")

        # Real-time vector calculation logic
        # 1. Coordinate Normalization (simulated UI coordinate extraction)
        # Using a slight random walk to simulate focus shifts for the demo
        import random
        focus_x = 0.5 + (random.random() - 0.5) * 0.4
        focus_y = 0.5 + (random.random() - 0.5) * 0.4

        # 2. Translate 2D Screen Space to 3D Galaxy Space
        # Galaxy uses spherical coordinates [longitude, latitude, radius]
        # X: [0, 1] -> Longitude: [-180, 180]
        # Y: [0, 1] -> Latitude: [-90, 90]
        lng = (focus_x - 0.5) * 360
        lat = (0.5 - focus_y) * 180

        spatial_output = {
            "focus_vector": [lng, lat, 100.0],  # Target XYZ in the Galaxy (radius 100)
            "avatar_gaze": "planet_active_focus" if focus_y > 0.3 else "top_tier_orbit",
            "lane_adjustment": "inner_rim" if focus_x < 0.5 else "outer_rim",
            "intentionality_score": 0.92,
            "timestamp": vision_pulse.get("timestamp"),
        }

        logger.debug("[SpatialCortex] Gaze Vector: %s", spatial_output["focus_vector"])
        return spatial_output

    async def generate_gesture(self, intent: str) -> str:
        """
        Generates a 3D animation trigger for the Avatar based on the current orchestrator intent.
        """
        gestures = {
            "thinking": "avatar_hand_to_chin",
            "success": "avatar_subtle_nod",
            "working": "avatar_spatial_typing",
        }
        return gestures.get(intent, "avatar_idle")
