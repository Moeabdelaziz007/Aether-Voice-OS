import logging
from typing import Any, Dict

from core.ai.agents.registry import AgentRegistry
from core.infra.config import GeminiModel

logger = logging.getLogger("AetherOS.ModelRouter")


class AgentModelRouter:
    """
    The 'Neural Bus' that ensures tasks are dispatched to the correct Gemini foundation.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    async def get_model_for_agent(self, agent_id: str) -> GeminiModel:
        """
        Retrieves the foundation model for a specific agent.
        Defaults to FLASH if not found.
        """
        agent = self.registry.get_agent(agent_id)
        if not agent:
            logger.warning(
                f"[ModelRouter] Agent {agent_id} not found. Defaulting to FLASH."
            )
            return GeminiModel.FLASH

        logger.info(
            f"[ModelRouter] Agent {agent_id} mapped to {agent.foundation_model}"
        )
        return agent.foundation_model

    def get_dispatch_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Generates model-specific configuration (e.g., temperature, top_p) based on the model tier.
        """
        agent = self.registry.get_agent(agent_id)
        model = agent.foundation_model if agent else GeminiModel.FLASH

        # Dynamic config based on model tier
        if model == GeminiModel.PRO:
            return {"temperature": 0.2, "top_p": 0.95, "max_output_tokens": 8192}
        elif model in [GeminiModel.LIVE_FLASH, GeminiModel.FLASH]:
            return {"temperature": 0.7, "top_p": 0.9, "max_output_tokens": 4096}
        elif model == GeminiModel.ROBOTICS:
            return {
                "temperature": 0.1,
                "top_p": 0.9,
                "response_mime_type": "application/json",
            }

        return {"temperature": 0.5}
