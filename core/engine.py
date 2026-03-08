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
import os
import signal
import sys
from datetime import datetime
from typing import Any, Optional

import aiofiles
from google.adk.runners import InMemoryRunner
from google.genai import types

from core.ai.adk_agents import root_agent
from core.ai.agents.proactive import (
    CodeAwareProactiveAgent,
    ProactiveInterventionEngine,
)
from core.ai.codex._bridge import AetherCodex
from core.ai.genetic import GeneticOptimizer
from core.ai.handover.protocol import create_handoff_protocol
from core.ai.hive import HiveCoordinator
from core.ai.session import GeminiLiveSession
from core.audio.capture import AudioCapture
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.audio.playback import AudioPlayback
from core.audio.processing import AdaptiveVAD
from core.identity.package import AthPackage
from core.infra.cloud.firebase.interface import FirebaseConnector
from core.infra.config import AetherConfig, load_config
from core.infra.transport.gateway import AetherGateway
from core.services.admin_api import SHARED_STATE, AdminAPIServer
from core.services.registry import AetherRegistry
from core.tools import (
    aix_tool,
    hive_memory,
    memory_tool,
    system_tool,
    tasks_tool,
    voyager_tool,
    vision_tool,
    widget_awareness_tool,
    workspace_tool,
)
from core.tools.router import ToolRouter

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
        self._audio_out: asyncio.Queue[bytes] = asyncio.Queue(maxsize=15)

        # Firebase persistence layer
        self._firebase = FirebaseConnector()

        # Google ADK Runner
        self._adk_runner = InMemoryRunner(agent=root_agent)

        # Neural Dispatcher — routes Gemini tool_calls to handlers
        from pathlib import Path

        from core.tools.vector_store import LocalVectorStore

        self._router = ToolRouter()

        # Load local index for semantic routing and RAG
        root_dir = Path(__file__).resolve().parent.parent
        index_path = root_dir / ".aether_index.pkl"
        global_index = LocalVectorStore(api_key=self._config.ai.api_key)
        global_index.load(index_path)

        # Inject global index into router for semantic recovery
        self._router._vector_store = global_index

        # Affective Computing: Paralinguistic Analyzer
        self._paralinguistics = ParalinguisticAnalyzer(
            sample_rate=self._config.audio.send_sample_rate
        )

        # Components
        self._vad = AdaptiveVAD(
            window_size_sec=(
                self._config.audio.vad_window_sec
                if hasattr(self._config.audio, "vad_window_sec")
                else 5.0
            ),
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
            ai_config=self._config.ai,
            audio_config=self._config.audio,
            gateway_config=self._config.gateway,
            tool_router=self._router,
            hive=self._hive,  # Gateway needs hive (might be None initially)
            on_audio_rx=self._audio_in.put,
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
            on_handover=self._on_agent_handover,
        )
        self._admin_api = AdminAPIServer(port=18790)

        self._optimizer = GeneticOptimizer(
            self._firebase, api_key=self._config.ai.api_key
        )

        # Codex: Real-time Knowledge Bridge
        self._codex = AetherCodex(
            firebase=self._firebase,
            session=self._session,
            pulse_interval=self._config.ai.codex_pulse_interval
            if hasattr(self._config.ai, "codex_pulse_interval")
            else 10.0,
        )

        # Phase 4: Proactive Intelligence Engine
        self._proactive_engine = ProactiveInterventionEngine()
        self._proactive_agent = CodeAwareProactiveAgent()

        # ADK Tool Registry (legacy — kept for backward compat)
        self._tools: dict[str, Any] = {}

        self._shutdown_event = asyncio.Event()
        # Background task tracking to avoid GC issues
        self._background_tasks: set[asyncio.Task] = set()

    def _run_background_task(
        self, coro: Any, name: Optional[str] = None
    ) -> asyncio.Task:
        """Helper to run and track background tasks safely."""
        task = asyncio.create_task(coro, name=name)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def _register_tools(self) -> None:
        """Register all tool modules with the Neural Dispatcher."""
        from core.tools import (
            context_scraper,
            discovery_tool,
            hive_tool,
            rag_tool,
            voice_tool,
        )

        # Inject references into Discovery tool
        discovery_tool.set_references(affective=self._proactive_engine, hive=self._hive)

        # Inject Hive Coordinator into Hive tool
        hive_tool.set_hive_coordinator(self._hive)

        # Inject vector index to RAG tool
        rag_tool.set_shared_index(self._router._vector_store)

        # Inject Firebase connector into persistence tools
        tasks_tool.set_firebase_connector(self._firebase)
        memory_tool.set_firebase_connector(self._firebase)
        workspace_tool.set_workspace_event_emitter(self._emit_workspace_event)
        voyager_tool.set_mirror_event_emitter(self._emit_workspace_event)

        self._router.register_module(system_tool)
        self._router.register_module(tasks_tool)
        self._router.register_module(memory_tool)
        self._router.register_module(voice_tool)
        self._router.register_module(vision_tool)
        self._router.register_module(hive_tool)
        self._router.register_module(rag_tool)
        self._router.register_module(discovery_tool)
        self._router.register_module(context_scraper)
        self._router.register_module(aix_tool)
        self._router.register_module(workspace_tool)
        self._router.register_module(voyager_tool)
        self._router.register_module(widget_awareness_tool)
        self._router.register(
            name="delegate_complex_task",
            description=(
                "Delegate a complex multi-step task to ADK specialists and "
                "return their consolidated response."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to delegate to ADK specialists",
                    }
                },
                "required": ["task"],
            },
            handler=self._delegate_complex_task,
            latency_tier="p95_sub_2s",
        )

        # Connect Hive to tools via Canonical Handover Protocol
        self._handoff_protocol = create_handoff_protocol(
            self._hive, self._session_restart
        )
        self._router.register_module(self._handoff_protocol)
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

        # Optimization: Drain the outgoing audio queue to prevent stale audio playback
        # This ensures immediate silence when the user interrupts.
        while not self._audio_out.empty():
            try:
                self._audio_out.get_nowait()
                self._audio_out.task_done()
            except asyncio.QueueEmpty:
                break

        # Panic Threshold: If input is extremely loud (>0.8), stop immediately
        # regardless of classification. Cognitive Guard: If it's a hard signal
        # but classified as non-speech, it's likely noise. We duck instead of
        # stop to maintain Aether's "presence".
        if (is_hard and stype not in ("thinking", "breathing", "void")) or rms > 0.8:
            logger.info(
                "⚡ Hard Barge-in (Speech detected, RMS: %.2f) — Stopping playback.",
                rms,
            )
            self._playback.interrupt()

    async def _execute_adk_task(self, task: str) -> str:
        response_text = ""
        async for event in self._adk_runner.run_async(task):
            if event.is_final_response():
                response_text = event.text
        return response_text

    async def _handle_complex_task(self, user_message: str) -> str:
        """
        Processes complex multi-step tasks using Google ADK orchestration.
        Delegates to specialized agents (Architect/Debugger) as needed.
        """
        logger.info("🧠 ADK: Orchestrating complex task: %s", user_message)
        response_text = await self._execute_adk_task(user_message)
        if (
            response_text
            and self._session
            and getattr(self._session, "_session", None) is not None
        ):
            logger.info("✅ ADK: Task complete, injecting response.")
            await self._session._session.send_realtime_input(
                parts=[types.Part.from_text(response_text)]
            )
        return response_text

    async def _delegate_complex_task(self, task: str, **kwargs) -> dict:
        response_text = await self._execute_adk_task(task)
        if not response_text:
            return {"status": "error", "message": "No response from ADK."}
        return {"status": "success", "response": response_text}

    def _on_affective_data(self, features: ParalinguisticFeatures) -> None:
        """Handle incoming affective metrics from the capture layer."""
        if self._firebase.is_connected:
            self._run_background_task(self._firebase.log_affective_metrics(features))

        # Phase 4: Proactive Intervention Trigger
        # Check if frustration levels warrant a system intervention
        valence = getattr(features, "valence", 0.0)
        arousal = getattr(features, "arousal", 0.0)

        if self._proactive_engine.should_intervene(valence, arousal):
            self._run_background_task(self._trigger_intervention())

        # UI Broadcast: Advanced Affective Metrics
        self._run_background_task(
            self._gateway.broadcast(
                "affective_score",
                {
                    "frustration": (1.0 - features.engagement_score)
                    * (features.rms_variance / 500.0),
                    "valence": features.engagement_score,
                    "arousal": features.rms_variance / 500.0,
                    "pitch": features.pitch_estimate,
                    "rate": features.speech_rate,
                    "zen_mode": features.zen_mode,
                },
            )
        )

    def _on_agent_handover(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Broadcasts a neural handover event to the UI."""
        logger.info(f"Broadcast: Neural Handover [{from_agent}] -> [{to_agent}]")
        galaxy_id = str((payload or {}).get("galaxy_id", "Genesis"))
        if self._gateway:
            handover_id = f"handover-{int(datetime.now().timestamp())}"
            self._run_background_task(
                self._emit_cinematic_handover_events(
                    handover_id=handover_id,
                    from_agent=from_agent,
                    to_agent=to_agent,
                    task=task,
                    galaxy_id=galaxy_id,
                )
            )
            self._run_background_task(
                self._gateway.broadcast(
                    "neural_event",
                    {
                        "id": handover_id,
                        "fromAgent": from_agent,
                        "toAgent": to_agent,
                        "task": task,
                        "status": "completed",
                        "galaxy_id": galaxy_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            )

    async def _emit_cinematic_handover_events(
        self,
        handover_id: str,
        from_agent: str,
        to_agent: str,
        task: str,
        galaxy_id: str = "Genesis",
    ) -> None:
        if not self._gateway:
            return

        now_iso = datetime.now().isoformat()
        protocol_version = 1

        await self._gateway.broadcast(
            "workspace_state",
            {
                "workspace_galaxy": galaxy_id,
                "focus_agent": to_agent,
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )
        await self._gateway.broadcast(
            "avatar_state",
            {
                "avatar_state": "EXECUTING",
                "reason": f"Handover {from_agent} -> {to_agent}",
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )
        await self._gateway.broadcast(
            "task_pulse",
            {
                "task_id": handover_id,
                "phase": "COMPLETED",
                "action": f"handover_{from_agent.lower()}_to_{to_agent.lower()}",
                "vibe": "success",
                "thought": f"{to_agent} received and completed handover task.",
                "avatar_state": "EUREKA",
                "avatar_target": to_agent,
                "intensity": 0.82,
                "latency_ms": 120,
                "galaxy_id": galaxy_id,
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )
        await self._gateway.broadcast(
            "task_timeline_item",
            {
                "task_id": handover_id,
                "title": "Handover Completed",
                "detail": f"{from_agent} delegated '{task}' to {to_agent}",
                "status": "completed",
                "galaxy_id": galaxy_id,
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )

    async def _emit_rollback_event(
        self,
        handover_id: str,
        from_agent: str,
        to_agent: str,
        reason: str,
        galaxy_id: str = "Genesis",
    ) -> None:
        """Emit cinematic events for handover rollback.

        Args:
            handover_id: Handover identifier
            from_agent: Source agent name
            to_agent: Target agent name
            reason: Reason for rollback
            galaxy_id: Galaxy identifier
        """
        if not self._gateway:
            return

        now_iso = datetime.now().isoformat()
        protocol_version = 1

        # Emit FAILED task_pulse
        await self._gateway.broadcast(
            "task_pulse",
            {
                "task_id": handover_id,
                "phase": "FAILED",
                "action": f"rollback_{to_agent.lower()}_to_{from_agent.lower()}",
                "vibe": "caution",
                "thought": f"Rollback triggered: {reason}",
                "avatar_state": "ERROR",
                "avatar_target": from_agent,
                "intensity": 0.9,
                "latency_ms": 80,  # Fast rollback target
                "galaxy_id": galaxy_id,
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )

        # Emit timeline item
        await self._gateway.broadcast(
            "task_timeline_item",
            {
                "task_id": handover_id,
                "title": "Rollback Executed",
                "detail": f"Failed handover rolled back: {reason}",
                "status": "failed",
                "galaxy_id": galaxy_id,
                "protocol_version": protocol_version,
                "timestamp": now_iso,
            },
        )

        logger.warning(
            "🔄 Rollback emitted for handover %s: %s -> %s (%s)",
            handover_id,
            from_agent,
            to_agent,
            reason,
        )

    async def _emit_workspace_event(
        self, event_type: str, payload: dict[str, Any]
    ) -> None:
        if not self._gateway:
            return
        await self._gateway.broadcast(event_type, payload)

    async def _trigger_intervention(self) -> None:
        """
        Injects a proactive context update into the Gemini session
        when the user is frustrated.
        """
        empathy_msg = self._proactive_engine.generate_empathetic_message()
        tools = await self._proactive_agent.get_investigation_tools()
        tool_names = [t["tool"] for t in tools]

        system_note = (
            f"SYSTEM_ALERT: High user frustration detected. "
            f"Suggested Action: {empathy_msg} "
            f"Available Diagnostic Tools: {tool_names}"
        )

        logger.info("🚨 Proactive Intervention: %s", system_note)

        # Inject into session so Gemini knows to speak/act
        if hasattr(self._session, "send_text"):
            await self._session.send_text(system_note)

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

    def _on_package_change(self, name: str, package: Optional[AthPackage]) -> None:
        """Handle dynamic package loading/unloading."""
        if package:
            logger.info("Hot-Reloading package: %s", name)
        else:
            logger.info("Unloading package: %s", name)

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

            logger.info("✦ System Initialized. Launching concurrent core tasks...")

            async with asyncio.TaskGroup() as tg:
                # 1. Start Peripheral IO
                tg.create_task(self._capture.run(), name="audio-capture")
                tg.create_task(self._playback.run(), name="audio-playback")

                # 2. Start the Gateway (This now owns the Gemini session loop)
                tg.create_task(self._gateway.run(), name="gateway")

                # 3. Start Administrative & Proactive tasks
                tg.create_task(self._admin_sync_loop(), name="admin-sync")
                tg.create_task(self._codex.start(), name="codex-bridge")

                # 4. Wait for shutdown signal
                await self._shutdown_event.wait()
                logger.info("✦ Shutdown event received: Stopping core tasks...")

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

    async def _update_admin_sessions(self) -> None:
        """Update recent sessions from Firestore."""
        if not (self._firebase.is_connected and self._firebase._db):
            return

        try:
            query = (
                self._firebase._db.collection("sessions")
                .order_by("started_at", direction="DESCENDING")
                .limit(10)
            )
            sessions = []
            async for doc in query.stream():
                if d := doc.to_dict():
                    d["id"] = doc.id
                    sessions.append(d)
            SHARED_STATE["sessions"] = sessions
        except Exception as e:
            logger.debug("Session sync error: %s", e)

    async def _update_admin_synapse(self, path: str) -> None:
        """Update L2 Synapse status from local heartbeat file."""
        if not os.path.exists(path):
            return

        try:
            import json

            async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                SHARED_STATE["synapse"] = json.loads(content)
        except Exception as e:
            logger.debug("Synapse sync error: %s", e)

    async def _admin_sync_loop(self) -> None:
        """Background task to continually update Admin API shared state."""
        synapse_path = os.path.expanduser("~/.aetheros/synapse/heartbeat.ath")
        while True:
            try:
                await self._update_admin_sessions()
                await self._update_admin_synapse(synapse_path)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.debug("Admin sync overall error: %s", e)

            await asyncio.sleep(2.0)

    async def _shutdown(self) -> None:
        """Graceful shutdown sequence."""
        logger.info("Starting graceful shutdown...")

        # Stop in reverse order: capture first, then processor, then output
        await self._capture.stop()
        await self._session.stop()
        await self._codex.stop()
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
