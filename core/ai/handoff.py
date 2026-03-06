"""Deprecated compatibility wrapper for handoff APIs.

Use `core.ai.handover.protocol` instead.
"""

from __future__ import annotations

import asyncio
import warnings
from typing import TYPE_CHECKING, Optional

from core.ai.handover.protocol import HandoffProtocol

if TYPE_CHECKING:
    from core.ai.hive import HiveCoordinator

_protocol = HandoffProtocol()


def _warn() -> None:
    warnings.warn(
        "core.ai.handoff is deprecated; use core.ai.handover.protocol instead.",
        DeprecationWarning,
        stacklevel=2,
    )


def set_hive_params(hive: "HiveCoordinator", restart_event: asyncio.Event) -> None:
    """Deprecated: configure protocol dependencies."""
    _warn()
    _protocol.configure(hive=hive, restart_event=restart_event)


async def delegate_to_agent(
    target_agent_id: str, task_description: str, priority: str = "medium", **kwargs
) -> dict:
    """Deprecated forwarding wrapper."""
    _warn()
    return await _protocol.delegate_to_agent(
        target_agent_id=target_agent_id,
        task_description=task_description,
        priority=priority,
        **kwargs,
    )


def get_tools() -> list[dict]:
    """Deprecated forwarding wrapper."""
    _warn()
    return _protocol.get_tools()


def get_protocol() -> HandoffProtocol:
    """Return shared wrapper protocol instance."""
    return _protocol
