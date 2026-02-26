"""
Aether Voice OS — Engine (Orchestrator).

The central nervous system of Aether. Owns the lifecycle
of all components and the asyncio.Queue pipeline:

    Mic → audio_in_queue → Gemini → audio_out_queue → Speaker
                                  → Gateway (events)

Uses asyncio.TaskGroup for structured concurrency:
if any component crashes, all others are cancelled cleanly.

This is the "WhisperFlow powered by Gemini" — a single
unified pipeline that replaces:
    Whisper STT → GPT → TTS
with:
    Gemini Native Audio (STT + reasoning + TTS in one model)

Supports ADK-style tool registration for modular extensibility.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import Any, Optional

from core.admin_api import SHARED_STATE, AdminAPIServer
from core.ai import handoff
from core.ai.genetic import GeneticOptimizer
from core.ai.hive import HiveCoordinator
from core.ai.session import GeminiLiveSession
from core.audio.capture import AudioCapture
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.audio.playback import AudioPlayback
from core.audio.processing import AdaptiveVAD
from core.config import AetherConfig, load_config
from core.identity.package import AthPackage
from core.identity.registry import AetherRegistry
from core.tools import hive_memory, memory_tool, system_tool, tasks_tool, vision_tool
from core.tools import voice_tool as voice_tool_mod
from core.tools.firebase_tool import FirebaseConnector
from core.tools.router import ToolRouter
from core.transport.gateway import AetherGateway

logger = logging.getLogger(__name__)


class AetherEngine:
    """
    The Aether Voice Engine — orchestrates all components.

    Lifecycle:
      1. Load config from environment
      2. Initialize identity registry (.ath packages)
      3. Open audio devices (mic + speaker)
      4. Connect to Gemini Live
      5. Start gateway for external clients
      6. Run pipeline until SIGINT/SIGTERM
      7. Graceful shutdown: stop capture → drain queues → close session → stop gateway
    """

    def __init__(self, config: Optional[AetherConfig] = None) -> None:
        self._config = config or load_config()
        self._setup_logging()

        # Pipeline queues
        self._audio_in: asyncio.Queue[dict[str, object]] = asyncio.Queue(
            maxsize=self._config.audio.mic_queue_max
        )
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=50)

        # Firebase persistence layer (created before tools so they can reference it)
        self._firebase = FirebaseConnector()

        # Neural Dispatcher — routes Gemini tool_calls to handlers
        self._router = ToolRouter()
        self._router.init_vector_store(self._config.ai.api_key)

        # Affective Computing: Paralinguistic Analyzer
        self._paralinguistics = ParalinguisticAnalyzer(
            sample_rate=self._config.audio.send_sample_rate
        )

        # Components
        self._vad = AdaptiveVAD(
            window_size_sec=self._config.audio.vad_window_sec
            if hasattr(self._config.audio, "vad_window_sec")
            else 5.0,
            sample_rate=self._config.audio.send_sample_rate,
        )
        self._capture = AudioCapture(
            self._config.audio,
            self._audio_in,
            vad_engine=self._vad,
            paralinguistic_analyzer=self._paralinguistics,
            on_affective_data=self._on_affective_data,
        )
        self._gateway = AetherGateway(
            self._config.gateway, on_audio_rx=self._audio_in.put
        )
        self._playback = AudioPlayback(
            self._config.audio,
            self._audio_out,
            on_audio_tx=self._gateway.broadcast_binary,
        )
        self._session = GeminiLiveSession(
            self._config.ai,
            self._audio_in,
            self._audio_out,
            on_interrupt=self._on_interrupt,
            on_tool_call=self._on_tool_call,
            tool_router=self._router,
        )
        self._registry = AetherRegistry(
            self._config.packages_dir, on_change=self._on_package_change
        )
        self._hive = HiveCoordinator(
            registry=self._registry,
            router=self._router,
            default_soul_name="ArchitectExpert",
        )
        self._admin_api = AdminAPIServer(port=18790)

        # Genetic Evolution Layer
        self._optimizer = GeneticOptimizer(
            self._firebase, api_key=self._config.ai.api_key
        )

        # ADK Tool Registry (legacy — kept for backward compat)
        self._tools: dict[str, Any] = {}

        self._shutdown_event = asyncio.Event()
        self._session_restart = asyncio.Event()

    def _register_tools(self) -> None:
        """Register all tool modules with the Neural Dispatcher."""
        # Inject Firebase connector into persistence tools
        tasks_tool.set_firebase_connector(self._firebase)
        memory_tool.set_firebase_connector(self._firebase)

        self._router.register_module(system_tool)
        self._router.register_module(tasks_tool)
        self._router.register_module(memory_tool)
        self._router.register_module(voice_tool_mod)
        self._router.register_module(vision_tool)
        self._router.register_module(handoff)
        self._router.register_module(hive_memory)

        # Connect Hive to tools
        handoff.set_hive_params(self._hive, self._session_restart)
        hive_memory.set_firebase_connector(self._firebase)

        logger.info(
            "Neural Dispatcher ready: %d tools registered",
            self._router.count,
        )

    def _setup_logging(self) -> None:
        """Configure structured logging."""
        logging.basicConfig(
            level=getattr(logging, self._config.log_level.upper(), logging.INFO),
            format=("%(asctime)s │ %(levelname)-7s │ %(name)-28s │ %(message)s"),
            datefmt="%H:%M:%S",
        )

    def _on_interrupt(self) -> None:
        """
        Called when Gemini signals barge-in — implements Cognitive Barge-in.
        Refined with Hybrid Cognition: System 1 (Reflex) & System 2 (Semantic).
        """
        from core.audio.state import audio_state

        is_hard = audio_state.is_hard
        rms = audio_state.last_rms
        stype = audio_state.silence_type

        vad_payload: dict[str, object] = {
            "type": "interrupted",
            "rms": rms,
            "is_hard": is_hard,
            "silence_type": stype,
        }

        # Cognitive Guard: If it's a hard signal but classified as non-speech, it's likely noise.
        # We duck instead of stop to maintain Aether's "presence".
        if is_hard and stype not in ("thinking", "breathing", "void"):
            logger.info(
                "⚡ Hard Barge-in (Speech detected, RMS: %.2f) — Stopping playback.",
                rms,
            )
            self._playback.interrupt()
            vad_payload["action"] = "hard_stop"
        else:
            logger.info(
                "🌊 Semantic Ducking (Type: %s, RMS: %.2f) — Maintaining presence.",
                stype,
                rms,
            )
            self._playback.set_gain(0.2)
            vad_payload["action"] = "ducking"

        # Broadcast VAD event to connected UI clients
        asyncio.create_task(self._gateway.broadcast("vad.event", vad_payload))

    def _on_affective_data(self, features: ParalinguisticFeatures) -> None:
        """Handle incoming affective metrics from the capture layer."""
        if self._firebase.is_connected:
            asyncio.create_task(self._firebase.log_affective_metrics(features))

    async def _on_tool_call(self, tool_name: str, args: dict, result: dict) -> None:
        """Log tool calls to Firestore for session analytics."""
        if not self._firebase.is_connected:
            return
        try:
            from datetime import datetime, timezone

            await self._firebase._db.collection("events").add(
                {
                    "type": "tool_call",
                    "tool": tool_name,
                    "args_summary": str(args)[:200] if args else "{}",
                    "result_status": result.get("status", "unknown"),
                    "session_id": self._firebase._session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as exc:
            logger.debug("Analytics log failed: %s", exc)

    async def _on_package_change(
        self, name: str, package: Optional[AthPackage]
    ) -> None:
        """Handle dynamic package loading/unloading."""
        if package:
            logger.info("Hot-Reloading package: %s", name)
            # 1. Un-register old tools first if they exist
            # Note: In a production version, we'd track which tools belong to which package.
            # For now, we assume tool names are unique.
            # 2. Register tools from package
            # TODO: Implement dynamic module import for .ath packages
            pass
        else:
            logger.info("Unloading package: %s", name)
            # TODO: Clean up tools associated with this package

    def register_tool(self, name: str, tool: Any) -> None:
        """Register an ADK-compatible tool with the engine."""
        self._tools[name] = tool
        logger.info("Registered tool: %s", name)

    async def run(self) -> None:
        """
        Main engine lifecycle.

        All components run as concurrent tasks inside a TaskGroup.
        If any crashes, all others are cancelled (structured concurrency).
        SIGINT/SIGTERM trigger graceful shutdown.
        """
        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._signal_shutdown)

        # Load identity packages
        self._registry.scan()
        self._registry.start_watcher()

        # Initialize Firebase (non-blocking — engine runs even if Firebase fails)
        firebase_ok = await self._firebase.initialize()
        if firebase_ok:
            await self._firebase.start_session()
            logger.info(
                "  Firebase: ✦ Connected — session %s", self._firebase._session_id
            )
        else:
            logger.warning("  Firebase: ✗ Offline — tasks will not persist")

        # Register tools now that we have an active event loop
        self._register_tools()

        logger.info("═" * 60)
        logger.info("  AETHER VOICE OS — Starting Engine")
        logger.info("  Model: %s", self._config.ai.model.value)
        logger.info("  Gateway: ws://0.0.0.0:%d", self._config.gateway.port)
        logger.info("  Packages: %d loaded", self._registry.count)
        logger.info("  Neural Tools: %s", ", ".join(self._router.names))
        if self._tools:
            logger.info("  ADK Tools: %s", ", ".join(self._tools.keys()))
        logger.info("═" * 60)

        try:
            # Initialize audio devices
            await self._capture.start()
            await self._playback.start()

            # Integrate Admin API locally
            self._admin_api.start()

            # The Hive Loop: Manages the Gemini session lifecycle and soul handoffs
            while not self._shutdown_event.is_set():
                self._session_restart.clear()

                # Create a fresh session with the active expert soul
                active_soul = self._hive.active_soul
                self._session = GeminiLiveSession(
                    self._config.ai,
                    self._audio_in,
                    self._audio_out,
                    on_interrupt=self._on_interrupt,
                    on_tool_call=self._on_tool_call,
                    tool_router=self._router,
                    soul_manifest=active_soul.manifest,
                )

                await self._session.connect()

                logger.info(
                    "✦ Hive Active: Expert '%s' taking control",
                    active_soul.manifest.name,
                )

                # Run session alongside other background tasks
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self._capture.run(), name="audio-capture")
                    tg.create_task(self._playback.run(), name="audio-playback")
                    session_task = tg.create_task(
                        self._session.run(), name="gemini-session"
                    )
                    tg.create_task(self._gateway.run(), name="gateway")
                    tg.create_task(self._admin_sync_loop(), name="admin-sync")

                    # Watcher for shutdown or restart
                    restart_waiter = tg.create_task(
                        self._session_restart.wait(), name="restart-waiter"
                    )
                    shutdown_waiter = tg.create_task(
                        self._shutdown_event.wait(), name="shutdown-waiter"
                    )

                    # Wait for either session to end, restart triggered, or shutdown
                    done, pending = await asyncio.wait(
                        [session_task, restart_waiter, shutdown_waiter],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # Clean up pending tasks in the group
                    for p in pending:
                        p.cancel()

                if self._session_restart.is_set():
                    logger.info("🔄 Hive Handoff: Preparing next expert...")

                    # TRIGGER GENETIC EVOLUTION
                    # We evolve the 'soul' instructions based on the just-finished session performance
                    mutation = await self._optimizer.evolve(
                        current_instructions=active_soul.manifest.general_instructions,
                        session_id=self._firebase._session_id,
                    )
                    if mutation:
                        logger.info(
                            "🧬 Genetic Leap: Soul '%s' instruction set evolved.",
                            active_soul.manifest.name,
                        )
                        # TODO: Hot-patch the in-memory registry if needed, or wait for next session
                        # For now, we trust the registry watcher to handle file-system mutations
                        # A higher-tier implementation would write back to the .ath file.

                    await self._session.stop()
                    # Brief delay for audio cross-fade (simulated)
                    await asyncio.sleep(1.0)
                else:
                    # If sesson ended naturally and not because of restart/shutdown
                    if not self._shutdown_event.is_set():
                        logger.warning(
                            "Gemini session ended unexpectedly. Restarting in 5s..."
                        )
                        await asyncio.sleep(5.0)

        except* KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except* Exception as eg:
            for exc in eg.exceptions:
                if not isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt)):
                    logger.error("Engine error: %s", exc, exc_info=True)
        finally:
            await self._shutdown()

    def _signal_shutdown(self) -> None:
        """Handle SIGINT/SIGTERM."""
        logger.info("Shutdown signal received")
        self._shutdown_event.set()

    async def _wait_for_shutdown(self) -> None:
        """Wait for shutdown signal, then cancel the TaskGroup."""
        await self._shutdown_event.wait()
        raise asyncio.CancelledError("Shutdown requested")

    async def _admin_sync_loop(self) -> None:
        """Background task to continually update Admin API shared state."""
        import json
        import os

        synapse_path = os.path.expanduser("~/.aetheros/synapse/heartbeat.ath")
        while True:
            try:
                # 1. Update Sessions from Firestore
                if self._firebase.is_connected and self._firebase._db:
                    query = (
                        self._firebase._db.collection("sessions")
                        .order_by("started_at", direction="DESCENDING")
                        .limit(10)
                    )
                    sessions = []
                    async for doc in query.stream():
                        d = doc.to_dict()
                        if d:
                            d["id"] = doc.id
                            sessions.append(d)
                    SHARED_STATE["sessions"] = sessions

                # 2. Update L2 Synapse Status
                if os.path.exists(synapse_path):
                    with open(synapse_path, "r", encoding="utf-8") as f:
                        SHARED_STATE["synapse"] = json.load(f)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Admin sync error: %s", e)

            await asyncio.sleep(2.0)

    async def _shutdown(self) -> None:
        """Graceful shutdown sequence."""
        logger.info("Starting graceful shutdown...")

        # Stop in reverse order: capture first, then processor, then output
        await self._capture.stop()
        await self._session.stop()
        await self._playback.stop()
        await self._gateway.stop()
        self._registry.stop_watcher()
        self._admin_api.stop()

        # End Firebase session with summary
        if self._firebase.is_connected:
            await self._firebase.end_session(
                {
                    "tools_used": self._router.names,
                    "tool_count": self._router.count,
                }
            )

        logger.info("═" * 60)
        logger.info("  AETHER VOICE OS — Engine stopped cleanly")
        logger.info("═" * 60)


def main() -> None:
    """Entry point for `python -m core.engine`."""
    try:
        engine = AetherEngine()
        asyncio.run(engine.run())
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
