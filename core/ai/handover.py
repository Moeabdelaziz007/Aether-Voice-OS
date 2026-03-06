import logging
import time
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from core.ai.agents.registry import AgentMetadata

logger = logging.getLogger("AetherOS.Handover")

# ==========================================
# 🌌 Agent Handover Context
# The "Electronic Soul" transfer packet.
# ==========================================


class HandoverPacket(BaseModel):
    """
    Carries the state of a conversation between specialists.
    Prevents 'Context Amnesia' during agent switches.
    """

    timestamp: float
    source_agent_id: str
    target_agent_id: str

    # State Payload
    task_goal: str
    conversation_summary: str
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    pending_tool_calls: list = Field(default_factory=list)


# ==========================================
# 🌌 Handover Protocol (ADK 2.0)
# handles the formal transfer of ownership.
# ==========================================


class AgentHandoverManager:
    """
    Coordinates the transition of control from one expert to another.
    """

    def __init__(self):
        self._last_handover: Optional[HandoverPacket] = None

    async def execute_handover(
        self,
        source: AgentMetadata,
        target: AgentMetadata,
        task: str,
        summary: str,
        memory: Dict[str, Any],
    ) -> HandoverPacket:
        """
        Formalizes the transition between two agents.
        """
        packet = HandoverPacket(
            timestamp=time.time(),
            source_agent_id=source.id,
            target_agent_id=target.id,
            task_goal=task,
            conversation_summary=summary,
            working_memory=memory,
        )

        logger.info(
            f"🎯 [Handover] Handing over from {source.name} -> {target.name} "
            f"for task: '{task[:50]}...'"
        )

        self._last_handover = packet
        return packet

    def get_last_packet(self) -> Optional[HandoverPacket]:
        return self._last_handover
