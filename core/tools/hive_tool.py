"""
Aether Voice OS — Hive Tool.

Provides tools for the agent to voluntarily trigger Hive Handovers
and specialist consultations.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator

logger = logging.getLogger(__name__)

# Global reference populated by the engine
_hive_coordinator: HiveCoordinator | None = None


def set_hive_coordinator(coordinator: HiveCoordinator):
    global _hive_coordinator
    _hive_coordinator = coordinator


async def switch_expert_soul(target_name: str, reason: str, **kwargs) -> dict:
    """
    Switches the current agent's personality and expertise to another soul.
    Use this when you need specialized knowledge (e.g., Architect, Debugger).
    """
    if not _hive_coordinator:
        return {"status": "error", "message": "Hive Coordinator not initialized."}

    success = _hive_coordinator.request_handoff(target_name, reason)
    if success:
        return {
            "status": "success",
            "message": f"Handoff to {target_name} initiated.",
            "reason": reason,
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to find or switch to soul: {target_name}",
        }


def get_tools() -> list[dict]:
    """Module-level tool registration."""
    return [
        {
            "name": "switch_expert_soul",
            "description": "Switch your current personality/expertise to a specialized soul (e.g. 'ArchitectExpert' or 'DebuggerExpert').",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_name": {
                        "type": "string",
                        "description": "Name of the expert soul to switch to",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Context/Task for the new expert",
                    },
                },
                "required": ["target_name", "reason"],
            },
            "handler": switch_expert_soul,
            "latency_tier": "low_latency",
        }
    ]
