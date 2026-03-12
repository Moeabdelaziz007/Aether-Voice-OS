"""Aether Voice OS — Legacy Handover Protocol Entry Point."""
from core.ai.handover.models import *
from core.ai.handover.negotiation import *
from core.ai.handover.serialization import *


# Maintain legacy get_handover_protocol helper if needed
def get_handover_protocol():
    from core.ai.handover.migration import HandoverMigration
    return HandoverMigration()
