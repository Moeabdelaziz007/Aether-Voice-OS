"""
Aether Voice OS — Hive Coordinator.

Orchestrates multiple 'Expert' souls and manages the A2A (Agent-to-Agent)
handoff lifecycle. Maintains the expertise-to-soul mapping.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, Optional

if TYPE_CHECKING:
    from core.identity.package import AthPackage
    from core.identity.registry import AetherRegistry
    from core.tools.router import ToolRouter

logger = logging.getLogger(__name__)


class HiveCoordinator:
    """
    Orchestrator for the Aether Hive.

    Responsibilities:
    1. Tracking the currently active Soul.
    2. Finding the best Expert Soul for a task.
    3. Managing context transfer during Handoff.
    """

    def __init__(
        self,
        registry: AetherRegistry,
        router: ToolRouter,
        default_soul_name: str = "ArchitectExpert",
        on_handover: Optional[Callable] = None,
    ) -> None:
        self._registry = registry
        self._router = router
        self._active_soul: Optional[AthPackage] = None
        self._default_soul_name = default_soul_name
        self._on_handover = on_handover
        self._context_bridge: Dict[str, str] = (
            {}
        )  # Key-value store for cross-soul state

    @property
    def active_soul(self) -> AthPackage:
        if not self._active_soul:
            try:
                self._active_soul = self._registry.get(self._default_soul_name)
            except Exception:
                # Fallback to the first available soul if default fails
                pkgs = self._registry.list_packages()
                if pkgs:
                    self._active_soul = self._registry.get(pkgs[0])
                else:
                    logger.error("No souls found in registry!")
        return self._active_soul

    def request_handoff(self, target_name: str, task_context: str) -> bool:
        """Initiates a switch to a specified expert soul."""
        try:
            target = self._registry.get(target_name)
            logger.info(
                "A2A [HIVE] Handoff initiated: %s -> %s",
                self.active_soul.manifest.name,
                target_name,
            )

            # Store context for the next soul to pick up
            self._context_bridge["pending_task"] = task_context
            from_name = (
                self.active_soul.manifest.name if self._active_soul else "System"
            )
            self._active_soul = target

            # Trigger UI notification
            if self._on_handover:
                try:
                    self._on_handover(from_name, target_name, task_context)
                except Exception as e:
                    logger.error("Failed to trigger handover callback: %s", e)

            # TODO: Integrate with engine to restart Gemini session with new config
            return True
        except Exception as e:
            logger.error("Handoff failed: %s", e)
            return False

    def evaluate_intent(self, query: str) -> Optional[str]:
        """
        Check if a better expert exists for the user's query.
        Returns the name of the better expert if found.
        """
        best_expert = self._registry.find_expert(query)
        if best_expert and best_expert.manifest.name != self.active_soul.manifest.name:
            # Only suggest if the expertise score is significantly high
            return best_expert.manifest.name
        return None
