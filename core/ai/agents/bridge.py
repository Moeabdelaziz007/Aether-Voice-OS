import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ADKGeminiBridge:
    """
    Acts as the conduit between Gemini Live Native Audio sessions and the ADK.
    It routes tool_calls to ADK agents and tracks semantic recovery states.
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.was_recovered = False

    def route_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Receives a tool call from Gemini, routes it to the correct ADK agent via orchestrator,
        and returns the result to stream back to Gemini.
        """
        logger.info(f"Bridge routing tool: {tool_name} with args: {arguments}")

        # In a real environment, analyze tool_name to select active agents
        result = self.orchestrator.collaborate(task=f"Execute {tool_name}", agents=None)

        # Track semantic recovery (e.g. if the tool fixed a broken state)
        if "fix" in tool_name.lower() or "recovery" in str(result).lower():
            self.was_recovered = True

        return result

    def reset_recovery_state(self):
        self.was_recovered = False
