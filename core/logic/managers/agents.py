import logging
import asyncio
from typing import Optional, Any, Callable
from pathlib import Path
from core.ai.hive import HiveCoordinator
from core.services.registry import AetherRegistry
from core.ai.handover.handler import MultiAgentOrchestrator
from core.infra.config import AetherConfig

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages AI agents, registry, and handovers."""
    
    def __init__(self, config: AetherConfig, router: Any, on_handover: Callable):
        self._config = config
        self._router = router
        
        self._registry = AetherRegistry(
            self._config.packages_dir, 
            on_change=self._on_package_change
        )
        self._registry.initialize_vector_store(self._config.ai.api_key)
        
        self._hive = HiveCoordinator(
            registry=self._registry,
            router=self._router,
            default_soul_name="ArchitectExpert",
            on_handover=on_handover,
            ai_config=self._config.ai,
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
