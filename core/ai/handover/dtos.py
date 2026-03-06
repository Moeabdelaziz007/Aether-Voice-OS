"""DTOs for handoff/handover APIs."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class HandoffRequest(BaseModel):
    """A2A V3 handoff request payload."""

    target_agent_id: str
    task_description: str
    context_keys: List[str] = Field(default_factory=list)
    priority: str = "medium"
    timeout_seconds: int = 30
    handoff_time: str = Field(default_factory=lambda: datetime.now().isoformat())


class HandoverPacket(BaseModel):
    """Legacy packet schema kept for compatibility wrappers."""

    timestamp: float = Field(default_factory=time.time)
    source_agent_id: str
    target_agent_id: str
    task_goal: str
    conversation_summary: str
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    pending_tool_calls: List[Any] = Field(default_factory=list)
