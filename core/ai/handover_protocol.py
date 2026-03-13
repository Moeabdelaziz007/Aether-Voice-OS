"""Aether Voice OS — Legacy Handover Protocol Entry Point."""
from core.ai.handover.models import *
from core.ai.handover.negotiation import *
from core.ai.handover.serialization import *


# Maintain legacy helpers
def get_handover_protocol():
    from core.ai.handover.migration import HandoverMigration
    return HandoverMigration()

def ContextSerializer():
    from core.ai.handover.serialization import ContextSerializer
    return ContextSerializer
