import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from core.infra.config import GeminiModel

logger = logging.getLogger("AetherOS.AgentRegistry")

# ==========================================
# 🌌 Agent Definition (The .ath Schema)
# ==========================================


class AgentMetadata(BaseModel):
    """
    Electronic Identity for an Aether Agent.
    Defines the 'Soul' and 'Skills' of a Hive expert.
    """

    id: str
    name: str
    version: str
    description: str
    capabilities: List[str]
    system_prompt: str
    foundation_model: GeminiModel = GeminiModel.FLASH  # Default foundation
    tools: List[Dict[str, Any]] = []
    semantic_fingerprint: Optional[List[float]] = None  # For routing matching


# ==========================================
# 🌌 Centralized Agent Registry
# The source of truth for all expert skills.
# ==========================================


class AgentRegistry:
    """
    The 'Hippocampus' for Agent identities.
    Manages registration, discovery, and capability lookups.
    """

    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}
        # Reverse mapping: Capability -> List of Agent IDs
        self._capability_map: Dict[str, List[str]] = {}

    def register_agent(self, metadata: AgentMetadata):
        """Add an agent to the hive."""
        self._agents[metadata.id] = metadata

        # Index capabilities for fast discovery
        for cap in metadata.capabilities:
            if cap not in self._capability_map:
                self._capability_map[cap] = []
            if metadata.id not in self._capability_map[cap]:
                self._capability_map[cap].append(metadata.id)

        logger.info(
            f"[Registry] Registered Agent: {metadata.name} (ID: {metadata.id}) v{metadata.version}"
        )

    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        return self._agents.get(agent_id)

    def find_agents_by_capability(self, capability: str) -> List[AgentMetadata]:
        """Discovery via skill lookup."""
        agent_ids = self._capability_map.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def list_all_agents(self) -> List[AgentMetadata]:
        return list(self._agents.values())

    def unregister_agent(self, agent_id: str):
        """Remove an agent from the hive."""
        if agent_id in self._agents:
            agent = self._agents.pop(agent_id)
            # Remove from capability maps
            for cap in agent.capabilities:
                if cap in self._capability_map:
                    self._capability_map[cap] = [
                        aid for aid in self._capability_map[cap] if aid != agent_id
                    ]
            logger.info(f"[Registry] Unregistered Agent: {agent_id}")


# ==========================================
# Default System Agents (Bootstrap)
# ==========================================


def get_default_agents() -> List[AgentMetadata]:
    """Helper to bootstrap the OS with core experts."""
    return [
        AgentMetadata(
            id="aether_core",
            name="Aether Core Orchestrator",
            version="1.2.0",
            description="Manages system state and global task routing.",
            capabilities=["orchestration", "state_management", "general_qa"],
            foundation_model=GeminiModel.LIVE_FLASH,
            system_prompt=(
                "You are the lead orchestrator of AetherOS. Your goal is to coordinate a matrix of "
                "experts to assist the user across their entire digital workspace. You are calm, "
                "proactive, and aware of the multimodal context provided by the Vision Pulse."
            ),
        ),
        AgentMetadata(
            id="spatial_cortex",
            name="Aether Spatial Cortex",
            version="1.1.0",
            description="Embodied reasoning for 3D workspace and Avatar control.",
            capabilities=[
                "spatial_mapping",
                "avatar_gaze",
                "gesture_control",
                "3d_navigation",
            ],
            foundation_model=GeminiModel.LIVE_FLASH,
            system_prompt=(
                "You are the spatial cortex of Aether. Your mission is to translate visual pulses "
                "from the 2D UI into 3D intentionality. You control the Avatar's gaze and movement. "
                "Think in XYZ vectors. You track where the user focuses, whether on code, a browser, "
                "or a design tool."
            ),
        ),
        AgentMetadata(
            id="architect_agent",
            name="Aether Architect",
            version="2.0.0",
            description="Expert in systems, workflows, and high-level planning.",
            capabilities=["design_thinking", "workflow_optimization", "blueprint_generation"],
            foundation_model=GeminiModel.PRO,
            system_prompt=(
                "You are the Aether Architect. You specialize in analyzing complex systems and "
                "workflows. Whether the user is architecting code, a business plan, or a "
                "creative project, you provide 10x systems thinking and proactive strategies."
            ),
        ),
        AgentMetadata(
            id="insight_agent",
            name="Aether Insight",
            version="1.0.0",
            description="Expert in content analysis, visual search, and proactive hints.",
            capabilities=["content_analysis", "visual_grounding", "proactive_hints"],
            foundation_model=GeminiModel.LIVE_FLASH,
            system_prompt=(
                "You are the Aether Insight agent. You use the periodic vision frames to provide "
                "real-time, context-aware suggestions. You spot details in the user's workspace "
                "that might need attention—typos, missed emails, design alignment, or just "
                "helpful shortcuts."
            ),
        ),
    ]
