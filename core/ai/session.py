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
import json
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.tools.router import ToolRouter

from google import genai
from google.genai import types

from core.config import AIConfig
from core.errors import AIConnectionError, AISessionExpiredError

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
        on_interrupt: Optional[callable] = None,
        on_tool_call: Optional[callable] = None,
        tool_router: Optional["ToolRouter"] = None,
    ) -> None:
        self._config = config
        self._in_queue = audio_in_queue
        self._out_queue = audio_out_queue
        self._on_interrupt = on_interrupt
        self._on_tool_call = on_tool_call
        self._tool_router = tool_router
        self._client: Optional[genai.Client] = None
        self._session = None
        self._running = False

    def _build_session_config(self) -> types.LiveConnectConfig:
        """Build the LiveConnectConfig with tool declarations."""
        # Build tools list from router + Google Search grounding
        tools = []

        if self._tool_router and self._tool_router.count > 0:
            declarations = self._tool_router.get_declarations()
            tools.append(types.Tool(function_declarations=declarations))
            logger.info(
                "Session configured with %d tools: %s",
                len(declarations),
                self._tool_router.names,
            )

        # Google Search grounding — prevents hallucination on factual queries
        if self._config.enable_search_grounding:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
            logger.info("Google Search grounding enabled")

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=self._config.system_instruction,
            tools=tools,
        )

        # Advanced features (v1alpha)
        if self._config.enable_affective_dialog:
            config.enable_affective_dialog = True

        if self._config.proactive_audio:
            config.proactivity = {"proactive_audio": True}

        if self._config.thinking_budget is not None:
            config.thinking_config = types.ThinkingConfig(
                thinking_budget=self._config.thinking_budget,
            )

        return config

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

                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self._send_loop(session))
                    tg.create_task(self._receive_loop(session))

        except* Exception as eg:
            for exc in eg.exceptions:
                if isinstance(exc, asyncio.CancelledError):
                    logger.info("Session cancelled (shutdown)")
                else:
                    logger.error("Session error: %s", exc, exc_info=True)
                    raise AISessionExpiredError(
                        f"Gemini session terminated: {exc}",
                        cause=exc,
                    ) from exc
        finally:
            self._session = None
            self._running = False
            logger.info("Gemini Live session closed")

    async def _send_loop(self, session) -> None:
        """
        Reads PCM chunks from audio_in_queue and sends
        them to Gemini as realtime audio input.
        """
        logger.debug("Send loop started")
        frame_count = 0
        while self._running:
            try:
                msg = await asyncio.wait_for(
                    self._in_queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            try:
                await session.send_realtime_input(audio=msg)
                frame_count += 1
                if frame_count % 500 == 0:
                    logger.debug(
                        "Send loop: %d frames sent, in_queue=%d",
                        frame_count,
                        self._in_queue.qsize(),
                    )
            except Exception as exc:
                logger.error("Send error: %s", exc)
                if "closed" in str(exc).lower():
                    break

    async def _receive_loop(self, session) -> None:
        """
        Receives responses from Gemini and routes:
          - Audio chunks → output queue (speaker)
          - Tool calls → ToolRouter → tool response back to Gemini
          - Interruptions → drain output (barge-in)

        This is the neural switchboard of the entire system.
        """
        logger.debug("Receive loop started")
        while self._running:
            try:
                turn = session.receive()
                async for response in turn:
                    # ── Handle tool calls (function calling) ─────────
                    if response.tool_call:
                        await self._handle_tool_call(session, response.tool_call)
                        continue

                    # ── Extract audio from model response ────────────
                    if (
                        response.server_content
                        and response.server_content.model_turn
                    ):
                        for part in response.server_content.model_turn.parts:
                            if (
                                part.inline_data
                                and isinstance(part.inline_data.data, bytes)
                            ):
                                # Overflow protection: drop oldest if queue is full
                                if self._out_queue.full():
                                    try:
                                        self._out_queue.get_nowait()
                                        logger.debug("Output queue overflow — dropped oldest chunk")
                                    except asyncio.QueueEmpty:
                                        pass
                                self._out_queue.put_nowait(
                                    part.inline_data.data
                                )

                    # ── Handle barge-in / interruption ────────────────
                    if (
                        response.server_content
                        and response.server_content.interrupted
                    ):
                        logger.info("⚡ Barge-in detected — draining output")
                        self._drain_output()
                        if self._on_interrupt:
                            self._on_interrupt()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                if "closed" in str(exc).lower():
                    logger.info("Receive stream closed")
                    break
                logger.error("Receive error: %s", exc, exc_info=True)
                await asyncio.sleep(0.5)  # Brief backoff before retry

    async def _handle_tool_call(self, session, tool_call) -> None:
        """
        Handle a Gemini function call by dispatching to the ToolRouter.

        Flow:
          1. Gemini emits tool_call with function_calls list
          2. We dispatch each to the router
          3. We send tool_response back to Gemini
          4. Gemini speaks the confirmation (audio stream stays open)
        """
        if not self._tool_router:
            logger.warning("Tool call received but no ToolRouter configured")
            return

        function_responses = []

        for fc in tool_call.function_calls:
            logger.info(
                "🧠 Function call: %s(%s)",
                fc.name,
                json.dumps(fc.args, default=str)[:200] if fc.args else "{}",
            )

            # Dispatch to the router
            result = await self._tool_router.dispatch(fc)

            function_responses.append(
                types.FunctionResponse(
                    name=fc.name,
                    response=result,
                )
            )

            # Fire analytics callback
            if self._on_tool_call:
                try:
                    await self._on_tool_call(fc.name, fc.args, result)
                except Exception:
                    pass  # Analytics must never break the pipeline

        # Send all responses back to Gemini
        try:
            await session.send_tool_response(function_responses)
            logger.info(
                "✓ Sent %d tool response(s) back to Gemini",
                len(function_responses),
            )
        except Exception as exc:
            logger.error("Failed to send tool response: %s", exc)

    def _drain_output(self) -> None:
        """Drain the output queue on interruption (instant silence)."""
        count = 0
        while not self._out_queue.empty():
            try:
                self._out_queue.get_nowait()
                count += 1
            except asyncio.QueueEmpty:
                break
        if count:
            logger.debug("Drained %d audio chunks from output queue", count)

    async def stop(self) -> None:
        """Signal the session to stop."""
        self._running = False
        logger.info("Gemini session stop requested")
