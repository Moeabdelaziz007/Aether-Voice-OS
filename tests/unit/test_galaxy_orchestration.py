"""
Unit tests for Galaxy Orchestration components.

Tests cover:
- Gravity Router scoring and planet selection
- Fallback Strategy circuit breakers and retry management
- Galaxy Policy Enforcer validation
"""

import pytest
from core.ai.orchestrator.gravity_router import (
    GravityRouter,
    PlanetCandidate,
)
from core.ai.orchestrator.fallback_strategy import (
    FallbackStrategy,
    FailureCategory,
)
from core.ai.orchestrator.galaxy_policy import (
    GalaxyPolicyEnforcer,
    GalaxyPolicy,
)


class TestGravityRouter:
    """Test gravity score calculation and planet selection."""

    def test_calculate_gravity_score_perfect_match(self):
        """Test scoring with perfect capability match."""
        router = GravityRouter()
        candidate = PlanetCandidate(
            planet_id="test-planet",
            capabilities=["note.create", "semantic.search"],
            confidence=0.95,
            latency_ms=50.0,
            load=0.2,
            continuity_bonus=0.8,
        )

        score = router.calculate_gravity_score(
            candidate,
            required_capabilities=["note.create"],
        )

        # High score expected: perfect match + high confidence
        # Formula: 0.35*1.0 + 0.25*0.95 - 0.15*(50/500) - 0.15*0.2 + 0.10*0.8
        # = 0.35 + 0.2375 - 0.015 - 0.03 + 0.08 = 0.6225
        assert score > 0.6
        assert 0.0 <= score <= 1.0

    def test_calculate_gravity_score_no_capability_match(self):
        """Test scoring when capabilities don't match."""
        router = GravityRouter()
        candidate = PlanetCandidate(
            planet_id="test-planet",
            capabilities=["code.write"],
            confidence=0.95,
            latency_ms=50.0,
            load=0.2,
            continuity_bonus=0.8,
        )

        score = router.calculate_gravity_score(
            candidate,
            required_capabilities=["note.create"],
        )

        # Lower score due to capability mismatch (missing 0.35 weight)
        assert score < 0.65
        assert 0.0 <= score <= 1.0

    def test_calculate_gravity_score_high_latency_penalty(self):
        """Test that high latency reduces score."""
        router = GravityRouter()
        
        low_latency = PlanetCandidate(
            planet_id="fast-planet",
            capabilities=["note.create"],
            confidence=0.9,
            latency_ms=50.0,
            load=0.2,
            continuity_bonus=0.5,
        )
        
        high_latency = PlanetCandidate(
            planet_id="slow-planet",
            capabilities=["note.create"],
            confidence=0.9,
            latency_ms=450.0,  # Near max threshold
            load=0.2,
            continuity_bonus=0.5,
        )

        score_low = router.calculate_gravity_score(
            low_latency,
            required_capabilities=["note.create"],
        )
        score_high = router.calculate_gravity_score(
            high_latency,
            required_capabilities=["note.create"],
        )

        # Low latency should score higher
        assert score_low > score_high

    def test_calculate_gravity_score_high_load_penalty(self):
        """Test that high load reduces score."""
        router = GravityRouter()
        
        low_load = PlanetCandidate(
            planet_id="idle-planet",
            capabilities=["note.create"],
            confidence=0.9,
            latency_ms=100.0,
            load=0.1,
            continuity_bonus=0.5,
        )
        
        high_load = PlanetCandidate(
            planet_id="busy-planet",
            capabilities=["note.create"],
            confidence=0.9,
            latency_ms=100.0,
            load=0.9,
            continuity_bonus=0.5,
        )

        score_low = router.calculate_gravity_score(
            low_load,
            required_capabilities=["note.create"],
        )
        score_high = router.calculate_gravity_score(
            high_load,
            required_capabilities=["note.create"],
        )

        # Low load should score higher
        assert score_low > score_high

    def test_select_best_planet(self):
        """Test selecting best planet from multiple candidates."""
        router = GravityRouter()
        candidates = [
            PlanetCandidate(
                "planet-a",
                ["cap1"],
                0.9,
                100,
                0.3,
                0.5,
            ),
            PlanetCandidate(
                "planet-b",
                ["cap1", "cap2"],
                0.95,
                50,
                0.2,
                0.8,
            ),
        ]

        best_id, best_score = router.select_best_planet(
            candidates,
            required_capabilities=["cap1"],
        )

        # Planet B should win: better metrics across the board
        assert best_id == "planet-b"
        assert best_score > 0.6

    def test_select_best_planet_empty_candidates(self):
        """Test handling of empty candidate list."""
        router = GravityRouter()
        
        best_id, best_score = router.select_best_planet(
            [],
            required_capabilities=["cap1"],
        )

        assert best_id is None
        assert best_score == 0.0

    def test_score_clamping(self):
        """Test that scores are clamped to [0, 1] range."""
        router = GravityRouter()
        
        # Extreme case: all negative factors
        bad_candidate = PlanetCandidate(
            planet_id="terrible-planet",
            capabilities=[],  # No capabilities
            confidence=0.0,
            latency_ms=500.0,  # Max latency
            load=1.0,  # Max load
            continuity_bonus=0.0,
        )

        score = router.calculate_gravity_score(
            bad_candidate,
            required_capabilities=["required.capability"],
        )

        # Score should be clamped to >= 0.0
        assert score >= 0.0
        assert score <= 1.0


class TestFallbackStrategy:
    """Test fallback strategy and circuit breaker logic."""

    def test_circuit_breaker_opens_after_3_failures(self):
        """Test that circuit opens after 3 consecutive hard failures."""
        strategy = FallbackStrategy()
        
        # Initially circuit should be closed
        assert not strategy.is_circuit_open("test-planet")
        
        # Record 3 failures
        for _ in range(3):
            strategy.record_failure("test-planet", FailureCategory.HARD_FAILURE)
        
        # Circuit should now be open
        assert strategy.is_circuit_open("test-planet")

    def test_circuit_breaker_two_failures_still_closed(self):
        """Test that circuit remains closed with only 2 failures."""
        strategy = FallbackStrategy()
        
        # Record only 2 failures
        for _ in range(2):
            strategy.record_failure("test-planet", FailureCategory.HARD_FAILURE)
        
        # Circuit should still be closed
        assert not strategy.is_circuit_open("test-planet")

    def test_get_fallback_excludes_open_circuits(self):
        """Test that fallback selection excludes planets with open circuits."""
        strategy = FallbackStrategy()
        
        # Open circuit on planet-a
        for _ in range(3):
            strategy.record_failure("planet-a", FailureCategory.HARD_FAILURE)
        
        fallback = strategy.get_fallback_plan(
            failed_planet="planet-a",
            available_planets=["planet-a", "planet-b", "planet-c"],
            required_capabilities=[],
        )

        # Should not select planet-a (circuit open)
        assert fallback != "planet-a"
        # Should select one of the other planets
        assert fallback in ["planet-b", "planet-c"]

    def test_should_retry_within_budget(self):
        """Test retry budget management."""
        strategy = FallbackStrategy(max_retries=2)
        
        # Initially should allow retries
        assert strategy.should_retry("test-planet")
        
        # First retry
        strategy.increment_retry("test-planet")
        assert strategy.should_retry("test-planet")
        
        # Second retry (at limit)
        strategy.increment_retry("test-planet")
        assert not strategy.should_retry("test-planet")

    def test_reset_circuit_after_success(self):
        """Test circuit reset after successful operation."""
        strategy = FallbackStrategy()
        
        # Open the circuit
        for _ in range(3):
            strategy.record_failure("test-planet", FailureCategory.HARD_FAILURE)
        assert strategy.is_circuit_open("test-planet")
        
        # Reset after success
        strategy.reset_circuit("test-planet")
        
        # Circuit should be closed
        assert not strategy.is_circuit_open("test-planet")
        # Retry count should be reset
        assert strategy._retry_counts.get("test-planet", 0) == 0

    def test_get_fallback_no_eligible_planets(self):
        """Test fallback when all planets have open circuits."""
        strategy = FallbackStrategy()
        
        # Open circuits on all planets
        for planet in ["planet-a", "planet-b", "planet-c"]:
            for _ in range(3):
                strategy.record_failure(planet, FailureCategory.HARD_FAILURE)
        
        fallback = strategy.get_fallback_plan(
            failed_planet="planet-a",
            available_planets=["planet-a", "planet-b", "planet-c"],
            required_capabilities=[],
        )

        # No eligible fallbacks
        assert fallback is None


class TestGalaxyPolicyEnforcer:
    """Test galaxy policy enforcement."""

    def test_domain_not_allowed(self):
        """Test domain allowlist enforcement."""
        enforcer = GalaxyPolicyEnforcer()
        
        allowed, reason = enforcer.check_domain_allowed(
            "malicious-site.com",
            "Genesis",
        )
        
        assert not allowed
        assert "not allowed" in reason.lower()

    def test_domain_allowed_genesis_default(self):
        """Test default Genesis galaxy domain allowlist."""
        enforcer = GalaxyPolicyEnforcer()
        
        # These should be allowed in Genesis
        allowed_domains = [
            "github.com",
            "docs.python.org",
            "stackoverflow.com",
        ]
        
        for domain in allowed_domains:
            allowed, reason = enforcer.check_domain_allowed(
                domain,
                "Genesis",
            )
            assert allowed, f"Domain {domain} should be allowed: {reason}"

    def test_validate_routing_violations_latency(self):
        """Test routing validation catches high latency."""
        enforcer = GalaxyPolicyEnforcer()
        
        violations = enforcer.validate_routing_decision(
            planet_id="slow-planet",
            galaxy_id="Genesis",
            latency_ms=600.0,  # Exceeds 500ms threshold
            load=0.5,
        )
        
        assert len(violations) >= 1
        assert any("Latency" in v for v in violations)

    def test_validate_routing_violations_load(self):
        """Test routing validation catches high load."""
        enforcer = GalaxyPolicyEnforcer()
        
        violations = enforcer.validate_routing_decision(
            planet_id="overloaded-planet",
            galaxy_id="Genesis",
            latency_ms=100.0,
            load=0.95,  # Exceeds 0.9 threshold
        )
        
        assert len(violations) >= 1
        assert any("Load" in v for v in violations)

    def test_validate_routing_no_violations(self):
        """Test routing validation passes with good metrics."""
        enforcer = GalaxyPolicyEnforcer()
        
        violations = enforcer.validate_routing_decision(
            planet_id="healthy-planet",
            galaxy_id="Genesis",
            latency_ms=150.0,
            load=0.4,
        )
        
        assert len(violations) == 0

    def test_custom_galaxy_policy_creation(self):
        """Test that custom galaxy policies are created on demand."""
        enforcer = GalaxyPolicyEnforcer()
        
        # Get policy for non-existent galaxy
        policy = enforcer.get_policy("CustomGalaxy")
        
        assert policy.galaxy_id == "CustomGalaxy"
        # Should have default values
        assert policy.max_latency_ms == 500.0
        assert policy.max_load_threshold == 0.9

    def test_requires_confirmation_default(self):
        """Test default confirmation requirement."""
        enforcer = GalaxyPolicyEnforcer()
        
        requires_confirm = enforcer.requires_confirmation(
            action_type="sensitive_operation",
            galaxy_id="Genesis",
        )
        
        # Default policy requires confirmation
        assert requires_confirm


class TestIntegration:
    """Integration tests for galaxy orchestration components."""

    def test_gravity_router_with_policy_validation(self):
        """Test gravity scoring respects policy constraints."""
        router = GravityRouter()
        enforcer = GalaxyPolicyEnforcer()
        
        # Create candidates
        candidates = [
            PlanetCandidate(
                "fast-but-loaded-planet",
                ["note.create"],
                0.9,
                100,
                0.95,  # High load
                0.5,
            ),
            PlanetCandidate(
                "balanced-planet",
                ["note.create"],
                0.85,
                150,
                0.4,  # Moderate load
                0.6,
            ),
        ]
        
        # Validate each candidate against policy
        valid_candidates = []
        for candidate in candidates:
            violations = enforcer.validate_routing_decision(
                planet_id=candidate.planet_id,
                galaxy_id="Genesis",
                latency_ms=candidate.latency_ms,
                load=candidate.load,
            )
            
            if not violations:
                valid_candidates.append(candidate)
        
        # Only balanced-planet should pass policy check
        assert len(valid_candidates) == 1
        assert valid_candidates[0].planet_id == "balanced-planet"
        
        # Select best from valid candidates
        best_id, best_score = router.select_best_planet(
            valid_candidates,
            required_capabilities=["note.create"],
        )
        
        assert best_id == "balanced-planet"
        assert best_score > 0.5
