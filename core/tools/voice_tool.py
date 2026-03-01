"""
Aether Voice OS — Voice Tool.

Exposes the voice pipeline as a callable tool within the agent.
Compatible with ADK (Agent Development Kit) tool interfaces
and OpenClaw skill specifications.

This tool manages the full audio lifecycle:
  - Microphone capture (PyAudio → asyncio.Queue)
  - Gemini Live session (bidirectional WebSocket)
  - Speaker playback (asyncio.Queue → PyAudio)
  - Barge-in / interruption handling

Usage as a tool:
    tool = VoiceTool()
    await tool.setup(config)
    await tool.execute()       # starts listening + responding
    await tool.teardown()      # graceful cleanup
"""

from __future__ import annotations

import asyncio
import logging
import signal
from enum import Enum
from typing import Callable, Optional

from core.ai.session import GeminiLiveSession
from core.audio.capture import AudioCapture
from core.audio.playback import AudioPlayback
from core.infra.config import AetherConfig, load_config

logger = logging.getLogger(__name__)


class VoiceState(str, Enum):
    """Current state of the voice tool."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"
    STOPPED = "stopped"


class VoiceTool:
    """
    Voice interaction as an ADK-compatible tool.

    Lifecycle follows: setup → execute → teardown
    Compatible with OpenClaw skill registration.

    Events:
      on_state_change(old, new)  — state machine transitions
      on_transcript(text)        — when text is available
      on_error(exc)              — on non-fatal errors
    """

    NAME = "aether_voice"
    DESCRIPTION = (
        "Full-duplex voice interaction with Gemini Live. "
        "Captures microphone audio, streams to Gemini, "
        "and plays back AI responses through the speaker."
    )

    def __init__(
        self,
        config: Optional[AetherConfig] = None,
        on_state_change: Optional[Callable[[VoiceState, VoiceState], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        self._config = config
        self._state = VoiceState.IDLE
        self._on_state_change = on_state_change
        self._on_error = on_error

        # Pipeline components (created during setup)
        self._audio_in: Optional[asyncio.Queue] = None
        self._audio_out: Optional[asyncio.Queue] = None
        self._capture: Optional[AudioCapture] = None
        self._playback: Optional[AudioPlayback] = None
        self._session: Optional[GeminiLiveSession] = None
        self._shutdown_event: Optional[asyncio.Event] = None

    @property
    def state(self) -> VoiceState:
        """Current voice tool state."""
        return self._state

    @property
    def is_active(self) -> bool:
        """True if the tool is currently running."""
        return self._state in (
            VoiceState.LISTENING,
            VoiceState.PROCESSING,
            VoiceState.SPEAKING,
        )

    def _set_state(self, new_state: VoiceState) -> None:
        """Transition state with callback."""
        old = self._state
        self._state = new_state
        logger.debug("Voice state: %s → %s", old.value, new_state.value)
        if self._on_state_change:
            try:
                self._on_state_change(old, new_state)
            except Exception:
                logger.exception("State change callback error")

    # ── ADK Lifecycle ───────────────────────────────────────────

    async def setup(self, config: Optional[AetherConfig] = None) -> None:
        """
        Initialize all audio components.

        ADK Phase 1: Allocate resources, validate config.
        """
        self._set_state(VoiceState.INITIALIZING)

        self._config = config or self._config or load_config()

        # Pipeline queues
        self._audio_in = asyncio.Queue(maxsize=self._config.audio.mic_queue_max)
        self._audio_out = asyncio.Queue()

        # Components
        self._capture = AudioCapture(self._config.audio, self._audio_in)
        self._playback = AudioPlayback(self._config.audio, self._audio_out)
        self._session = GeminiLiveSession(
            self._config.ai,
            self._audio_in,
            self._audio_out,
            on_interrupt=self._handle_interrupt,
        )
        self._shutdown_event = asyncio.Event()

        logger.info("Voice tool initialized — ready to connect")

    async def execute(self) -> None:
        """
        Run the voice pipeline.

        ADK Phase 2: Begin full-duplex audio streaming.
        Blocks until shutdown is requested.
        """
        if not self._capture or not self._session or not self._playback:
            raise RuntimeError("Call setup() before execute()")

        # Register signal handlers for clean shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._request_shutdown)

        try:
            # Open audio devices
            await self._capture.start()
            await self._playback.start()

            # Connect to Gemini Live
            await self._session.connect()
            self._set_state(VoiceState.LISTENING)

            logger.info("═" * 50)
            logger.info("  AETHER VOICE TOOL — Active")
            logger.info("  Model: %s", self._config.ai.model.value)
            logger.info("  State: LISTENING")
            logger.info("═" * 50)

            # Run all tasks concurrently
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._capture.run(), name="voice-capture")
                tg.create_task(self._playback.run(), name="voice-playback")
                tg.create_task(self._session.run(), name="voice-session")
                tg.create_task(self._watch_shutdown(), name="voice-shutdown")

        except* KeyboardInterrupt:
            logger.info("Voice tool interrupted by user")
        except* Exception as eg:
            for exc in eg.exceptions:
                if not isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt)):
                    logger.error("Voice tool error: %s", exc, exc_info=True)
                    self._set_state(VoiceState.ERROR)
                    if self._on_error:
                        self._on_error(exc)
        finally:
            await self.teardown()

    async def teardown(self) -> None:
        """
        Graceful cleanup.

        ADK Phase 3: Release all resources.
        """
        logger.info("Voice tool shutting down...")
        if self._capture:
            await self._capture.stop()
        if self._session:
            await self._session.stop()
        if self._playback:
            await self._playback.stop()
        self._set_state(VoiceState.STOPPED)
        logger.info("Voice tool stopped cleanly")

    # ── Internal Handlers ───────────────────────────────────────

    def _handle_interrupt(self) -> None:
        """Handle barge-in from Gemini (user interrupted AI)."""
        if self._playback:
            self._playback.interrupt()
        self._set_state(VoiceState.LISTENING)
        logger.info("⚡ Barge-in: switched back to LISTENING")

    def _request_shutdown(self) -> None:
        """Signal the tool to stop."""
        logger.info("Shutdown requested")
        if self._shutdown_event:
            self._shutdown_event.set()

    async def _watch_shutdown(self) -> None:
        """Wait for shutdown signal, then cancel tasks."""
        if self._shutdown_event:
            await self._shutdown_event.wait()
        raise asyncio.CancelledError("Voice tool shutdown")

    # ── ADK Tool Interface ──────────────────────────────────────

    def to_adk_declaration(self) -> dict:
        """
        Return an ADK-compatible tool declaration.

        Can be registered with any ADK-based agent framework.
        """
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status"],
                        "description": "Voice tool action to perform",
                    }
                },
                "required": ["action"],
            },
        }

    async def handle_tool_call(self, action: str) -> dict:
        """
        Handle an incoming tool call from the agent.

        Args:
            action: "start", "stop", or "status"

        Returns:
            Tool result dict for the agent.
        """
        if action == "status":
            return {
                "state": self._state.value,
                "is_active": self.is_active,
            }
        elif action == "start":
            if not self.is_active:
                await self.setup(self._config)
                # Run in background — don't block the agent
                asyncio.create_task(self.execute())
            return {"state": self._state.value, "message": "Voice started"}
        elif action == "stop":
            self._request_shutdown()
            return {"state": self._state.value, "message": "Voice stopping"}
        else:
            return {"error": f"Unknown action: {action}"}


# ── Module-level integration for ToolRouter ─────────────────

_voice_tool: Optional[VoiceTool] = None


def set_voice_tool(tool: VoiceTool) -> None:
    """Inject the VoiceTool instance at startup."""
    global _voice_tool
    _voice_tool = tool


async def _voice_tool_handler(action: str = "status", **kwargs) -> dict:
    """Dispatch voice tool calls to the singleton."""
    if _voice_tool is None:
        return {"error": "Voice tool not initialized"}
    return await _voice_tool.handle_tool_call(action)


def get_tools() -> list[dict]:
    """
    Module-level tool registration.

    Called by ToolRouter.register_module() to auto-discover
    the voice control tool.
    """
    return [
        {
            "name": "aether_voice",
            "description": (
                "Control the voice pipeline. Actions: "
                "'start' to begin listening, "
                "'stop' to end the session, "
                "'status' to check current state."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status"],
                        "description": "Voice tool action to perform",
                    },
                },
                "required": ["action"],
            },
            "handler": _voice_tool_handler,
        },
    ]
