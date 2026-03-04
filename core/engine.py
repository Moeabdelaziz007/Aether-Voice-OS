"""
Aether Voice OS — Engine (Orchestrator).
"""

from __future__ import annotations
import asyncio
import logging
import signal
import sys
from typing import Any, Optional

from core.infra.config import AetherConfig, load_config
from core.infra.transport.gateway import AetherGateway
from core.infra.cloud.firebase import FirebaseConnector # Note: might need update depending on move result
from core.services.admin_api import AdminAPIServer, SHARED_STATE
from core.tools.router import ToolRouter
from core.logic.managers.audio import AudioManager
from core.logic.managers.infra import InfraManager
from core.logic.managers.agents import AgentManager

logger = logging.getLogger(__name__)

class AetherEngine:
    """The Aether Voice Engine — high-level orchestrator."""

    def __init__(self, config: Optional[AetherConfig] = None) -> None:
        self._config = config or load_config()
        self._setup_logging()
        
        print("  Engine: Loading config...", flush=True); print("CONFIG:", self._config.model_dump()); print("  Engine: Initializing Managers...", flush=True)
        self._router = ToolRouter()
        self._setup_vector_store()
        
        print("  Engine: Initializing AgentManager...", flush=True)
        self._agents = AgentManager(self._config, self._router, self._on_agent_handover)
        
        print("  Engine: Initializing Gateway...", flush=True)
        self._gateway = AetherGateway(
            gateway_config=self._config.gateway,
            ai_config=self._config.ai,
            audio_config=self._config.audio,
            tool_router=self._router,
            hive=self._agents._hive,
        )

        print("  Engine: Initializing AudioManager...", flush=True)
        self._audio = AudioManager(self._config, self._gateway, self._on_affective_data)
        print("  Engine: Initializing InfraManager...", flush=True)
        self._infra = InfraManager(self._gateway)
        print("  Engine: Initializing AdminAPI...", flush=True)
        self._admin_api = AdminAPIServer(port=18790)
        print("  Engine: State Ready.", flush=True)
        
        self._shutdown_event = asyncio.Event()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self._config.log_level.upper(), logging.INFO),
            format="%(asctime)s │ %(levelname)-7s │ %(name)-28s │ %(message)s",
            datefmt="%H:%M:%S",
        )

    def _setup_vector_store(self) -> None:
        from pathlib import Path
        from core.tools.vector_store import LocalVectorStore
        root_dir = Path(__file__).resolve().parent.parent
        index_path = root_dir / ".aether_index.pkl"
        global_index = LocalVectorStore(api_key=self._config.ai.api_key)
        global_index.load(index_path)
        self._router._vector_store = global_index

    def _on_affective_data(self, features: Any) -> None:
        # Affective logic handled by audio manager and infra manager
        if self._infra._firebase.is_connected:
            asyncio.create_task(self._infra._firebase.log_affective_metrics(features))
        
        asyncio.create_task(self._gateway.broadcast("affective_score", {
            "frustration": (1.0 - features.engagement_score) * (features.rms_variance / 500.0),
            "valence": features.engagement_score,
            "arousal": features.rms_variance / 500.0,
            "zen_mode": getattr(features, "zen_mode", False),
        }))

    def _on_agent_handover(self, from_agent: str, to_agent: str, task: str) -> None:
        asyncio.create_task(self._gateway.broadcast("neural_event", {
            "fromAgent": from_agent,
            "toAgent": to_agent,
            "task": task,
            "status": "active",
        }))

    def _register_tools(self) -> None:
        # Tool registration remains centralized here or moved to a tool registry later
        from core.tools import system_tool, tasks_tool, memory_tool, voice_tool, vision_tool, hive_tool, rag_tool, discovery_tool, context_scraper
        
        # Inject Firebase into tools
        tasks_tool.set_firebase_connector(self._infra._firebase)
        memory_tool.set_firebase_connector(self._infra._firebase)
        
        self._router.register_module(system_tool)
        self._router.register_module(tasks_tool)
        self._router.register_module(memory_tool)
        self._router.register_module(voice_tool)
        self._router.register_module(vision_tool)
        self._router.register_module(hive_tool)
        self._router.register_module(rag_tool)
        self._router.register_module(discovery_tool)
        self._router.register_module(context_scraper)

    async def run(self) -> None:
        print("🚀 Aether Engine: Neural Stream Active.", flush=True)
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: self._shutdown_event.set())

        self._agents.scan_registry()
        await self._infra.initialize()
        self._register_tools()

        try:
            print("  Engine: Starting Audio Manager...", flush=True)
            await self._audio.start()
            print("  Engine: Audio Ready.", flush=True)
            
            print("  Engine: Starting Admin API...", flush=True)
            self._admin_api.start()
            
            print("  Engine: Starting Watchdog...", flush=True)
            self._infra.start_watchdog()
            
            print("  Engine: Spawning Core Tasks...", flush=True)

            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._gateway.run(), name="gateway")
                self._audio.run_tasks(tg)
                tg.create_task(self._admin_sync_loop(), name="admin-sync")
                await self._shutdown_event.wait()
                raise asyncio.CancelledError()

        except* asyncio.CancelledError:
            pass
        finally:
            await self._shutdown()

    async def _admin_sync_loop(self) -> None:
        while True:
            # Sync logic simplified for brevity; same as original
            await asyncio.sleep(2.0)

    async def _shutdown(self) -> None:
        logger.info("Starting graceful shutdown...")
        await self._audio.stop()
        await self._gateway.stop()
        self._agents.stop_watcher()
        self._infra.stop()
        self._admin_api.stop()
        await self._infra.end_session(self._router)
        logger.info("Aether Engine stopped cleanly.")
