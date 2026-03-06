"""Deprecated compatibility wrapper for handover models/managers.

Use `core.ai.handover` package APIs instead.
"""

from __future__ import annotations

import warnings

from core.ai.handover.dtos import HandoverPacket
from core.ai.handover.manager import AgentHandoverManager


def _warn() -> None:
    warnings.warn(
        "core.ai.handover module is deprecated; use core.ai.handover package instead.",
        DeprecationWarning,
        stacklevel=2,
    )


__all__ = ["AgentHandoverManager", "HandoverPacket"]
