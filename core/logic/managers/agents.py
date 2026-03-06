import logging
from typing import Any, Callable, Optional

from core.ai.hive import HiveCoordinator
from core.infra.config import AetherConfig
from core.services.registry import AetherRegistry

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages AI agents, registry, and handovers."""

    def __init__(
        self,
        config: AetherConfig,
        router: Any,
        on_handover: Callable,
        event_bus: Optional[Any] = None,
    ):
        self._config = config
        self._router = router
        self._event_bus = event_bus

        self._registry = AetherRegistry(
            self._config.packages_dir, on_change=self._on_package_change
        )
        self._registry.initialize_vector_store(self._config.ai.api_key)

        self._hive = HiveCoordinator(
            registry=self._registry,
            router=self._router,
            default_soul_name="ArchitectExpert",
            on_handover=on_handover,
            event_bus=self._event_bus,
            api_key=self._config.ai.api_key,
        )

    def scan_registry(self):
        self._registry.scan()
        self._registry.start_watcher()

    def stop_watcher(self):
        self._registry.stop_watcher()

    async def _on_package_change(self, name: str, package: Optional[Any]) -> None:
        if package:
            logger.info("Hot-Reloading package: %s", name)
        else:
            logger.info("Unloading package: %s", name)
