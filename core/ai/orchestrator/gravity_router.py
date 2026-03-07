"""Gravity Score Routing for Galaxy Orchestration.

Calculates gravity scores for planet routing decisions based on:
- Capability match (35% weight)
- Confidence score (25% weight)
- Latency penalty (15% weight)
- Load penalty (15% weight)
- Continuity bonus (10% weight)

Formula:
    score = 0.35*capability + 0.25*confidence
            - 0.15*latency - 0.15*load + 0.10*continuity
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlanetCandidate:
    """Candidate planet for task routing."""

    planet_id: str
    capabilities: List[str]
    confidence: float
    latency_ms: float
    load: float
    continuity_bonus: float = 0.0


class GravityRouter:
    """Calculates gravity scores for planet routing decisions.

    Scoring Formula:
        score = 0.35*capability_match + 0.25*confidence
                - 0.15*latency - 0.15*load + 0.10*continuity
    """

    CAPABILITY_WEIGHT = 0.35
    CONFIDENCE_WEIGHT = 0.25
    LATENCY_WEIGHT = 0.15
    LOAD_WEIGHT = 0.15
    CONTINUITY_WEIGHT = 0.10

    MAX_LATENCY_MS = 500.0  # Normalization ceiling

    def calculate_gravity_score(
        self,
        candidate: PlanetCandidate,
        required_capabilities: List[str],
    ) -> float:
        """Calculate gravity score for a planet candidate.

        Args:
            candidate: Planet candidate with metrics
            required_capabilities: List of required capabilities

        Returns:
            Gravity score clamped to [0.0, 1.0]
        """
        # Capability match (binary: 0 or 1)
        capability_match = 1.0 if all(
            cap in candidate.capabilities
            for cap in required_capabilities
        ) else 0.0

        # Normalized latency (lower is better, max 500ms)
        normalized_latency = min(
            candidate.latency_ms / self.MAX_LATENCY_MS,
            1.0
        )

        # Load (0-1, lower is better)
        load = min(candidate.load, 1.0)

        # Continuity bonus (0-1)
        continuity = min(candidate.continuity_bonus, 1.0)

        # Calculate weighted score
        score = (
            self.CAPABILITY_WEIGHT * capability_match
            + self.CONFIDENCE_WEIGHT * candidate.confidence
            - self.LATENCY_WEIGHT * normalized_latency
            - self.LOAD_WEIGHT * load
            + self.CONTINUITY_WEIGHT * continuity
        )

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    def select_best_planet(
        self,
        candidates: List[PlanetCandidate],
        required_capabilities: List[str],
    ) -> Tuple[Optional[str], float]:
        """Select best planet based on gravity score.

        Args:
            candidates: List of planet candidates
            required_capabilities: Required capabilities

        Returns:
            Tuple of (planet_id, score) or (None, 0.0) if empty
        """
        if not candidates:
            logger.warning("No planet candidates available for routing")
            return None, 0.0

        scored = []
        for candidate in candidates:
            score = self.calculate_gravity_score(
                candidate,
                required_capabilities,
            )
            scored.append((candidate.planet_id, score))
            logger.debug(
                "Planet %s gravity score: %.3f",
                candidate.planet_id,
                score,
            )

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        best_id, best_score = scored[0]
        logger.info(
            "Selected planet %s with gravity score %.3f",
            best_id,
            best_score,
        )

        return best_id, best_score

    def calculate_all_scores(
        self,
        candidates: List[PlanetCandidate],
        required_capabilities: List[str],
    ) -> List[Tuple[str, float]]:
        """Calculate gravity scores for all candidates.

        Args:
            candidates: List of planet candidates
            required_capabilities: Required capabilities

        Returns:
            List of (planet_id, score) tuples sorted by score descending
        """
        scored = [
            (
                candidate.planet_id,
                self.calculate_gravity_score(candidate, required_capabilities),
            )
            for candidate in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
