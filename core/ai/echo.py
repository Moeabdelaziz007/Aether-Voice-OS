import random
from typing import Dict, List, Optional


class EchoGenerator:
    """
    Generates anthropomorphic 'thought' echoes based on active tool context.
    Makes the agent feel alive during long processing windows.
    """

    # Context-aware templates
    ECHOS: Dict[str, List[str]] = {
        "generic": [
            "Hmm...",
            "Thinking...",
            "Let me see...",
            "Analyzing that...",
            "Processing...",
        ],
        "discovery": [
            "Scanning the codebase...",
            "Searching for patterns...",
            "Looking through the directory tree...",
            "Hmm, let me check the project structure...",
        ],
        "system": [
            "Checking the system logs...",
            "Let me see what the process list says...",
            "Hmm, analyzing the stack trace...",
        ],
        "code": [
            "Reviewing the logic flow...",
            "Analyzing these functions...",
            "Hmm, checking for potential edge cases here...",
        ],
        "healing": [
            "Thinking of a potential fix...",
            "Evaluating corrective actions...",
            "Hmm, how should we patch this...",
        ],
    }

    # Tool to Category mapping
    TOOL_MAP: Dict[str, str] = {
        "discovery_tool": "discovery",
        "file_search": "discovery",
        "system_tool": "system",
        "read_logs": "system",
        "code_indexer": "code",
        "view_code_item": "code",
        "healing_tool": "healing",
        "propose_fix": "healing",
    }

    def generate(self, tool_name: Optional[str] = None) -> str:
        """Get a random echo phrase based on tool name or generic fallback."""
        category = "generic"
        if tool_name:
            for tool_key, cat in self.TOOL_MAP.items():
                if tool_key in tool_name.lower():
                    category = cat
                    break

        choices = self.ECHOS.get(category, self.ECHOS["generic"])
        return random.choice(choices)

    def generate_filler(self) -> str:
        """Generate a short filler sound (vocalized thinking)."""
        return random.choice(["Mhm...", "Aha...", "Right...", "Uh-huh...", "Wait..."])
