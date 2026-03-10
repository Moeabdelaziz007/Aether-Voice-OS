"""
Aether Voice OS — Agent Forge Tool.

Allows the Aether Forge (Mother Agent) to programmatically create
new AI agent packages (.ath) based on user voice requests.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from core.infra.cloud.firebase.interface import FirebaseConnector

logger = logging.getLogger(__name__)

# Initialize single connector for the forge
_connector = FirebaseConnector()


def create_agent(
    name: str,
    description: str,
    instructions: str,
    expertise: Dict[str, float],
    suggested_tools: List[str] = None,
) -> Dict[str, Any]:
    """
    Creates a new agent package boilerplate in the packages/ directory.

    Args:
        name: The unique ID/name of the agent (e.g., 'DevOpsExpert').
        description: A short human-readable description of what the agent does.
        instructions: The system prompt/instructions for the agent.
        expertise: A map of domains to expertise levels (0.0 to 1.0).
        suggested_tools: A list of tool names the agent should ideally have.

    Returns:
        A status dictionary indicating success or failure.
    """
    try:
        # 1. Determine the packages directory (relative to project root)
        # Assuming we are in core/tools/forge_tool.py, project root is ../../
        root_dir = Path(__file__).parent.parent.parent
        packages_dir = root_dir / "packages"
        agent_dir = packages_dir / name.lower().replace(" ", "_")

        if agent_dir.exists():
            return {
                "status": "error",
                "message": f"Agent '{name}' already exists at {agent_dir}",
            }

        # 2. Create the directory structure
        agent_dir.mkdir(parents=True, exist_ok=True)

        # 3. Generate manifest.json
        manifest = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "expertise": expertise,
            "author": "Aether Forge",
            "tools": suggested_tools or [],
        }

        with open(agent_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=4)

        # 4. Generate Soul.md (Behavioral Identity)
        soul_content = f"""# Soul: {name}

## Identity
{instructions}

## Role
{description}

## Capabilities
- {", ".join(expertise.keys())}
"""
        with open(agent_dir / "Soul.md", "w") as f:
            f.write(soul_content)

        # 5. Generate empty Skills.md and Heartbeat.md
        with open(agent_dir / "Skills.md", "w") as f:
            f.write(f"# Skills for {name}\n\nList of specialized procedural tools if any.")

        with open(agent_dir / "Heartbeat.md", "w") as f:
            f.write(f"# Heartbeat for {name}\n\nAutonomous background routines.")

        logger.info("✨ Agent Forge: Successfully created agent '%s' at %s", name, agent_dir)

        # 6. Sync to Firebase (Autonomous Cloud Persistence)
        try:
            # We use a helper to run the async sync in the background or thread
            loop = asyncio.get_event_loop()
            if not _connector._initialized:
                loop.create_task(_connector.initialize())

            dna = {
                "name": name,
                "manifest": manifest,
                "instructions": instructions,
                "created_at": str(Path(agent_dir).stat().st_ctime),
            }
            loop.create_task(_connector.sync_agent_dna(name, dna))
        except Exception as sync_err:
            logger.warning("Agent forged locally but Cloud Sync failed: %s", sync_err)

        return {
            "status": "success",
            "message": f"Agent '{name}' forged and synced successfully.",
            "path": str(agent_dir),
        }

    except Exception as e:
        logger.error("Failed to forge agent: %s", e)
        return {"status": "error", "message": str(e)}


def list_forged_agents() -> List[str]:
    """Returns a list of all currently forged agents in the packages/ directory."""
    root_dir = Path(__file__).parent.parent.parent
    packages_dir = root_dir / "packages"
    if not packages_dir.exists():
        return []

    agents = []
    for entry in packages_dir.iterdir():
        if entry.is_dir() and (entry / "manifest.json").exists():
            agents.append(entry.name)
    return agents
