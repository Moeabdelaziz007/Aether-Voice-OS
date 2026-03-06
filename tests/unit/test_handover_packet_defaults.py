from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_handover_packet_class():
    module_path = Path(__file__).resolve().parents[2] / "core/ai/handover.py"
    spec = spec_from_file_location("handover_module", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.HandoverPacket


def _packet():
    handover_packet_cls = _load_handover_packet_class()
    return handover_packet_cls(
        timestamp=123.0,
        source_agent_id="source",
        target_agent_id="target",
        task_goal="task",
        conversation_summary="summary",
    )


def test_handover_packet_defaults_are_isolated_between_instances():
    first = _packet()
    second = _packet()

    first.working_memory["key"] = "value"
    first.pending_tool_calls.append("tool")

    assert second.working_memory == {}
    assert second.pending_tool_calls == []
