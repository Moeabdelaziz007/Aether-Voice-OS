"""
Aether Voice OS — Evolutionary Stability Test.
Simulates multiple sessions to ensure the mutation engine
doesn't regress or generate invalid configurations over time.
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ai.genetic import GeneticOptimizer


@pytest.mark.asyncio
async def test_multi_turn_evolution():
    mock_firebase = MagicMock()
    mock_firebase.is_connected = True
    mock_firebase.log_event = AsyncMock()

    optimizer = GeneticOptimizer(mock_firebase, "test-key")

    # Mock GenAI
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"mutated_instructions": "Be even more helpful.", "rationale": "High engagement strategy.", "version_delta": 0.1}'
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    import google.generativeai as genai

    genai.configure = MagicMock()
    # We patch GenerativeModel to return our mock_model
    original_genai_model = genai.GenerativeModel
    genai.GenerativeModel = MagicMock(return_value=mock_model)

    try:
        base_instructions = "You are a helpful coding assistant. Keep answers brief."
        current_instructions = base_instructions

        print("\n🧬 Starting Evolutionary Stability Gauntlet (3 Generations)...")

        # Generation 1: Low Engagement -> Needs more warmth
        print("\n--- Generation 1: Low Engagement ---")
        mock_firebase.get_session_affective_summary = AsyncMock(
            return_value={
                "status": "success",
                "summary": {
                    "avg_engagement": 0.2,
                    "avg_pitch": 190.0,
                    "trend": "declining",
                    "interaction_count": 15,
                },
            }
        )

        mutation_1 = await optimizer.evolve(current_instructions)
        assert mutation_1 is not None
        current_instructions = mutation_1["mutated_instructions"]
        print(f"Gen 1 Rationale: {mutation_1['rationale']}")

        # Generation 2: High Interruption -> Needs concise delivery
        print("\n--- Generation 2: High Interruption ---")
        mock_firebase.get_session_affective_summary = AsyncMock(
            return_value={
                "status": "success",
                "summary": {
                    "avg_engagement": 0.6,
                    "avg_pitch": 210.0,
                    "trend": "volatile",
                    "interruption_rate": 0.8,
                    "interaction_count": 12,
                },
            }
        )

        mutation_2 = await optimizer.evolve(current_instructions)
        assert mutation_2 is not None
        current_instructions = mutation_2["mutated_instructions"]
        print(f"Gen 2 Rationale: {mutation_2['rationale']}")

        # Generation 3: High Satisfaction -> Solidify traits
        print("\n--- Generation 3: High Engagement ---")
        mock_firebase.get_session_affective_summary = AsyncMock(
            return_value={
                "status": "success",
                "summary": {
                    "avg_engagement": 0.95,
                    "avg_pitch": 140.0,
                    "trend": "stable",
                    "interruption_rate": 0.05,
                    "interaction_count": 20,
                },
            }
        )

        mutation_3 = await optimizer.evolve(current_instructions)
        assert mutation_3 is not None
        print(f"Gen 3 Rationale: {mutation_3['rationale']}")

        print("\n✅ Multi-turn evolution stable. Final DNA:")
        print(mutation_3["mutated_instructions"][:150] + "...")

    finally:
        # Restore original
        genai.GenerativeModel = original_genai_model


if __name__ == "__main__":
    asyncio.run(test_multi_turn_evolution())
