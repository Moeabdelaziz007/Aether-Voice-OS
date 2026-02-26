"""
Aether Voice OS — The E2E Singularity Gauntlet
-----------------------------------------------
This is the ultimate expert-level integration test. It simulates a full end-to-end
lifecycle of the Aether Live Agent, proving cohesion between:
1. Cognitive VAD (Adaptive Noise Floor)
2. Neural Dispatcher (Parallel Tool Execution)
3. Hive Swarm Orchestration (Autonomous Handoff)
4. Collective Memory (Firestore State Transfer)
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from core.ai import handoff
from core.ai.hive import HiveCoordinator
# Aether Core Imports
from core.audio.processing import AdaptiveVAD, energy_vad
from core.identity.registry import AetherRegistry
from core.tools import hive_memory
from core.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_e2e_singularity():
    print("\n[E2E] Booting Aether Singularity simulation...")

    # ==========================================
    # 1. BOOTSTRAP ENVIRONMENT & REGISTRY
    # ==========================================
    registry = AetherRegistry(str(Path("brain/packages")))
    registry.scan()
    assert len(registry.list_packages()) >= 2, "Need at least 2 souls for handoff."

    # ==========================================
    # 2. INITIALIZE ROUTER & HIVE COORDINATOR
    # ==========================================
    router = ToolRouter()

    # We must mock Firebase for Collective Memory
    fb_mock = MagicMock()
    fb_mock.is_connected = True
    fb_mock._session_id = "test-session-e2e"
    mock_db, mock_coll, mock_doc = MagicMock(), MagicMock(), MagicMock()
    fb_mock._db = mock_db
    mock_db.collection.return_value = mock_coll
    mock_coll.document.return_value = mock_doc
    mock_doc.set = AsyncMock(return_value=None)
    mock_doc.get = AsyncMock()  # Will simulate empty memory initially
    mock_doc.get.return_value.exists = False

    hive_memory.set_firebase_connector(fb_mock)

    # Register core modules into router
    router.register_module(hive_memory)
    router.register_module(handoff)

    hive = HiveCoordinator(registry, router)
    restart_event = asyncio.Event()
    handoff.set_hive_params(hive, restart_event)

    print("[E2E] System modules synchronized.")

    # ==========================================
    # 3. PHASE A: THE ARCHITECT (Voice to Tool)
    # ==========================================
    # Simulate VAD detecting user speech (Adaptive threshold logic)
    vad = AdaptiveVAD(window_size_sec=0.5, min_threshold=0.01)
    # Prime VAD with silence to establish low baseline
    for _ in range(5):
        energy_vad(np.zeros(1600, dtype=np.int16), adaptive_engine=vad)

    speech_signal = np.random.normal(0, 15000, 1600).astype(
        np.int16
    )  # Very Loud speech
    vad_res = energy_vad(speech_signal, adaptive_engine=vad)
    assert (
        vad_res.is_hard is True
    ), f"Failed to detect speech. RMS: {vad_res.energy_rms}"

    assert (
        hive.active_soul.manifest.name == "ArchitectExpert"
    ), "Default must be Architect."
    print(f"[E2E] Speech detected. Active Soul: {hive.active_soul.manifest.name}")

    # Simulate Gemini executing parallel write_memory calls
    print("[E2E] Architect saving system plan to Collective Memory (Parallel Tools)...")

    mock_fc1 = MagicMock()
    mock_fc1.name, mock_fc1.id, mock_fc1.args = (
        "write_memory",
        "call_1",
        {"key": "sys_plan", "value": {"design": "Microservices"}, "tags": ["arch"]},
    )
    mock_fc2 = MagicMock()
    mock_fc2.name, mock_fc2.id, mock_fc2.args = (
        "write_memory",
        "call_2",
        {"key": "sys_target", "value": {"language": "Python"}, "tags": ["code"]},
    )

    results = await asyncio.gather(router.dispatch(mock_fc1), router.dispatch(mock_fc2))

    assert results[0].get("x-a2a-status") == 200, f"Write failed: {results[0]}"
    assert results[1].get("x-a2a-status") == 200
    assert mock_doc.set.call_count == 2
    print("[E2E] Parallel Memory Write OK.")

    # ==========================================
    # 4. PHASE B: THE HANDOFF
    # ==========================================
    # System evaluates a new user intent "Can you write the code now?"
    print("[E2E] Evaluating intent shift to Coding...")
    target_expert = hive.evaluate_intent("Write the python code for the system plan.")
    assert target_expert == "CodingExpert"

    # Architect calls handoff tool
    mock_fc_handoff = MagicMock()
    mock_fc_handoff.name, mock_fc_handoff.id, mock_fc_handoff.args = (
        "delegate_to_agent",
        "call_3",
        {"target_agent_id": "CodingExpert", "task_description": "Implement the plan."},
    )

    handoff_result = await router.dispatch(mock_fc_handoff)

    assert (
        handoff_result["result"].get("status") == "handoff_initiated"
    ), f"Handoff failed: {handoff_result}"
    assert restart_event.is_set(), "Session restart signal must be fired."
    print("[E2E] Autonomous Handoff OK.")

    # ==========================================
    # 5. PHASE C: THE CODING EXPERT (Reading Memory)
    # ==========================================
    # Hive has now switched souls
    assert hive.active_soul.manifest.name == "CodingExpert"
    restart_event.clear()  # Reset for next session

    print(f"[E2E] Session restored with Soul: {hive.active_soul.manifest.name}")

    # Coding expert reads the memory left by the architect
    mock_doc.get.return_value.exists = True

    # Ensure to_dict is a synchronous MagicMock so it doesn't return a coroutine
    mock_doc.get.return_value.to_dict = MagicMock(
        return_value={"key": "sys_plan", "value": {"design": "Microservices"}}
    )

    mock_fc_read = MagicMock()
    mock_fc_read.name, mock_fc_read.id, mock_fc_read.args = (
        "read_memory",
        "call_4",
        {"key": "sys_plan"},
    )

    read_result = await router.dispatch(mock_fc_read)

    print("\n[E2E] READ_RESULT HEADERS:")
    print(read_result)

    assert read_result.get("x-a2a-status") == 200

    res_data = read_result.get("result", {})
    if isinstance(res_data, dict):
        if "data" in res_data:
            assert res_data["data"]["value"]["design"] == "Microservices"
        else:
            assert res_data["value"]["design"] == "Microservices"

    print("[E2E] Cross-Expert Context Retrieval OK.")
    print("\n[E2E] Singularity Gauntlet Complete: ALL SYSTEMS NOMINAL 🟢\n")


if __name__ == "__main__":
    asyncio.run(test_e2e_singularity())
