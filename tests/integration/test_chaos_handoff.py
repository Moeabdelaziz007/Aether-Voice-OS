import asyncio
from unittest.mock import MagicMock

import pytest

from core.ai.handover_protocol import HandoverStatus
from core.ai.hive import HiveCoordinator


@pytest.fixture
def mock_registry_chaos():
    registry = MagicMock()

    # Architect (Source)
    architect = MagicMock()
    architect.manifest.name = "ArchitectExpert"

    # Coder (Target - will "disappear")
    coder = MagicMock()
    coder.manifest.name = "CoderExpert"

    registry.get.side_effect = lambda name: (architect if name == "ArchitectExpert" else coder)
    return registry


@pytest.mark.async_hive
@pytest.mark.async_integration
@pytest.mark.asyncio
async def test_hive_chaos_rollback(mock_registry_chaos):
    """
    Chaos Integration Test: Failed Expert Transition.
    Verifies that if a handover is prepared but the target fails or is rejected,
    the Hive Coordinator rolls back the system state to the last known-good Expert.
    """
    router = MagicMock()
    hive = HiveCoordinator(registry=mock_registry_chaos, router=router, enable_deep_handover=True)

    # Initial state: Architect is active
    assert hive.active_soul.manifest.name == "ArchitectExpert"

    # 1. Prepare Handoff to Coder
    success, context, msg = hive.prepare_handoff(target_name="CoderExpert", task="Fix deep handover bug")
    assert success
    hov_id = context.handover_id

    # 2. Simulate "Chaos": The target agent is unreachable or the transition fails midway
    # In this scenario, we trigger a manual rollback via the Hive Coordinator
    # (Typically triggered by AetherGateway's watchdog or heart-beat loss)

    success_rollback = hive.rollback_handover(hov_id)
    assert success_rollback

    # 3. Verification
    # The active soul should still be the Architect (the previous known-good)
    assert hive.active_soul.manifest.name == "ArchitectExpert"

    # The context status should be ROLLED_BACK
    final_context = hive.get_handover_context(hov_id)
    assert final_context.status == HandoverStatus.ROLLED_BACK

    print(f"\n[Chaos Test] Handover {hov_id} successfully rolled back.")
    print(f"[Chaos Test] Active Expert preserved: {hive.active_soul.manifest.name}")


if __name__ == "__main__":
    reg = MagicMock()
    asyncio.run(test_hive_chaos_rollback(reg))
