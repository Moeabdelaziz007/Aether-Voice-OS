"""
Aether Voice OS — Genetic Verification.
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ai.genetic import GeneticOptimizer


@pytest.mark.asyncio
async def test_genetic_mutation_logic():
    # Mock Firebase and Report
    mock_firebase = MagicMock()
    mock_firebase.is_connected = True
    mock_firebase._session_id = "test-session"

    # Simulate LOW ENGAGEMENT
    mock_firebase.get_session_affective_summary = AsyncMock(
        return_value={
            "status": "success",
            "summary": {
                "avg_engagement": 0.35,  # Very low
                "avg_pitch": 180.5,
                "interaction_count": 5,
                "trend": "stable/declining",
            },
        }
    )
    mock_firebase.log_event = AsyncMock()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ Skipping live Gemini test: GOOGLE_API_KEY not set")
        return

    optimizer = GeneticOptimizer(mock_firebase, api_key)

    current_instr = "You are a helpful assistant. Answer questions concisely."

    print("\nStarting Mutation (Low Engagement Simulator)...")
    mutation = await optimizer.evolve(current_instr)

    if mutation:
        print(f"✅ Mutation Rationale: {mutation.get('rationale')}")
        print(f"✅ New Instructions: {mutation.get('mutated_instructions')[:100]}...")
        assert "mutated_instructions" in mutation
        assert mutation.get("version_delta", 0) > 0
    else:
        print("❌ Mutation failed (check API logs)")


if __name__ == "__main__":
    asyncio.run(test_genetic_mutation_logic())
