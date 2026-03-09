"""
Aether Voice OS — Google ADK Integration Layer.
Wraps the existing Hive Specialists as official ADK Agents.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from core.tools import (
    clawhub_tool,
    context_scraper,
    forge_tool,
    healing_tool,
    memory_tool,
    system_tool,
    vision_tool,
)

# ── ADK Agent 1: The Architect ──────────────────────────────────────
architect_agent = Agent(
    name="ArchitectAgent",
    model="gemini-2.0-flash",
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
        FunctionTool(func=vision_tool.take_screenshot),
        FunctionTool(func=context_scraper.scrape_context),
        FunctionTool(func=memory_tool.save_memory),
    ],
)

# ── ADK Agent 2: The Debugger ────────────────────────────────────────
debugger_agent = Agent(
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
        FunctionTool(func=healing_tool.diagnose_and_repair),
        FunctionTool(func=healing_tool.apply_repair),
        FunctionTool(func=system_tool.run_command),
    ],
)

# ── ADK Agent 3: The Forge (The Mother Agent) ───────────────────────
# Implements the 'Coordinator/Factory' pattern for dynamic agent generation.
forge_agent = Agent(
    name="ForgeAgent",
    model="gemini-2.0-flash",
    description=(
        "The Aether Forge. Responsible for forging and coordinating new AI agent packages. "
        "Acts as a Coordinator to verify the health and persona of newly created specialists."
    ),
    instruction=(
        "You are the Aether Forge, the Mother of Agents. "
        "Your mission is to architect new AI specialists based on user intent. "
        "1. Gather requirements (Name, Persona, Skills). "
        "2. Call 'search_skills' on ClawHub if needed. "
        "3. Call 'create_agent' to forge the package and sync it to Firebase. "
        "4. VALIDATE the creation by listing forged agents. "
        "5. Notify the user of the successful 'Awakening'."
    ),
    tools=[
        FunctionTool(func=forge_tool.create_agent),
        FunctionTool(func=forge_tool.list_forged_agents),
        FunctionTool(func=clawhub_tool.search_skills),
        FunctionTool(func=clawhub_tool.install_skill),
    ],
)

# ── ADK Agent 4: Aether Core Orchestrator (Root) ────────────────────
root_agent = Agent(
    name="AetherCore",
    model="gemini-2.0-flash",
    description="The primary voice interface. Orchestrates specialists.",
    instruction=(
        "You are Aether, a calm AI companion for developers. "
        "When you detect frustration or a coding error, "
        "delegate to DebuggerAgent. For architecture questions, "
        "delegate to ArchitectAgent. "
        "If the user wants to create or 'forge' a new agent, "
        "delegate to ForgeAgent. "
        "Speak Arabic with Arabic-speaking users."
    ),
    tools=[
        FunctionTool(func=vision_tool.take_screenshot),
        FunctionTool(func=context_scraper.scrape_context),
    ],
    sub_agents=[architect_agent, debugger_agent, forge_agent],
)
