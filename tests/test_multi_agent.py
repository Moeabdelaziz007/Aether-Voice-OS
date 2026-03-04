import logging

from core.ai.handover.manager import MultiAgentOrchestrator
from core.ai.agents.specialists.architect import ArchitectAgent
from core.ai.agents.specialists.debugger import DebuggerAgent

logging.basicConfig(level=logging.INFO)


def test_synergy():
    orchestrator = MultiAgentOrchestrator()
    orchestrator.register_agent("Architect", ArchitectAgent())
    orchestrator.register_agent("Debugger", DebuggerAgent())

    result = orchestrator.collaborate(
        "Design and build a new database migration script.", "Architect"
    )
    print(f"\n--- Final Result ---\n{result}\n--------------------")

    assert "Synergy Complete" in result
    assert "Architect generated structural blueprint" in result
    assert "Debugger verified and approved" in result


if __name__ == "__main__":
    test_synergy()
