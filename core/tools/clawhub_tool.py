"""
Aether Voice OS — ClawHub Skill Orchestrator.

Provides a bridge to www.clawhub.ai to fetch, install, and
inspect skills for newly forged AI agents.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# [V-STANDARD COMPLIANCE]
# V1: Acquisition (Search/Install)
# V2: Validation (Inspect/Audit)


def search_skills(query: str) -> List[Dict[str, str]]:
    """
    Searches ClawHub.ai for skills matching the query.
    """
    try:
        cmd = ["npx", "-y", "clawhub", "search", query]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse output (assuming it returns names and slugs)
        # For now, let's just return lines as slugs
        lines = result.stdout.strip().split("\n")
        skills = []
        for line in lines:
            if line.strip():
                skills.append({"slug": line.strip(), "name": line.strip()})
        return skills
    except Exception as e:
        logger.error("ClawHub Search failed: %s", e)
        return []


def install_skill(slug: str, agent_name: str) -> Dict[str, Any]:
    """
    Installs a ClawHub skill into a specific agent package.
    """
    try:
        root_dir = Path(__file__).parent.parent.parent
        agent_dir = root_dir / "packages" / agent_name.lower().replace(" ", "_")

        if not agent_dir.exists():
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' does not exist.",
            }

        # Run clawhub install in a temporary directory
        temp_dir = root_dir / "tmp" / f"clawhub_{slug}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["npx", "-y", "clawhub", "install", slug]
        subprocess.run(cmd, cwd=str(temp_dir), check=True)

        # ClawHub skills typically include a SKILL.md.
        # Find all .md files and move them to the agent directory.
        skill_files = list(temp_dir.glob("*.md"))
        for skill_file in skill_files:
            # Append content to the agent's Skills.md or create new ones
            with open(skill_file, "r") as src:
                content = src.read()
                dest_path = agent_dir / f"skill_{slug}.md"
                with open(dest_path, "w") as dest:
                    dest.write(content)

        # Also check for any script directories if present
        # (Implementation details vary based on ClawHub skill structure)

        logger.info(
            "✅ ClawHub: Skill '%s' installed into agent '%s'", slug, agent_name
        )
        return {
            "status": "success",
            "message": f"Skill '{slug}' integrated successfully.",
        }

    except Exception as e:
        logger.error("ClawHub Install failed: %s", e)
        return {"status": "error", "message": str(e)}


def inspect_skill(slug: str) -> str:
    """
    Inspects the details of a ClawHub skill.
    """
    try:
        cmd = ["npx", "-y", "clawhub", "inspect", slug]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        logger.error("ClawHub Inspect failed: %s", e)
        return f"Error: {e}"
