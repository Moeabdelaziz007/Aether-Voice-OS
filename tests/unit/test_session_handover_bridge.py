from __future__ import annotations

from types import SimpleNamespace

from core.ai.session.handover_bridge import export_handover_state, restore_handover_state


def test_restore_and_export_handover_state():
    facade = SimpleNamespace(_injected_handover_context=None, _handover_acknowledgments={})
    state = {"acknowledgments": {"ack-1": "2024-01-01T00:00:00"}}
    assert restore_handover_state(facade, state) is True
    exported = export_handover_state(facade)
    assert exported["acknowledgments"]["ack-1"] == "2024-01-01T00:00:00"
