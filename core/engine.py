import asyncio
import logging
import signal
import sys
from typing import Any, Dict

from core.ai.gws_bridge import gws_bridge
from core.ai.scheduler import CognitiveScheduler
from core.ai.session import GeminiLiveSession
from core.ai.thalamic import ThalamicGate
from core.infra.config import load_config
from core.infra.event_bus import EventBus
from core.infra.transport.gateway import AetherGateway
from core.logic.managers.agents import AgentManager
from core.logic.managers.audio import AudioManager
from core.logic.managers.infra import InfraManager
from core.logic.managers.pulse import PulseManager
from core.services.admin_api import AdminAPIServer
from core.tools.router import ToolRouter

# Ensure core logs are captured with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)-28s │ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("AetherOS.Engine")


class AetherEngine:
    """
    AetherOS V2.5 — The "Manager-Driven" Orchestrator.
    Decomposes the previous monolithic engine into specialized service managers:
    - InfraManager: Firebase, Watchdog, SRE protocols.
    - AudioManager: Capture, Playback, Paralinguistics, AEC.
    - AgentManager: Registry, Hive Coordinator, DNA/Handovers.
    - PulseManager: Proactive vision/context heartbeat.
    - CognitiveScheduler: Proactive task scheduling.
    """

    def __init__(self):
        self._config = load_config()
        self._event_bus = EventBus()

        # Shared Tool Router
        self._router = ToolRouter()

        # Register core skills (MCP Bridge)
        self._router.register_module(gws_bridge)

        # 1. Specialized Managers
        # Agents: Registry + Hive
        self._agents = AgentManager(
            config=self._config,
            router=self._router,
            on_handover=self._on_agent_handover,
            event_bus=self._event_bus,
        )

        # Audio: Capture + Playback + Analysis
        self._audio = AudioManager(
            config=self._config,
            gateway=self,
            on_affective_data=self._on_affective_data,
            event_bus=self._event_bus,
        )

        # Infrastructure: Firebase + Watchdog
        self._infra = InfraManager(gateway=self, audio_manager=self._audio)

        # Proactive Perceivers
        self._pulse = PulseManager(event_bus=self._event_bus)
        self._scheduler = CognitiveScheduler(self._event_bus, self._router)

        # Inject Scheduler into Hive for proactive prompt injection
        self._agents._hive._scheduler = self._scheduler

        # 2. Main AI Session (The Core Brain)
        self._session = GeminiLiveSession(
            config=self._config.ai,
            gateway=self,
            audio_in_queue=self._audio.input_queue,
            audio_out_queue=self._audio.output_queue,
            tool_router=self._router,
            soul_manifest=self._agents._registry.get(self._config.ai.default_soul),
            agent_registry=self._agents._registry,
            firebase=self._infra._firebase,
        )

        # 3. Proactive Intervention Engine (Thalamic Gate)
        self._thalamic = ThalamicGate(self._session)

        # 4. Control Interface
        self._admin_api = AdminAPIServer(port=self._config.admin_port or 18790)

        # 5. External Gateway (WebSocket Bridge)
        self._gateway = AetherGateway(
            config=self._config.gateway,
            ai_config=self._config.ai,
            hive=self._agents._hive,
            bus=self._event_bus,
            tool_router=self._router,
        )

        self._running = False
        self._shutdown_event = asyncio.Event()

    @property
    def audio_in_queue(self) -> asyncio.Queue:
        return self._session.audio_in_queue

    @property
    def audio_out_queue(self) -> asyncio.Queue:
        return self._session.audio_out_queue

    @property
    def _bus(self) -> EventBus:
        """Internal alias for manager compatibility."""
        return self._event_bus

    def broadcast(self, data: Dict[str, Any]) -> None:
        """Broadcasts telemetry to the Admin API (Web UI)."""
        self._admin_api.broadcast(data)

    def broadcast_binary(self, data: bytes) -> None:
        """Broadcasts raw binary (audio) to Admin clients."""
        self._admin_api.broadcast_binary(data)

    async def run(self) -> None:
        """Main engine execution loop using TaskGroups."""
        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._signal_shutdown)

        logger.info("═" * 60)
        logger.info("  AETHER VOICE OS — Starting Engine V2.5")
        logger.info("═" * 60)

        # Initialize Infrastructure
        await self._infra.initialize()

        # Start GWS MCP Daemon (Silent Auth)
        await gws_bridge.start()

        # Start Admin API
        self._admin_api.start()

        # Initialize Registry
        self._agents.scan_registry()

        # Start Core Brain
        await self._session.start()

        # Start Audio Pipeline
        await self._audio.start()

        # Start Proactive Pulse
        await self._pulse.start()

        # Start Thalamic Gate
        await self._thalamic.start()

        self._running = True
        logger.info("🚀 Engine fully online. Listening...")

        try:
            async with asyncio.TaskGroup() as tg:
                # 1. Run main brain session
                tg.create_task(self._session.run(), name="genai-session")

                # 2. Run audio lifecycle
                self._audio.run_tasks(tg)

                # 3. Start Watchdog (Self-Healing)
                self._infra.start_watchdog()

                # 4. Run External Gateway
                tg.create_task(self._gateway.start(), name="aether-gateway")

                # 5. Wait for shutdown signal
                await self._shutdown_event.wait()
                logger.info("✦ Shutdown event received: Stopping core tasks...")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception("Engine fatal error: %s", e)
        finally:
            await self._shutdown()

    async def _shutdown(self) -> None:
        """Graceful shutdown sequence."""
        self._running = False
        logger.info("Starting graceful shutdown...")

        await gws_bridge.stop()
        await self._thalamic.stop()
        await self._pulse.stop()
        await self._audio.stop()
        await self._session.stop()
        self._agents.stop_watcher()
        self._infra.stop()
        await self._infra.end_session(self._router)
        self._admin_api.stop()

        logger.info("═" * 60)
        logger.info("  AETHER VOICE OS — Engine stopped cleanly")
        logger.info("═" * 60)

    def _signal_shutdown(self) -> None:
        """Handle SIGINT/SIGTERM."""
        logger.info("Shutdown signal received")
        self._shutdown_event.set()

    def _on_affective_data(self, features: Any) -> None:
        """Bridge affective features to telemetry and UI."""
        self.broadcast(
            {
                "type": "affective_pulse",
                "engagement": features.engagement_score,
                "latency": features.processing_ms or 0,
            }
        )

    def _on_agent_handover(self, source: str, target: str, context: str) -> None:
        """Logged when the Hive Coordinator swaps expert souls."""
        logger.info("🤝 HANDOVER: %s -> %s | Context: %s", source, target, context)
        self.broadcast(
            {"type": "agent_handover", "from": source, "to": target, "reason": context}
        )


def main() -> None:
    try:
        engine = AetherEngine()
        asyncio.run(engine.run())
    except Exception as e:
        logger.exception("Startup failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
