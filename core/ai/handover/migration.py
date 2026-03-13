"""Symbol migration map for handoff/handover APIs."""

SYMBOL_MIGRATION_MAP = {
    "core.ai.handoff.set_hive_params": "core.ai.handover.protocol.HandoffProtocol.configure",
    "core.ai.handoff.delegate_to_agent": "core.ai.handover.protocol.HandoffProtocol.delegate_to_agent",
    "core.ai.handoff.get_tools": "core.ai.handover.protocol.HandoffProtocol.get_tools",
    "core.ai.handover.HandoverPacket": "core.ai.handover.dtos.HandoverPacket",
    "core.ai.handover.AgentHandoverManager": "core.ai.handover.manager.AgentHandoverManager",
    "core.ai.handover_protocol.*": "core.ai.handover.protocol_models.*",
    "core.ai.handover_telemetry.*": "core.ai.handover.telemetry.*",
}

class HandoverMigration:
    """Shim for legacy handover discovery."""
    def __init__(self):
        from core.ai.handover.protocol import create_handoff_protocol
        self._impl = create_handoff_protocol()
    
    def __getattr__(self, name):
        return getattr(self._impl, name)
