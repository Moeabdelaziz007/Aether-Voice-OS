"""Fallback Strategy for Galaxy Orchestration.

Manages fallback planet reassignment when routing fails, including:
- Circuit breaker logic (opens after 3 consecutive failures)
- Retry budget management (max 2 retries per task node)
- Fallback planet selection
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FailureCategory(Enum):
    """Category of failure for circuit breaker logic."""

    TIMEOUT = "timeout"
    HARD_FAILURE = "hard_failure"
    CAPABILITY_MISMATCH = "capability_mismatch"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class FallbackPlan:
    """Fallback plan for failed planet."""

    primary_planet: str
    fallback_planets: List[str]
    failure_reason: str
    retry_budget: int = 2


class FallbackStrategy:
    """Manages fallback planet reassignment when routing fails."""

    def __init__(self, max_retries: int = 2):
        """Initialize fallback strategy.

        Args:
            max_retries: Maximum retry attempts per planet (default: 2)
        """
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}
        self._circuit_breakers: Dict[str, int] = {}

    def record_failure(
        self,
        planet_id: str,
        failure_category: FailureCategory,
    ) -> None:
        """Record a failure for circuit breaker logic.

        Args:
            planet_id: Planet that failed
            failure_category: Category of failure
        """
        if failure_category == FailureCategory.HARD_FAILURE:
            count = self._circuit_breakers.get(planet_id, 0) + 1
            self._circuit_breakers[planet_id] = count

            logger.warning(
                "Circuit breaker for %s: %d consecutive failures",
                planet_id,
                count,
            )

    def is_circuit_open(self, planet_id: str) -> bool:
        """Check if circuit breaker is open.

        Circuit opens after 3 consecutive hard failures.

        Args:
            planet_id: Planet to check

        Returns:
            True if circuit is open (blocked), False otherwise
        """
        return self._circuit_breakers.get(planet_id, 0) >= 3

    def get_fallback_plan(
        self,
        failed_planet: str,
        available_planets: List[str],
        required_capabilities: List[str],
    ) -> Optional[str]:
        """Get fallback planet assignment.

        Args:
            failed_planet: Planet that failed
            available_planets: List of available planets
            required_capabilities: Required capabilities

        Returns:
            Fallback planet ID or None if no eligible fallback
        """
        # Filter out planets with open circuits and the failed planet
        eligible = [
            p
            for p in available_planets
            if not self.is_circuit_open(p) and p != failed_planet
        ]

        if not eligible:
            logger.error("No eligible fallback planets for %s", failed_planet)
            return None

        # Simple strategy: first eligible
        # Can be enhanced with gravity scoring if needed
        fallback = eligible[0]
        logger.info(
            "Selected fallback planet %s for failed planet %s",
            fallback,
            failed_planet,
        )
        return fallback

    def should_retry(self, planet_id: str) -> bool:
        """Check if retry budget is available.

        Args:
            planet_id: Planet to check

        Returns:
            True if retry is allowed, False if budget exhausted
        """
        current_retries = self._retry_counts.get(planet_id, 0)
        return current_retries < self.max_retries

    def increment_retry(self, planet_id: str) -> int:
        """Increment retry count.

        Args:
            planet_id: Planet to increment retry for

        Returns:
            New retry count
        """
        count = self._retry_counts.get(planet_id, 0) + 1
        self._retry_counts[planet_id] = count
        return count

    def reset_circuit(self, planet_id: str) -> None:
        """Reset circuit breaker after success.

        Args:
            planet_id: Planet to reset
        """
        self._circuit_breakers[planet_id] = 0
        self._retry_counts[planet_id] = 0
        logger.debug("Circuit breaker reset for planet %s", planet_id)

    def get_circuit_status(self, planet_id: str) -> Dict[str, int]:
        """Get circuit breaker status for a planet.

        Args:
            planet_id: Planet to query

        Returns:
            Dict with failure_count and is_open status
        """
        failures = self._circuit_breakers.get(planet_id, 0)
        return {
            "failure_count": failures,
            "is_open": failures >= 3,
            "retry_count": self._retry_counts.get(planet_id, 0),
        }

    def clear_all(self) -> None:
        """Clear all circuit breakers and retry counts."""
        self._circuit_breakers.clear()
        self._retry_counts.clear()
        logger.info("All circuit breakers cleared")
