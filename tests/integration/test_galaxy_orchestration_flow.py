"""
Integration tests for Galaxy Orchestration flow.

Tests the complete handover flow with galaxy orchestration:
- Gravity score calculation during handovers
- Fallback reassignment on failures
- Policy enforcement validation
- Cinematic event emission on rollbacks
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.ai.handover.manager import MultiAgentOrchestrator
from core.ai.handover_protocol import HandoverContext, IntentConfidence
from core.ai.orchestrator.fallback_strategy import FailureCategory
from core.ai.orchestrator.gravity_router import PlanetCandidate


@pytest.fixture
def orchestrator():
    """Create a test orchestrator instance."""
    return MultiAgentOrchestrator()


@pytest.fixture
def mock_agents(orchestrator):
    """Register mock agents with the orchestrator."""
    # Create mock agents with capabilities
    architect_agent = MagicMock()
    architect_agent.capabilities = [
        "design.create",
        "blueprint.generate",
        "risk.assess",
    ]
    architect_agent.process = AsyncMock(return_value="Architect completed design")

    debugger_agent = MagicMock()
    debugger_agent.capabilities = [
        "debug.analyze",
        "verify.design",
        "risk.assess",
    ]
    debugger_agent.process = AsyncMock(return_value="Debugger verified design")

    coding_agent = MagicMock()
    coding_agent.capabilities = ["code.write", "code.review", "refactor"]
    coding_agent.process = AsyncMock(return_value="CodingExpert implemented solution")

    # Register agents
    orchestrator.register_agent("Architect", architect_agent)
    orchestrator.register_agent("Debugger", debugger_agent)
    orchestrator.register_agent("CodingExpert", coding_agent)

    return {
        "Architect": architect_agent,
        "Debugger": debugger_agent,
        "CodingExpert": coding_agent,
    }


@pytest.mark.asyncio
async def test_handover_with_gravity_scoring(orchestrator, mock_agents):
    """Test handover calculates gravity score correctly."""
    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Verify architectural blueprint for risks",
        galaxy_id="Genesis",
    )

    # Add intent confidence
    context.intent_confidence = IntentConfidence(
        source_agent="Architect",
        target_agent="Debugger",
        confidence_score=0.95,
        reasoning="Design verification required",
    )

    success, result_context, message = await orchestrator.handover_with_context(
        from_agent="Architect",
        to_agent="Debugger",
        context=context,
    )

    assert success, f"Handover should succeed: {message}"
    assert result_context is not None
    assert result_context.gravity_score is not None
    assert 0.0 <= result_context.gravity_score <= 1.0

    # Debugger should have high score for verification tasks
    assert result_context.gravity_score > 0.6

    # Focus target should be set
    assert result_context.focus_target == "Debugger"


@pytest.mark.asyncio
async def test_handover_policy_violation_latency(orchestrator, mock_agents):
    """Test handover fails on policy violation (high latency)."""
    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Quick verification needed",
        galaxy_id="Genesis",
    )

    # Mock policy enforcer to report latency violation
    with patch.object(
        orchestrator.policy_enforcer,
        "validate_routing_decision",
        return_value=["Latency 650ms exceeds max 500ms"],
    ):
        success, result_context, message = await orchestrator.handover_with_context(
            from_agent="Architect",
            to_agent="Debugger",
            context=context,
        )

        # Should fail due to policy violation
        assert not success
        assert "Policy violations" in message


@pytest.mark.asyncio
async def test_fallback_on_circuit_open(orchestrator, mock_agents):
    """Test fallback reassignment when primary planet circuit is open."""
    # Open circuit on Debugger
    for _ in range(3):
        orchestrator.fallback_strategy.record_failure(
            "Debugger",
            FailureCategory.HARD_FAILURE,
        )

    assert orchestrator.fallback_strategy.is_circuit_open("Debugger")

    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Debug this issue",
        galaxy_id="Genesis",
    )

    # Attempt handover to Debugger (should use fallback or fail gracefully)
    success, result_context, message = await orchestrator.handover_with_context(
        from_agent="Architect",
        to_agent="Debugger",
        context=context,
    )

    # Either succeeded with different planet or failed with clear message
    if success:
        # If succeeded, should have used a different planet
        assert result_context.focus_target != "Debugger"
    else:
        # If failed, should mention circuit or fallback
        assert any(
            keyword in message.lower()
            for keyword in ["circuit", "fallback", "not eligible"]
        )


@pytest.mark.asyncio
async def test_handover_capability_extraction(orchestrator, mock_agents):
    """Test that agent capabilities are correctly extracted."""
    # Test capability extraction
    capabilities = orchestrator._extract_agent_capabilities("Architect")

    assert "design.create" in capabilities
    assert "blueprint.generate" in capabilities
    assert "risk.assess" in capabilities

    # Test required capability extraction from task
    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Design a new architecture blueprint",
    )

    required = orchestrator._extract_required_capabilities(context)

    assert "design.create" in required
    assert "blueprint.generate" in required


@pytest.mark.asyncio
async def test_handover_task_keyword_extraction(orchestrator, mock_agents):
    """Test that task keywords map to correct capabilities."""
    test_cases = [
        ("Debug the memory leak issue", ["debug.analyze", "verify.design"]),
        ("Write code for new feature", ["code.write", "code.review"]),
        ("Search documentation for API", ["semantic.search", "docs.lookup"]),
        ("Create notes about the meeting", ["note.create"]),
        ("Assess risks in the design", ["risk.assess"]),
    ]

    for task, expected_caps in test_cases:
        context = HandoverContext(
            source_agent="Architect",
            target_agent="Debugger",
            task=task,
        )

        required = orchestrator._extract_required_capabilities(context)

        for expected_cap in expected_caps:
            assert expected_cap in required, (
                f"Task '{task}' should extract {expected_cap}"
            )


@pytest.mark.asyncio
async def test_handover_with_working_memory_hints(orchestrator, mock_agents):
    """Test that working memory provides capability hints."""
    context = HandoverContext(
        source_agent="Architect",
        target_agent="CodingExpert",
        task="Implement the solution",
        working_memory={
            "context": "Design architecture approved - now implement",
        },
    )

    required = orchestrator._extract_required_capabilities(context)

    # Should extract from both task and working memory
    assert "code.write" in required
    # Working memory mentions "Design" - should extract design capability
    assert "design.create" in required


@pytest.mark.asyncio
async def test_retry_budget_management(orchestrator, mock_agents):
    """Test retry budget is respected during handovers."""
    planet = "Debugger"

    # Use full retry budget
    for _ in range(2):
        orchestrator.fallback_strategy.increment_retry(planet)

    # Should not allow more retries
    assert not orchestrator.fallback_strategy.should_retry(planet)

    # Record failure to potentially open circuit
    orchestrator.fallback_strategy.record_failure(
        planet,
        FailureCategory.HARD_FAILURE,
    )

    # After 1 failure, circuit should still be closed
    assert not orchestrator.fallback_strategy.is_circuit_open(planet)


@pytest.mark.asyncio
async def test_multi_galaxy_policy_isolation(orchestrator, mock_agents):
    """Test that policies are isolated per galaxy."""
    # Get policies for different galaxies
    genesis_policy = orchestrator.policy_enforcer.get_policy("Genesis")
    custom_policy = orchestrator.policy_enforcer.get_policy("CustomGalaxy")

    # Modify custom galaxy policy
    custom_policy.max_latency_ms = 1000.0  # More lenient
    custom_policy.max_load_threshold = 0.95

    # Genesis should have default values
    assert genesis_policy.max_latency_ms == 500.0
    assert genesis_policy.max_load_threshold == 0.9

    # Custom should have modified values
    assert custom_policy.max_latency_ms == 1000.0
    assert custom_policy.max_load_threshold == 0.95


@pytest.mark.asyncio
async def test_gravity_score_continuity_bonus(orchestrator, mock_agents):
    """Test that recently used planets get continuity bonus."""
    # Create two similar candidates
    candidate_a = PlanetCandidate(
        planet_id="frequent-planet",
        capabilities=["note.create"],
        confidence=0.9,
        latency_ms=100,
        load=0.3,
        continuity_bonus=0.9,  # High continuity (recently used)
    )

    candidate_b = PlanetCandidate(
        planet_id="new-planet",
        capabilities=["note.create"],
        confidence=0.9,
        latency_ms=100,
        load=0.3,
        continuity_bonus=0.1,  # Low continuity (not recently used)
    )

    score_a = orchestrator.gravity_router.calculate_gravity_score(
        candidate_a,
        required_capabilities=["note.create"],
    )

    score_b = orchestrator.gravity_router.calculate_gravity_score(
        candidate_b,
        required_capabilities=["note.create"],
    )

    # Higher continuity should give better score
    assert score_a > score_b


@pytest.mark.asyncio
async def test_handover_preserves_galaxy_context(orchestrator, mock_agents):
    """Test that galaxy context is preserved through handover."""
    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Verify design",
        galaxy_id="Genesis",
        orbit_lane="inner",
    )

    success, result_context, message = await orchestrator.handover_with_context(
        from_agent="Architect",
        to_agent="Debugger",
        context=context,
    )

    assert success
    assert result_context.galaxy_id == "Genesis"
    assert result_context.orbit_lane == "inner"
    assert result_context.gravity_score is not None
    assert result_context.focus_target is not None


@pytest.mark.asyncio
async def test_fallback_selection_logic(orchestrator, mock_agents):
    """Test fallback selection excludes failed and open-circuit planets."""
    strategy = orchestrator.fallback_strategy

    # Open circuit on planet-a
    for _ in range(3):
        strategy.record_failure("planet-a", FailureCategory.HARD_FAILURE)

    # Get fallback for planet-b failure
    fallback = strategy.get_fallback_plan(
        failed_planet="planet-b",
        available_planets=["planet-a", "planet-b", "planet-c"],
        required_capabilities=[],
    )

    # Should not select planet-a (circuit open) or planet-b (failed)
    assert fallback != "planet-a"
    assert fallback != "planet-b"
    assert fallback == "planet-c"


@pytest.mark.asyncio
async def test_complete_handover_flow_with_telemetry(orchestrator, mock_agents):
    """Test complete handover flow with telemetry recording."""
    context = HandoverContext(
        source_agent="Architect",
        target_agent="Debugger",
        task="Complete design verification with detailed analysis",
        galaxy_id="Genesis",
    )

    success, result_context, message = await orchestrator.handover_with_context(
        from_agent="Architect",
        to_agent="Debugger",
        context=context,
    )

    # Verify success
    assert success, f"Handover failed: {message}"
    assert result_context.status.value == "COMPLETED"

    # Verify gravity scoring was applied
    assert result_context.gravity_score is not None
    assert 0.0 <= result_context.gravity_score <= 1.0

    # Verify focus target was set
    assert result_context.focus_target == "Debugger"

    # Verify agent was called
    mock_agents["Debugger"].process.assert_called_once()

    # Verify telemetry was recorded
    stats = orchestrator.get_telemetry_stats()
    assert stats["enabled"] is True
