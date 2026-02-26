import logging
from typing import Any, List

logger = logging.getLogger(__name__)


class HandoverContext:
    """Encapsulates state when agents hand tasks over to each other."""

    def __init__(self, task: str, payload: Any = None):
        self.task = task
        self.payload = payload or {}
        self.history = []

    def add_history(self, action: str):
        self.history.append(action)


class MultiAgentOrchestrator:
    """
    Coordinates interactions between multiple ADK Agents using the HandoverProtocol.
    """

    def __init__(self):
        self.active_agents = {}

    def register_agent(self, name: str, agent: Any):
        self.active_agents[name] = agent
        logger.debug(f"Registered ADK Specialist: {name}")

    def handover(self, from_agent: str, to_agent: str, context: HandoverContext) -> str:
        """Executes a handover between two specialized agents."""
        logger.info(f"🔄 Handover: [{from_agent}] -> [{to_agent}]")
        context.add_history(f"Handed over from {from_agent} to {to_agent}")

        target = self.active_agents.get(to_agent)
        if not target:
            return f"Error: Agent {to_agent} not found."

        return target.process(context)

    def collaborate(self, task: str, primary_agent: str) -> str:
        """
        Takes a complex task and routes it starting from a primary agent.
        """
        logger.info(f"Orchestrating task: '{task}' starting with {primary_agent}.")

        context = HandoverContext(task=task)
        starter = self.active_agents.get(primary_agent)

        if not starter:
            return "Orchestration Failed: Primary agent offline."

        # Pass the orchestrator reference so agents can trigger handovers
        starter.set_orchestrator(self)
        return starter.process(context)
