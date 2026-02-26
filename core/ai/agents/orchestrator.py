import logging
from typing import Any, List

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Coordinates interactions between multiple ADK Agents.
    Responsible for handoffs and synthesizing the final response.
    """

    def __init__(self):
        self.active_agents = []

    def register_agent(self, agent: Any):
        self.active_agents.append(agent)
        logger.debug(f"Registered ADK Agent: {type(agent).__name__}")

    def collaborate(self, task: str, agents: List[Any] = None) -> str:
        """
        Takes a complex task and routes it through specialized agents.
        Returns the synthesized final result.
        """
        target_agents = agents if agents else self.active_agents
        logger.info(f"Orchestrating task: '{task}' across {len(target_agents)} agents.")

        # Simulate ADK handoff logic
        intermediate_state = f"Task '{task}' processed by Orchestrator."
        for agent in target_agents:
            if hasattr(agent, "process"):
                intermediate_state = agent.process(intermediate_state)

        return f"Synthesized Result: {intermediate_state}"
