import asyncio

import pytest

from core.ai import handoff
from core.ai.handover import (
    AgentHandoverManager,
    HandoffProtocol,
    SYMBOL_MIGRATION_MAP,
    create_handoff_protocol,
)
from core.ai.handover.dtos import HandoverPacket


class _FakeHive:
    def __init__(self, succeed: bool = True):
        self._succeed = succeed
        self.calls = []

    def request_handoff(self, target_agent_id: str, task_description: str) -> bool:
        self.calls.append((target_agent_id, task_description))
        return self._succeed


@pytest.mark.asyncio
async def test_legacy_handoff_wrapper_remains_compatible() -> None:
    hive = _FakeHive()
    restart = asyncio.Event()

    handoff.set_hive_params(hive, restart)
    result = await handoff.delegate_to_agent("CodingExpert", "Write tests")

    assert result["status"] == "handoff_initiated"
    assert restart.is_set()
    assert hive.calls == [("CodingExpert", "Write tests")]


@pytest.mark.asyncio
async def test_canonical_handoff_protocol_injection() -> None:
    hive = _FakeHive()
    restart = asyncio.Event()
    protocol = create_handoff_protocol(hive=hive, restart_event=restart)

    result = await protocol.delegate_to_agent("Debugger", "Verify patch")

    assert result["status"] == "handoff_initiated"
    assert restart.is_set()
    assert hive.calls == [("Debugger", "Verify patch")]


def test_legacy_handover_symbols_forward_to_canonical_package() -> None:
    manager = AgentHandoverManager()
    assert isinstance(manager, AgentHandoverManager)
    assert HandoffProtocol is not None
    assert isinstance(SYMBOL_MIGRATION_MAP, dict)


@pytest.mark.asyncio
async def test_agent_handover_manager_produces_canonical_packet() -> None:
    class Meta:
        def __init__(self, i: str, n: str) -> None:
            self.id = i
            self.name = n

    manager = AgentHandoverManager()
    packet = await manager.execute_handover(
        source=Meta("architect", "Architect"),
        target=Meta("debugger", "Debugger"),
        task="Validate",
        summary="Summary",
        memory={"a": 1},
    )

    assert isinstance(packet, HandoverPacket)
    assert manager.get_last_packet() == packet
