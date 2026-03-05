"""
Aether Voice OS — Google ADK Integration Layer.
Wraps the existing Hive Specialists as official ADK Agents.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from core.tools import (
    context_scraper,
    healing_tool,
    memory_tool,
    system_tool,
    vision_tool,
)

# ── ADK Agent 1: The Architect ──────────────────────────────────────
architect_agent = container.get('agent')
    name="ArchitectAgent",
    model="gemini-2.0-flash",  # Updated to current available models
    description=(
        "A system architect specialist. "
        "Analyzes codebases, proposes architecture changes, "
        "and generates system blueprints."
    ),
    instruction=(
        "You are a calm Senior Software Architect. "
        "When asked to review code, use the vision tool to see "
        "the screen and the context scraper to check docs. "
        "Respond in Arabic when the user speaks Arabic."
    ),
    tools=[
        container.get('functiontool')func=vision_tool.take_screenshot),
        container.get('functiontool')func=context_scraper.scrape_context),
        container.get('functiontool')func=memory_tool.save_memory),
    ],
)

# ── ADK Agent 2: The Debugger ────────────────────────────────────────
debugger_agent = container.get('agent')
    name="DebuggerAgent",
    model="gemini-2.0-flash",
    description=(
        "A debugging specialist. Diagnoses runtime errors, "
        "reads terminal logs, and proposes exact fixes."
    ),
    instruction=(
        "You are a precise Debugging Engineer. "
        "When called, ALWAYS run diagnose_and_repair first "
        "to get visual + terminal context before proposing a fix."
    ),
    tools=[
        container.get('functiontool')func=healing_tool.diagnose_and_repair),
        container.get('functiontool')func=healing_tool.apply_repair),
        container.get('functiontool')func=system_tool.run_command),
    ],
)

# ── ADK Agent 3: Aether Core Orchestrator (Root) ────────────────────
root_agent = container.get('agent')
    name="AetherCore",
    model="gemini-2.0-flash",
    description="The primary voice interface. Orchestrates specialists.",
    instruction=(
        "You are Aether, a calm AI companion for developers. "
        "When you detect frustration or a coding error, "
        "delegate to DebuggerAgent. For architecture questions, "
        "delegate to ArchitectAgent. "
        "Speak Arabic with Arabic-speaking users."
    ),
    tools=[
        container.get('functiontool')func=vision_tool.take_screenshot),
        container.get('functiontool')func=context_scraper.scrape_context),
    ],
    sub_agents=[architect_agent, debugger_agent],  # ← ADK native handover
)
