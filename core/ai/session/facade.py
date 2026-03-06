"""
Aether Voice OS — Gemini Live Session.

Manages the bidirectional audio connection to Gemini's Live API.
This is the AI "brain" of Aether — the WhisperFlow-style pipeline
powered by Gemini's native audio instead of Whisper + TTS.

Architecture:
  - send_loop: reads from audio_in_queue → sends to Gemini
  - receive_loop: receives from Gemini → pushes to audio_out_queue
  - tool_call handling: dispatches function calls via ToolRouter
  - Interruption: when Gemini signals barge-in, we drain the output queue

Uses the official `google-genai` SDK (not google-generativeai).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from core.infra.transport.gateway import AetherGateway
    from core.tools.router import ToolRouter

from google import genai
from google.genai import types

from core.ai.agents.proactive import VisionPulseAgent
from core.ai.handover_protocol import HandoverContext
from core.ai.thalamic import ThalamicGate
from core.demo.fallback import DemoFallback
from core.identity.package import SoulManifest
from core.infra.config import AIConfig
from core.utils.errors import AIConnectionError, AISessionExpiredError

from .config_builder import build_session_config
from .handover_bridge import (
    build_system_instruction,
    clear_handover_context,
    complete_handover_acknowledgment,
    export_handover_state,
    format_handover_context_for_instruction,
    inject_handover_context,
    restore_handover_state,
)
from .io_loops import drain_output, handle_usage, receive_loop, send_loop
from .tool_dispatch import handle_tool_call

logger = logging.getLogger(__name__)


class GeminiLiveSession:
    """
    Bidirectional audio session with Gemini Live API.

    This replaces the WhisperFlow pattern of:
      Whisper STT → LLM → TTS
    with a single unified model that handles:
      Audio In → Understanding + Thinking → Audio Out
    in one WebSocket connection, with ~300ms latency.
    """

    def __init__(
        self,
        config: AIConfig,
        audio_in_queue: asyncio.Queue[dict[str, object]],
        audio_out_queue: asyncio.Queue[bytes],
        gateway: "AetherGateway",
        on_interrupt: Optional[Callable] = None,
        on_tool_call: Optional[Callable] = None,
        tool_router: Optional["ToolRouter"] = None,
        soul_manifest: Optional["SoulManifest"] = None,
        scheduler: Optional[Any] = None,
    ) -> None:
        self._config = config
        self._soul = soul_manifest
        self._in_queue = audio_in_queue
        self._out_queue = audio_out_queue
        self._gateway = gateway
        self._on_interrupt = on_interrupt
        self._on_tool_call = on_tool_call
        self._tool_router = tool_router
        self._scheduler = scheduler
        if self._scheduler:
            self._scheduler.set_echo_callback(self._inject_echo)
        self._client: Optional[genai.Client] = None
        self._session = None
        self._running = False

        # Telemetry counters (best-effort; exposed via gateway.metrics when possible)
        self._output_queue_drops = 0

        self._frame_buffer: list[
            tuple[float, bytes]
        ] = []  # Rolling history of screenshots
        self._max_frames = 10  # ~10 seconds of visual history
        self._active_handoffs: dict[str, dict] = {}  # A2A V3 Handoff Tracking

        # Vision Pulse Agent (Phase 6)
        self._vision_pulse = VisionPulseAgent()
        self._vision_task: Optional[asyncio.Task] = None

        # Deep Handover Protocol integration
        self._injected_handover_context: Optional[HandoverContext] = None
        self._handover_acknowledgments: Dict[str, str] = {}
        self._soul_instruction_cache: Optional[str] = None
        self._start_time: datetime = datetime.now()

    def _build_session_config(self) -> types.LiveConnectConfig:
        """Build the LiveConnectConfig with tool declarations."""
        return build_session_config(self)

    async def connect(self) -> None:
        """Establish the Gemini Live session."""
        try:
            self._client = genai.Client(
                api_key=self._config.api_key,
                http_options={"api_version": self._config.api_version},
            )
            logger.info(
                "Connecting to Gemini Live: model=%s, api_version=%s",
                self._config.model.value,
                self._config.api_version,
            )
        except Exception as exc:
            raise AIConnectionError(
                f"Failed to create Gemini client: {exc}",
                cause=exc,
            ) from exc

    async def run(self) -> None:
        """
        Main session lifecycle.

        Opens the Live connection and runs send/receive loops
        concurrently via TaskGroup. If either loop crashes,
        both are cancelled (structured concurrency).
        """
        if not self._client:
            raise AIConnectionError("Call connect() before run()")

        config = self._build_session_config()
        self._running = True

        try:
            async with self._client.aio.live.connect(
                model=self._config.model.value,
                config=config,
            ) as session:
                self._session = session
                logger.info("✦ Gemini Live session established")

                # Wire in Thalamic Gate V2
                try:
                    self._thalamic_gate = ThalamicGate(session)
                    self._demo_fallback = DemoFallback()
                    await self._thalamic_gate.start()
                except Exception as e:
                    logger.error("Failed to wire Thalamic Gate: %s", e)

                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self._send_loop(session))
                    tg.create_task(self._receive_loop(session))

                    # ── Proactive Vision Pulse ──────────────────────
                    # Periodic screenshots injected into the stream
                    # for real-time visual context.
                    if self._config.enable_proactive_vision:
                        tg.create_task(self._proactive_vision_loop(session))

                    # ── Architecture of Silence (Backchanneling) ────
                    tg.create_task(self._backchannel_loop(session))

        except Exception as exc:
            if isinstance(exc, asyncio.CancelledError):
                logger.info("Session cancelled (shutdown)")
            else:
                logger.error("Session error: %s", exc, exc_info=True)
                raise AISessionExpiredError(
                    f"Gemini session terminated: {exc}",
                    cause=exc,
                ) from exc
        finally:
            if hasattr(self, "_thalamic_gate"):
                self._thalamic_gate.stop()
            self._session = None
            self._running = False
            logger.info("Gemini Live session closed")

    async def _send_loop(self, session) -> None:
        await send_loop(self, session)

    async def _backchannel_loop(self, session) -> None:
        """
        Monitors Silence Architecture signals.
        If user is 'Thinking' or 'Breathing', injects an empathetic
        text part to trigger a model backchannel.
        """
        from core.audio.state import audio_state

        logger.info("Backchannel loop active (Acoustic Empathy enabled)")

        thinking_streak = 0
        while self._running:
            await asyncio.sleep(0.2)

            # Reset empathy if model is currently playing audio
            if audio_state.is_playing:
                thinking_streak = 0
                continue

            stype = audio_state.silence_type
            if stype in ("thinking", "breathing"):
                thinking_streak += 1
                if thinking_streak >= 25:  # ~5 seconds of cognitive load
                    logger.info(
                        "🧠 Empathy Trigger: User is thinking. Sending backchannel cue."
                    )
                    try:
                        # Sending a tiny text hint can encourage Gemini to
                        # give a soft vocal affirmative without fully taking the turn.
                        await session.send_realtime_input(
                            parts=[
                                types.Part.from_text(text="[user thinking, soft 'Mhm']")
                            ]
                        )
                        thinking_streak = 0  # Reset to avoid spamming
                    except Exception as e:
                        logger.debug("Backchannel send failed: %s", e)
            else:
                thinking_streak = 0

    async def _receive_loop(self, session) -> None:
        await receive_loop(self, session)

    def _handle_usage(self, response: types.LiveConnectResponse) -> None:
        handle_usage(self, response)

    async def _handle_tool_call(self, session, tool_call) -> None:
        await handle_tool_call(self, session, tool_call)

    def _drain_output(self) -> None:
        drain_output(self)

    async def stop(self) -> None:
        """Signal the session to stop."""
        self._running = False
        logger.info("Gemini session stop requested")

    async def send_text(self, text: str) -> bool:
        """
        Injects a text part into the active realtime session.
        This allows asynchronous context injection (e.g., from Codex).
        """
        if not hasattr(self, "_session") or not self._session:
            logger.warning("Cannot send text: No active session.")
            return False

        try:
            from google.genai import types
            await self._session.send_realtime_input(
                parts=[types.Part.from_text(text)]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send text to session: {e}")
            return False

    # ── Deep Handover Protocol Methods ──

    def _build_system_instruction(self) -> str:
        """Build the system instruction with soul/handover state."""
        return build_system_instruction(self)

    def _format_handover_context_for_instruction(self) -> str:
        """Format the injected handover context as system-instruction text."""
        return format_handover_context_for_instruction(self)

    def inject_handover_context(self, context: HandoverContext) -> bool:
        return inject_handover_context(self, context)

    def clear_handover_context(self) -> None:
        clear_handover_context(self)

    async def _inject_echo(self, echo: str) -> None:
        """Inject a 'thought echo' into the live stream to trigger vocalization."""
        if not self._session or not self._running:
            return

        logger.info("🔮 A2A [ECHO] Injecting thought: %s", echo)
        try:
            # We wrap the echo in a directive to ensure Gemini vocalizes it as a thought
            await self._session.send_realtime_input(
                parts=[types.Part.from_text(text=f"[thought: {echo}]")]
            )
        except Exception as e:
            logger.error("Echo injection failed: %s", e)

    def get_handover_acknowledgment(self, handover_id: str) -> Optional[str]:
        """
        Get the acknowledgment timestamp for a handover.

        Args:
            handover_id: The handover ID

        Returns:
            ISO timestamp of acknowledgment, or None if not acknowledged
        """
        ack_id = f"ack-{handover_id}"
        return self._handover_acknowledgments.get(ack_id)

    def is_handover_acknowledged(self, handover_id: str) -> bool:
        """
        Check if a handover has been acknowledged.

        Args:
            handover_id: The handover ID

        Returns:
            True if acknowledged
        """
        return self.get_handover_acknowledgment(handover_id) is not None

    def get_active_handover(self) -> Optional[HandoverContext]:
        """Get the currently active (injected) handover context."""
        return self._injected_handover_context

    def complete_handover_acknowledgment(
        self, handover_id: str, success: bool, message: str = ""
    ) -> bool:
        return complete_handover_acknowledgment(self, handover_id, success, message)

    def export_handover_state(self) -> Dict[str, Any]:
        return export_handover_state(self)

    def restore_handover_state(self, state: Dict[str, Any]) -> bool:
        return restore_handover_state(self, state)
