import logging

from core.ai.agents.registry import AgentMetadata
from core.infra.config import GeminiModel

logger = logging.getLogger("AetherOS.AgentForge")


class AgentForge:
    """
    The 'Vulcan' of AetherOS.
    Generates new AgentDNA and Soul manifests from natural language descriptions.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        # In a real implementation, this would use a Gemini 1.5 Pro instance
        # to generate high-quality system prompts and tool schemas.

    async def forge_agent(self, description: str) -> AgentMetadata:
        """
        Takes a raw user request and returns a full AgentMetadata record.
        """
        logger.info(f"🔨 Forging new agent for: {description}")

        # Placeholder for AI generation logic
        # For the demo, we'll generate a consistent schema
        name_hint = description.split()[:2]
        agent_id = f"custom_agent_{hash(description) % 10000}"

        metadata = AgentMetadata(
            id=agent_id,
            name=f"Forge: {' '.join(name_hint)}",
            version="1.0.0",
            description=description,
            capabilities=["task_specific", "custom_tools"],
            system_prompt=f"You are a specialized Aether agent created to: {description}. Be helpful and follow user instructions strictly.",
            foundation_model=GeminiModel.FLASH,
            tools=[],
        )

        return metadata
