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

from core.config import AetherConfig, load_config
from core.audio.capture import AudioCapture
from core.audio.playback import AudioPlayback
from core.ai.session import GeminiLiveSession
from core.transport.gateway import AetherGateway
from core.identity.registry import AetherRegistry
from core.tools.router import ToolRouter
from core.tools import system_tool, tasks_tool, memory_tool, vision_tool
from core.tools import voice_tool as voice_tool_mod
from core.tools.firebase_tool import FirebaseConnector
from core.tools.search_tool import get_search_tool
from core.admin_api import AdminAPIServer, SHARED_STATE

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
        self._register_tools()

        # Components
        self._capture = AudioCapture(self._config.audio, self._audio_in)
        self._playback = AudioPlayback(self._config.audio, self._audio_out)
        self._session = GeminiLiveSession(
            self._config.ai,
            self._audio_in,
            self._audio_out,
            on_interrupt=self._on_interrupt,
            on_tool_call=self._on_tool_call,
            tool_router=self._router,
        )
        self._gateway = AetherGateway(self._config.gateway)
        self._registry = AetherRegistry(self._config.packages_dir)
        self._admin_api = AdminAPIServer(port=18790)

        # ADK Tool Registry (legacy — kept for backward compat)
        self._tools: dict[str, Any] = {}

        self._shutdown_event = asyncio.Event()

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
        logger.info(
            "Neural Dispatcher ready: %d tools registered",
            self._router.count,
        )

    def _setup_logging(self) -> None:
        """Configure structured logging."""
        logging.basicConfig(
            level=getattr(logging, self._config.log_level.upper(), logging.INFO),
            format=(
                "%(asctime)s │ %(levelname)-7s │ %(name)-28s │ %(message)s"
            ),
            datefmt="%H:%M:%S",
        )

    def _on_interrupt(self) -> None:
        """
        Called when Gemini signals barge-in — stop playback instantly.

        Also samples the audio input for energy level via Rust VAD
        and broadcasts the event to connected UI clients.
        """
        self._playback.interrupt()

        # Sample energy from the last audio chunk for UI reactivity
        vad_payload: dict[str, object] = {"type": "interrupted"}
        try:
            from core.audio.processing import energy_vad
            import numpy as np

            # Peek at the most recent chunk in the input queue (non-blocking)
            if not self._audio_in.empty():
                last_msg = self._audio_in._queue[-1]  # type: ignore[attr-defined]
                if isinstance(last_msg, dict) and "data" in last_msg:
                    pcm = np.frombuffer(last_msg["data"], dtype=np.int16)
                    result = energy_vad(pcm)
                    vad_payload["energy_rms"] = result.energy_rms
                    vad_payload["is_speech"] = result.is_speech
        except Exception:
            pass  # Non-critical — UI enhancement only

        # Broadcast VAD event to connected UI clients
        asyncio.create_task(
            self._gateway.broadcast("vad.event", vad_payload)
        )

    async def _on_tool_call(
        self, tool_name: str, args: dict, result: dict
    ) -> None:
        """Log tool calls to Firestore for session analytics."""
        if not self._firebase.is_connected:
            return
        try:
            from datetime import datetime, timezone

            await self._firebase._db.collection("events").add({
                "type": "tool_call",
                "tool": tool_name,
                "args_summary": str(args)[:200] if args else "{}",
                "result_status": result.get("status", "unknown"),
                "session_id": self._firebase._session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            logger.debug("Analytics log failed: %s", exc)

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

        # Initialize Firebase (non-blocking — engine runs even if Firebase fails)
        firebase_ok = await self._firebase.initialize()
        if firebase_ok:
            await self._firebase.start_session()
            logger.info("  Firebase: ✦ Connected — session %s", self._firebase._session_id)
        else:
            logger.warning("  Firebase: ✗ Offline — tasks will not persist")

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

            # Connect to Gemini
            await self._session.connect()

            # Integrate Admin API locally
            self._admin_api.start()

            # Run all tasks concurrently
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._capture.run(), name="audio-capture")
                tg.create_task(self._playback.run(), name="audio-playback")
                tg.create_task(self._session.run(), name="gemini-session")
                tg.create_task(self._gateway.run(), name="gateway")
                tg.create_task(self._admin_sync_loop(), name="admin-sync")
                tg.create_task(self._wait_for_shutdown(), name="shutdown-watcher")

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
                    query = self._firebase._db.collection("sessions").order_by(
                        "started_at", direction="DESCENDING"
                    ).limit(10)
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
        self._admin_api.stop()

        # End Firebase session with summary
        if self._firebase.is_connected:
            await self._firebase.end_session({
                "tools_used": self._router.names,
                "tool_count": self._router.count,
            })

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
