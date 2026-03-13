"""Canonical deep handover protocol model surface."""

from core.ai.handover.models import (
    ArchitectOutput,
    DebuggerOutput,
    HandoverContext,
    HandoverStatus,
    IntentConfidence,
    ValidationCheckpoint,
)
from core.ai.handover.negotiation import HandoverNegotiation
from core.ai.handover.serialization import ContextSerializer


def get_handover_protocol():
    from core.ai.handover.migration import HandoverMigration
    return HandoverMigration()


__all__ = [
    "ArchitectOutput",
    "ContextSerializer",
    "DebuggerOutput",
    "HandoverContext",
    "HandoverNegotiation",
    "HandoverStatus",
    "IntentConfidence",
    "ValidationCheckpoint",
    "get_handover_protocol",
]
