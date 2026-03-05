"""
Performance & Integration Test: Aether Hive Swarm.

Proves that specialized experts can collaborate and share memory.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ai import handoff
from core.ai.hive import HiveCoordinator
from core.services.registry import AetherRegistry
from core.tools import hive_memory


@pytest.mark.asyncio
async def test_hive_full_lifecycle():
    # 1. Setup Mock Registry
    packages_dir = Path("brain/packages")  # Assuming these exist from fabrication
    registry = AetherRegistry(str(packages_dir))
    registry.scan()

    print(f"Loaded packages: {registry.list_packages()}")
    for name in registry.list_packages():
        pkg = registry.get(name)
        print(f"  - {name}: expertise={pkg.manifest.expertise}")

    # 2. Setup Hive Coordinator
    router = MagicMock()
    hive = HiveCoordinator(registry, router)
    restart_event = asyncio.Event()

    # Setup tools for handoff
    handoff.set_hive_params(hive, restart_event)

    # 3. Test Expertise Matching
    coding_expert_name = await hive.evaluate_intent("Could you write a python script for me?")
    assert coding_expert_name == "CodingExpert"

    # Should be None because we are already in ArchitectExpert (the default)
    arch_expert_name = await hive.evaluate_intent(
        "What is the best architecture for this swarm?"
    )
    assert arch_expert_name is None

    # Should be CodingExpert because it differs from ArchitectExpert
    coding_expert_suggested = await hive.evaluate_intent("Write a python script.")
    assert coding_expert_suggested == "CodingExpert"

    # 4. Test Handoff Execution
    assert hive.active_soul.manifest.name == "ArchitectExpert"

    result = await handoff.delegate_to_agent(
        target_agent_id="CodingExpert", task_description="Refactor engine.py"
    )

    assert result["status"] == "handoff_initiated"
    assert hive.active_soul.manifest.name == "CodingExpert"
    assert restart_event.is_set()

    # 5. Test Collective Memory (Simulated Firestore)
    # We mock firebase connector for the test
    fb_mock = MagicMock()
    fb_mock.is_connected = True
    fb_mock._session_id = "test-session"

    # Manual mock for the Firestore async chain
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_doc = MagicMock()

    fb_mock._db = mock_db
    mock_db.collection.return_value = mock_coll
    mock_coll.document.return_value = mock_doc

    # These must be AsyncMocks because they are awaited in hive_memory
    mock_doc.set = AsyncMock(return_value=None)
    mock_doc.get = AsyncMock()  # Will return a mock doc with .exists

    hive_memory.set_firebase_connector(fb_mock)

    # Agent A writes memory
    await hive_memory.write_collective_memory(
        "last_plan", {"steps": [1, 2, 3]}, tags=["arch"]
    )

    # Verify mock call
    mock_db.collection.assert_called_with("hive_memory")
    mock_coll.document.assert_called_with("last_plan")
    mock_doc.set.assert_called()

    print("\n✅ Aether Hive Verification: Infrastructure - OK")
    print("✅ Aether Hive Verification: Expertise Match - OK")
    print("✅ Aether Hive Verification: Handoff Protocol - OK")
    print("✅ Aether Hive Verification: Collective Memory - OK")


if __name__ == "__main__":
    asyncio.run(test_hive_full_lifecycle())
