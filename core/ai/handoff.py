"""
Aether Voice OS — A2A Handoff Protocol (ADK V3).

Defines the models and tools for Agent-to-Agent delegation.
This allows Aether to "Handoff" a task to specialized sub-agents
(e.g., a "Travel Agent" or "Code Specialist") when its own
internal tools are insufficient.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import Field

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator

logger = logging.getLogger(__name__)

_hive: Optional[HiveCoordinator] = None
_restart_event: Optional[asyncio.Event] = None


def set_hive_params(hive: HiveCoordinator, restart_event: asyncio.Event) -> None:
    global _hive, _restart_event
    _hive = hive
    _restart_event = restart_event


@dataclass
class HandoffRequest:
    """A2A V3 standard handoff request."""

    target_agent_id: str
    task_description: str
    context_keys: list[str] = Field(default_factory=list)
    priority: str = "medium"
    timeout_seconds: int = 30
    handoff_time: str = Field(default_factory=lambda: datetime.now().isoformat())


async def delegate_to_agent(
    target_agent_id: str, task_description: str, priority: str = "medium", **kwargs
) -> dict:
    """
    Delegate a complex task to a specialized external agent.
    A2A Protocol compliant.

    Args:
        target_agent_id: The ID or alias of the sub-agent (e.g. 'finance_agent').
        task_description: Precise description of what the sub-agent should do.
        priority: Priority of the delegated task.
    """

    logger.info("A2A [HANDOFF] Initiating delegation to: %s", target_agent_id)
    logger.info("A2A [HANDOFF] Task: %s", task_description)

    if _hive and _restart_event:
        success = _hive.request_handoff(target_agent_id, task_description)
        if success:
            _restart_event.set()
            return {
                "status": "handoff_initiated",
                "a2a_code": 202,
                "target": target_agent_id,
                "handoff_id": f"h-idx-{datetime.now().timestamp()}",
                "message": (
                    f"Handoff to Expert '{target_agent_id}' successful. "
                    "Restarting session..."
                ),
            }
        else:
            return {
                "status": "error",
                "message": f"Target expert '{target_agent_id}' not found in registry.",
            }

    return {
        "status": "handoff_simulated",
        "a2a_code": 202,  # Accepted for processing
        "target": target_agent_id,
        "handoff_id": f"h-idx-{datetime.now().timestamp()}",
        "message": (
            f"Task delegated to '{target_agent_id}' (Simulation). "
            "I'll monitor the completion."
        ),
    }


def get_tools() -> list[dict]:
    """Module registration for A2A Handoff tools."""
    return [
        {
            "name": "delegate_to_agent",
            "description": (
                "Delegate a complex task to a specialized agent (A2A Handoff). "
                "Use when a specialist agent is required for a search or task."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target_agent_id": {
                        "type": "string",
                        "description": "The destination agent ID (e.g., 'researcher').",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Markdown formatted description of the task",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["target_agent_id", "task_description"],
            },
            "handler": delegate_to_agent,
            "latency_tier": "batch",
            "idempotent": False,
        }
    ]
