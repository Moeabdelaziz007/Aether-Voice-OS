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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.tools.router import ToolRouter

from google import genai
from google.genai import types

from core.config import AIConfig
from core.errors import AIConnectionError, AISessionExpiredError
from core.identity.package import SoulManifest

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
        soul_manifest: Optional["SoulManifest"] = None,
    ) -> None:
        self._config = config
        self._soul = soul_manifest
        self._in_queue = audio_in_queue
        self._out_queue = audio_out_queue
        self._on_interrupt = on_interrupt
        self._on_tool_call = on_tool_call
        self._tool_router = tool_router
        self._client: Optional[genai.Client] = None
        self._session = None
        self._running = False
        self._frame_buffer: list[tuple[float, bytes]] = (
            []
        )  # Rolling history of screenshots
        self._max_frames = 10  # ~10 seconds of visual history
        self._active_handoffs: dict[str, dict] = {}  # A2A V3 Handoff Tracking

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

        # ── Hive expert logic ──
        system_instruction = self._config.system_instruction
        if self._soul:
            expertise = (
                self._soul.manifest.expertise if hasattr(self._soul, "manifest") else {}
            )
            system_instruction = (
                f"{self._soul.persona}\n\n"
                f"Primary Domain: {expertise}\n\n"
                f"{system_instruction}"
            )
            logger.info("A2A [SESSION] Applying Expert Soul: %s", self._soul.name)

        # ── Voice Preference Mapping ──
        speech_config = None
        if (
            self._soul
            and hasattr(self._soul, "manifest")
            and self._soul.manifest.voice_id
        ):
            voice_name = self._soul.manifest.voice_id
            logger.info("A2A [SESSION] Applying Expert Voice: %s", voice_name)
            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=system_instruction,
            tools=tools,
            speech_config=speech_config,
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

                # Wire in Thalamic Gate V2
                try:
                    from core.ai.thalamic import ThalamicGate
                    from core.demo.fallback import DemoFallback

                    self._thalamic_gate = ThalamicGate(session)
                    self._demo_fallback = DemoFallback(self)
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
                        tg.create_task(self._vision_pulse_loop(session))

                    # ── Architecture of Silence (Backchanneling) ────
                    tg.create_task(self._backchannel_loop(session))

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
            if hasattr(self, "_thalamic_gate"):
                self._thalamic_gate.stop()
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
                msg = await asyncio.wait_for(self._in_queue.get(), timeout=1.0)
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

    async def _vision_pulse_loop(self, session) -> None:
        """
        Maintains a rolling buffer of screen frames (1s resolution) for Indexical Sync.
        Also sends proactive pulses every 10s or on Hard-Interrupt (Camera Pulse).
        """
        logger.info("Vision Pulse loop started (Reflex-Triggered Camera active)")
        import os
        import time

        from core.audio.state import audio_state
        from core.tools.camera_tool import camera_instance
        from core.tools.vision_tool import capture_screenshot

        last_proactive_pulse = 0
        while self._running:
            try:
                # 1 second resolution for the rolling buffer
                await asyncio.sleep(1.0)

                now = time.time()
                is_hard = audio_state.is_hard

                # ── Pulse 1: Screen Capture (Rolling Buffer) ──
                res = await capture_screenshot()
                if res.get("status") == "ok":
                    path = res["path"]
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            image_bytes = f.read()

                        self._frame_buffer.append((now, image_bytes))
                        if len(self._frame_buffer) > self._max_frames:
                            self._frame_buffer.pop(0)

                        # Proactive Pulse (10s)
                        if now - last_proactive_pulse > 10.0:
                            logger.debug(
                                "Proactive Vision: Sending screenshot to Gemini"
                            )
                            await session.send_realtime_input(
                                parts=[
                                    types.Part.from_bytes(
                                        data=image_bytes, mime_type="image/jpeg"
                                    )
                                ]
                            )
                            last_proactive_pulse = now

                        os.remove(path)

                # ── Pulse 2: Camera Capture (Hard Interrupt Grounding) ──
                if is_hard:
                    logger.info(
                        "📸 Camera Pulse: Capturing user reaction to hard-interrupt."
                    )
                    cam_bytes = camera_instance.capture_frame()
                    if cam_bytes:
                        await session.send_realtime_input(
                            parts=[
                                types.Part.from_bytes(
                                    data=cam_bytes, mime_type="image/jpeg"
                                )
                            ]
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Vision pulse failed: %s", e)

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
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            # 1. Handle Text Transcript
                            if part.text:
                                try:
                                    # Broadcast transcript segment directly to UI
                                    asyncio.create_task(
                                        self._gateway.broadcast(
                                            "transcript", {"text": part.text}
                                        )
                                    )
                                except Exception as e:
                                    logger.debug(
                                        "Failed to broadcast transcript: %s", e
                                    )

                            # 2. Handle Audio Output
                            if part.inline_data and isinstance(
                                part.inline_data.data, bytes
                            ):
                                # Overflow protection: drop oldest if queue is full
                                if self._out_queue.full():
                                    try:
                                        self._out_queue.get_nowait()
                                        logger.debug("Output queue overflow")
                                    except asyncio.QueueEmpty:
                                        pass
                                self._out_queue.put_nowait(part.inline_data.data)

                    # ── Handle barge-in / interruption ────────────────
                    if response.server_content and response.server_content.interrupted:
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

        Upgraded to PARALLEL execution via TaskGroup.
        """
        if not self._tool_router:
            logger.warning("Tool call received but no ToolRouter configured")
            return

        calls = tool_call.function_calls
        logger.info("🧠 Brain Dispatch: Executing %d calls in parallel", len(calls))

        # 1. Create dispatch tasks
        tasks = []
        for fc in calls:
            tasks.append(self._tool_router.dispatch(fc))

        # 2. Parallel Execution
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Process Responses
        function_responses = []
        for fc, result in zip(calls, results):
            if isinstance(result, Exception):
                logger.error("Tool %s failed: %s", fc.name, result)
                result = {"error": str(result), "status": "failed"}

            function_responses.append(
                types.FunctionResponse(
                    name=fc.name,
                    response=result,
                )
            )

            # --- Multimodal Vision Injection (if tool returns screenshot) ---
            if isinstance(result, dict) and "screenshot_path" in result:
                import os

                path = result["screenshot_path"]
                if os.path.exists(path):
                    try:
                        with open(path, "rb") as f:
                            image_bytes = f.read()
                        await session.send_realtime_input(
                            parts=[
                                types.Part.from_bytes(
                                    data=image_bytes, mime_type="image/jpeg"
                                )
                            ]
                        )
                        os.remove(path)
                    except Exception as e:
                        logger.error("Vision injection failed: %s", e)

            # Fire analytics
            if self._on_tool_call:
                asyncio.create_task(self._on_tool_call(fc.name, fc.args, result))

            # --- A2A Handoff State Injection ---
            if (
                fc.name == "delegate_to_agent"
                and result.get("status") == "handoff_initiated"
            ):
                handoff_id = result.get("handoff_id")
                self._active_handoffs[handoff_id] = {
                    "target": fc.args.get("target_agent_id"),
                    "task": fc.args.get("task_description"),
                    "timestamp": result.get("handoff_time"),
                }
                logger.info("A2A [STATE] Tracking handoff: %s", handoff_id)

        # 4. Final step: Send all responses back in a single turn
        try:
            await session.send_tool_response(function_responses)
            logger.info(
                "✓ Parallel Brain Cycle Complete: %d results sent",
                len(function_responses),
            )
        except Exception as exc:
            logger.error("Failed to send parallel tool responses: %s", exc)

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
