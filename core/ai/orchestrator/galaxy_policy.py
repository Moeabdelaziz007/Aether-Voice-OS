"""Galaxy Policy Enforcement for Orchestration.

Enforces per-galaxy policies for planet routing and task execution,
including domain allowlists, latency thresholds, and load limits.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class PolicyViolationLevel(Enum):
    """Severity level of policy violation."""

    WARNING = "warning"
    ERROR = "error"
    BLOCKING = "blocking"


@dataclass
class GalaxyPolicy:
    """Policy configuration for a galaxy."""

    galaxy_id: str
    allowed_domains: List[str] = field(default_factory=list)
    max_parallel_tasks: int = 3
    sensitive_action_requires_confirm: bool = True
    blocked_capabilities: Set[str] = field(default_factory=set)
    max_latency_ms: float = 500.0
    max_load_threshold: float = 0.9


class GalaxyPolicyEnforcer:
    """Enforces per-galaxy policies for planet routing and task execution."""

    def __init__(self):
        """Initialize policy enforcer with default policies."""
        self._policies: Dict[str, GalaxyPolicy] = {}
        self._register_default_policies()

    def _register_default_policies(self) -> None:
        """Register default galaxy policies."""
        self._policies["Genesis"] = GalaxyPolicy(
            galaxy_id="Genesis",
            allowed_domains=[
                "github.com",
                "docs.python.org",
                "stackoverflow.com",
            ],
            max_parallel_tasks=3,
            sensitive_action_requires_confirm=True,
        )
        logger.info("Registered default policy for Genesis galaxy")

    def get_policy(self, galaxy_id: str) -> GalaxyPolicy:
        """Get policy for galaxy.

        Creates a new default policy if galaxy doesn't exist.

        Args:
            galaxy_id: Galaxy identifier

        Returns:
            GalaxyPolicy for the specified galaxy
        """
        if galaxy_id not in self._policies:
            self._policies[galaxy_id] = GalaxyPolicy(galaxy_id=galaxy_id)
            logger.info("Created default policy for galaxy %s", galaxy_id)
        return self._policies[galaxy_id]

    def check_domain_allowed(
        self,
        domain: str,
        galaxy_id: str,
    ) -> Tuple[bool, str]:
        """Check if domain is allowed in galaxy.

        Args:
            domain: Domain to check
            galaxy_id: Galaxy identifier

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        policy = self.get_policy(galaxy_id)
        if domain not in policy.allowed_domains:
            return (
                False,
                f"Domain {domain} not allowed in {galaxy_id}",
            )
        return True, ""

    def check_capability_blocked(
        self,
        capability: str,
        galaxy_id: str,
    ) -> Tuple[bool, str]:
        """Check if capability is blocked in galaxy.

        Args:
            capability: Capability to check
            galaxy_id: Galaxy identifier

        Returns:
            Tuple of (blocked: bool, reason: str)
        """
        policy = self.get_policy(galaxy_id)
        if capability in policy.blocked_capabilities:
            return (
                True,
                f"Capability {capability} is blocked in {galaxy_id}",
            )
        return False, ""

    def validate_routing_decision(
        self,
        planet_id: str,
        galaxy_id: str,
        latency_ms: float,
        load: float,
    ) -> List[str]:
        """Validate routing decision against policy.

        Args:
            planet_id: Planet being routed to
            galaxy_id: Galaxy identifier
            latency_ms: Expected latency in milliseconds
            load: Expected load (0.0-1.0)

        Returns:
            List of policy violation messages (empty if valid)
        """
        policy = self.get_policy(galaxy_id)
        violations = []

        # Check latency threshold
        if latency_ms > policy.max_latency_ms:
            violations.append(
                f"Latency {latency_ms:.0f}ms exceeds max "
                f"{policy.max_latency_ms:.0f}ms for {planet_id}"
            )

        # Check load threshold
        if load > policy.max_load_threshold:
            violations.append(
                f"Load {load:.2f} exceeds threshold "
                f"{policy.max_load_threshold:.2f} for {planet_id}"
            )

        if violations:
            logger.warning(
                "Policy violations for planet %s in %s: %s",
                planet_id,
                galaxy_id,
                violations,
            )

        return violations

    def requires_confirmation(
        self,
        action_type: str,
        galaxy_id: str,
    ) -> bool:
        """Check if action requires user confirmation.

        Args:
            action_type: Type of action being performed
            galaxy_id: Galaxy identifier

        Returns:
            True if confirmation is required
        """
        policy = self.get_policy(galaxy_id)
        return policy.sensitive_action_requires_confirm

    def add_allowed_domain(
        self,
        galaxy_id: str,
        domain: str,
    ) -> None:
        """Add domain to galaxy's allowed list.

        Args:
            galaxy_id: Galaxy identifier
            domain: Domain to add
        """
        policy = self.get_policy(galaxy_id)
        if domain not in policy.allowed_domains:
            policy.allowed_domains.append(domain)
            logger.info(
                "Added domain %s to galaxy %s allowlist",
                domain,
                galaxy_id,
            )

    def block_capability(
        self,
        galaxy_id: str,
        capability: str,
    ) -> None:
        """Block a capability in galaxy.

        Args:
            galaxy_id: Galaxy identifier
            capability: Capability to block
        """
        policy = self.get_policy(galaxy_id)
        policy.blocked_capabilities.add(capability)
        logger.info(
            "Blocked capability %s in galaxy %s",
            capability,
            galaxy_id,
        )

    def get_all_policies(self) -> Dict[str, GalaxyPolicy]:
        """Get all registered policies.

        Returns:
            Dictionary mapping galaxy_id to policy
        """
        return self._policies.copy()
