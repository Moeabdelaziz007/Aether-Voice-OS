"""Canonical handoff protocol implementation with dependency injection."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from core.ai.handover.dtos import HandoffRequest

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator

logger = logging.getLogger(__name__)


class HandoffProtocol:
    """Tool protocol for delegating work to Hive specialists."""

    def __init__(
        self,
        hive: Optional["HiveCoordinator"] = None,
        restart_event: Optional[asyncio.Event] = None,
    ) -> None:
        self._hive = hive
        self._restart_event = restart_event

    def configure(
        self,
        *,
        hive: Optional["HiveCoordinator"] = None,
        restart_event: Optional[asyncio.Event] = None,
    ) -> None:
        """Update dependencies (legacy bridge path only)."""
        if hive is not None:
            self._hive = hive
        if restart_event is not None:
            self._restart_event = restart_event

    async def delegate_to_agent(
        self,
        target_agent_id: str,
        task_description: str,
        priority: str = "medium",
        **_: object,
    ) -> dict:
        """Delegate a task to a specialist agent."""
        _ = HandoffRequest(
            target_agent_id=target_agent_id,
            task_description=task_description,
            priority=priority,
        )

        logger.info("A2A [HANDOFF] Initiating delegation to: %s", target_agent_id)
        logger.info("A2A [HANDOFF] Task: %s", task_description)

        if self._hive and self._restart_event:
            success = self._hive.request_handoff(target_agent_id, task_description)
            if success:
                self._restart_event.set()
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
            return {
                "status": "error",
                "message": f"Target expert '{target_agent_id}' not found in registry.",
            }

        return {
            "status": "handoff_simulated",
            "a2a_code": 202,
            "target": target_agent_id,
            "handoff_id": f"h-idx-{datetime.now().timestamp()}",
            "message": (
                f"Task delegated to '{target_agent_id}' (Simulation). "
                "I'll monitor the completion."
            ),
        }

    def get_tools(self) -> list[dict]:
        """Tool definitions for router registration."""
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
                "handler": self.delegate_to_agent,
                "latency_tier": "batch",
                "idempotent": False,
            }
        ]


def create_handoff_protocol(
    hive: Optional["HiveCoordinator"] = None,
    restart_event: Optional[asyncio.Event] = None,
) -> HandoffProtocol:
    """Factory for DI-friendly handoff protocol instances."""
    return HandoffProtocol(hive=hive, restart_event=restart_event)
