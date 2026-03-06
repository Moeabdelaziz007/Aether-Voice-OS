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
from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, Optional

if TYPE_CHECKING:
    from core.infra.transport.gateway import AetherGateway
    from core.tools.router import ToolRouter

from google import genai
from google.genai import types

from core.ai.agents.proactive import VisionPulseAgent
from core.ai.handover_protocol import HandoverContext, HandoverStatus
from core.ai.thalamic import ThalamicGate
from core.demo.fallback import DemoFallback
from core.identity.package import SoulManifest
from core.infra.config import AIConfig
from core.audio.telemetry import (
    log_output_queue_chunk_action,
    log_output_queue_pressure_transition,
)
from core.infra.telemetry import (
    record_usage,
)  # Import record_usage from telemetry module

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
        audio_out_queue: asyncio.Queue[bytes | dict[str, object]],
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
        self._pressure_tier: Literal["normal", "pressure", "critical"] = "normal"

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
        system_instruction = self._build_system_instruction()

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
                    # ── Handle Usage Metadata (Cost Tracking) ────────
                    self._handle_usage(response)

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
                                self._enqueue_output_audio_chunk(part.inline_data.data)
                                # UI Broadcast: Speaking state
                                asyncio.create_task(
                                    self._gateway.broadcast(
                                        "engine_state", {"state": "SPEAKING"}
                                    )
                                )

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

    def _handle_usage(self, response: types.LiveConnectResponse) -> None:
        """Extract and record token usage from the response."""
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count or 0
            completion_tokens = usage.candidates_token_count or 0
            if prompt_tokens > 0 or completion_tokens > 0:
                record_usage(
                    session_id=str(id(self)),
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model=self._config.model.value,
                )

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
        # UI Broadcast: Thinking state
        asyncio.create_task(
            self._gateway.broadcast("engine_state", {"state": "THINKING"})
        )

        tasks = []
        for fc in calls:
            if self._scheduler:
                self._scheduler.on_tool_start(fc.name)
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

            # --- Gateway Tool Result Broadcast ---
            asyncio.create_task(
                self._gateway.broadcast(
                    "tool_result",
                    {
                        "tool_name": fc.name,
                        "result": str(result.get("result", result))
                        if isinstance(result, dict)
                        else str(result),
                        "status": "failed"
                        if isinstance(result, dict) and "error" in result
                        else "success",
                        "code": result.get("x-a2a-status")
                        if isinstance(result, dict)
                        else None,
                    },
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

            if self._scheduler:
                self._scheduler.on_tool_end(fc.name)

        # 4. Final step: Send all responses back in a single turn
        try:
            await session.send_tool_response(function_responses)
            logger.info(
                "✓ Parallel Brain Cycle Complete: %d results sent",
                len(function_responses),
            )
        except Exception as exc:
            logger.error("Failed to send parallel tool responses: %s", exc)


    def _queue_capacity(self) -> int:
        return max(1, int(getattr(self._out_queue, "maxsize", 0) or 1))

    def _current_pressure_tier(self) -> Literal["normal", "pressure", "critical"]:
        utilization = self._out_queue.qsize() / self._queue_capacity()
        audio_cfg = getattr(self._gateway, "_audio_config", None)
        high = getattr(audio_cfg, "output_queue_high_watermark", 0.7)
        critical = getattr(audio_cfg, "output_queue_critical_watermark", 0.9)
        if utilization >= critical:
            return "critical"
        if utilization >= high:
            return "pressure"
        return "normal"

    def _emit_pressure_transition(self, next_tier: Literal["normal", "pressure", "critical"]) -> None:
        if next_tier == self._pressure_tier:
            return
        audio_cfg = getattr(self._gateway, "_audio_config", None)
        high = getattr(audio_cfg, "output_queue_high_watermark", 0.7)
        critical = getattr(audio_cfg, "output_queue_critical_watermark", 0.9)
        log_output_queue_pressure_transition(
            session_id=str(id(self)),
            previous_tier=self._pressure_tier,
            next_tier=next_tier,
            queue_size=self._out_queue.qsize(),
            queue_capacity=self._queue_capacity(),
            high_watermark=high,
            critical_watermark=critical,
        )
        self._pressure_tier = next_tier

    def _safe_put_outbound(self, payload: bytes | dict[str, object]) -> bool:
        try:
            self._out_queue.put_nowait(payload)
            return True
        except asyncio.QueueFull:
            try:
                self._out_queue.get_nowait()
            except asyncio.QueueEmpty:
                return False
            try:
                self._out_queue.put_nowait(payload)
                return True
            except asyncio.QueueFull:
                return False

    def _enqueue_output_audio_chunk(self, audio_chunk: bytes) -> None:
        tier = self._current_pressure_tier()
        self._emit_pressure_transition(tier)

        queue_size = self._out_queue.qsize()
        queue_capacity = self._queue_capacity()

        if tier == "normal":
            self._safe_put_outbound(audio_chunk)
            return

        if tier == "pressure":
            trimmed = audio_chunk[: max(2, int(len(audio_chunk) * 0.75))]
            dropped_chunks = 0
            if self._out_queue.full():
                try:
                    self._out_queue.get_nowait()
                    dropped_chunks = 1
                except asyncio.QueueEmpty:
                    dropped_chunks = 0
            self._safe_put_outbound(trimmed)
            log_output_queue_chunk_action(
                session_id=str(id(self)),
                action="coalesce_trim",
                tier=tier,
                queue_size=queue_size,
                queue_capacity=queue_capacity,
                chunk_bytes=len(trimmed),
                dropped_chunks=dropped_chunks,
            )
            return

        # critical tier: drop chunk and insert marker so playback can smooth
        self._output_queue_drops += 1
        if hasattr(self._gateway, "metrics"):
            metrics = self._gateway.metrics
            metrics["gemini_output_queue_drops"] = metrics.get("gemini_output_queue_drops", 0) + 1

        marker = {"type": "pressure_marker", "reason": "critical_drop", "fill_ms": 30}
        self._safe_put_outbound(marker)
        log_output_queue_chunk_action(
            session_id=str(id(self)),
            action="drop_with_marker",
            tier=tier,
            queue_size=queue_size,
            queue_capacity=queue_capacity,
            chunk_bytes=len(audio_chunk),
            dropped_chunks=1,
        )

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

    # ── Deep Handover Protocol Methods ──

    def _build_system_instruction(self) -> str:
        """
        Build the system instruction with soul-specific and handover context.

        Merges:
        1. Base system instruction from config
        2. Soul persona and expertise
        3. Injected handover context (if any)

        Returns:
            Complete system instruction string
        """
        # Start with base instruction
        instruction_parts = []

        # Add soul persona if available
        if self._soul:
            # Normalize: handle both AthPackage and SoulManifest
            manifest = (
                self._soul.manifest if hasattr(self._soul, "manifest") else self._soul
            )
            expertise = getattr(manifest, "expertise", {})
            persona = getattr(manifest, "persona", "An Aether Agent")

            soul_instruction = f"{persona}\n\nPrimary Domain: {expertise}"
            instruction_parts.append(soul_instruction)
            self._soul_instruction_cache = soul_instruction
            logger.info(
                "A2A [SESSION] Applying Expert Soul: %s",
                getattr(manifest, "name", "Unknown"),
            )

        # Add handover context if injected
        if self._injected_handover_context:
            handover_section = self._format_handover_context_for_instruction()
            if handover_section:
                instruction_parts.append(handover_section)
                logger.info(
                    "A2A [SESSION] Injected handover context: %s",
                    self._injected_handover_context.handover_id,
                )

        # Add base system instruction
        if self._config.system_instruction:
            instruction_parts.append(self._config.system_instruction)

        # 4. Neural Proactive Grounding (Cortex)
        if self._scheduler:
            instruction_parts.append(self._scheduler.get_grounding_context())

        # Join with clear separators
        return "\n\n---\n\n".join(instruction_parts)

    def _format_handover_context_for_instruction(self) -> str:
        """
        Format the injected handover context as a system instruction section.

        Returns:
            Formatted handover context string
        """
        if not self._injected_handover_context:
            return ""

        ctx = self._injected_handover_context
        parts = ["# HANDOVER CONTEXT"]

        # Basic info
        parts.append(f"Handover ID: {ctx.handover_id}")
        parts.append(f"From: {ctx.source_agent} → To: {ctx.target_agent}")
        parts.append(f"Task: {ctx.task}")

        # Task tree
        if ctx.task_tree:
            parts.append("\n## Task Tree")
            for node in ctx.task_tree:
                status_icon = "✓" if node.status == "completed" else "○"
                parts.append(f"{status_icon} {node.description}")

        # Working memory
        if ctx.working_memory and ctx.working_memory.short_term:
            parts.append("\n## Working Memory")
            for key, value in ctx.working_memory.short_term.items():
                parts.append(f"- {key}: {value}")

        # Intent confidence
        if ctx.intent_confidence:
            parts.append("\n## Confidence")
            parts.append(f"Score: {ctx.intent_confidence.confidence_score:.2%}")
            parts.append(f"Reasoning: {ctx.intent_confidence.reasoning}")

        # Code context
        if ctx.code_context:
            parts.append("\n## Code Context")
            if ctx.code_context.files_modified:
                parts.append(
                    f"Modified files: {', '.join(ctx.code_context.files_modified)}"
                )
            if ctx.code_context.language:
                parts.append(f"Language: {ctx.code_context.language}")
            if ctx.code_context.framework:
                parts.append(f"Framework: {ctx.code_context.framework}")

        # Recent conversation (last 5 entries)
        if ctx.conversation_history:
            parts.append("\n## Recent Conversation")
            for entry in ctx.conversation_history[-5:]:
                parts.append(f"[{entry.speaker}]: {entry.message[:100]}...")

        # History
        if ctx.history:
            parts.append("\n## Action History")
            for entry in ctx.history[-5:]:
                parts.append(f"- {entry}")

        return "\n".join(parts)

    def inject_handover_context(self, context: HandoverContext) -> bool:
        """
        Inject a handover context into the session.

        This merges the handover context into the system instruction,
        allowing the receiving agent to have full context awareness.

        Args:
            context: The handover context to inject

        Returns:
            True if injection was successful
        """
        try:
            self._injected_handover_context = context

            # Add acknowledgment entry
            ack_id = f"ack-{context.handover_id}"
            self._handover_acknowledgments[ack_id] = datetime.now().isoformat()

            # Add acknowledgment to context
            context.add_conversation_entry(
                speaker=context.target_agent,
                message=(
                    f"Handover acknowledged by {context.target_agent}. "
                    f"Ready to proceed."
                ),
                metadata={
                    "type": "handover_acknowledgment",
                    "acknowledgment_id": ack_id,
                    "session_id": id(self),
                },
            )

            logger.info(
                "A2A [SESSION] Handover context injected: %s (Task: %s)",
                context.handover_id,
                context.task[:50],
            )

            return True

        except Exception as e:
            logger.error("Failed to inject handover context: %s", e)
            return False

    def clear_handover_context(self) -> None:
        """Clear the injected handover context."""
        if self._injected_handover_context:
            logger.info(
                "A2A [SESSION] Clearing handover context: %s",
                self._injected_handover_context.handover_id,
            )
            self._injected_handover_context = None

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
        """
        Complete the handover acknowledgment protocol.

        Args:
            handover_id: The handover ID
            success: Whether the handover was successful
            message: Optional completion message

        Returns:
            True if completion was recorded
        """
        context = self._injected_handover_context
        if not context or context.handover_id != handover_id:
            logger.warning(
                "Cannot complete handover acknowledgment: context mismatch or not found"
            )
            return False

        # Update context status
        if success:
            context.update_status(HandoverStatus.COMPLETED)
        else:
            context.update_status(HandoverStatus.FAILED)

        # Add completion entry
        context.add_conversation_entry(
            speaker=context.target_agent,
            message=message or f"Handover {'completed' if success else 'failed'}",
            metadata={
                "type": "handover_completion",
                "success": success,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(
            "A2A [SESSION] Handover acknowledgment completed: %s (success=%s)",
            handover_id,
            success,
        )

        return True

    def export_handover_state(self) -> Dict[str, Any]:
        """
        Export the current handover state for persistence.

        Returns:
            Dictionary with handover state
        """
        return {
            "has_active_handover": self._injected_handover_context is not None,
            "handover_id": (
                self._injected_handover_context.handover_id
                if self._injected_handover_context
                else None
            ),
            "acknowledgments": self._handover_acknowledgments.copy(),
            "timestamp": datetime.now().isoformat(),
        }

    def restore_handover_state(self, state: Dict[str, Any]) -> bool:
        """
        Restore handover state from a persisted state dictionary.

        Args:
            state: The state dictionary to restore from

        Returns:
            True if restoration was successful
        """
        try:
            self._handover_acknowledgments = state.get("acknowledgments", {})
            logger.info(
                "Restored handover acknowledgments: %d",
                len(self._handover_acknowledgments),
            )
            return True
        except Exception as e:
            logger.error("Failed to restore handover state: %s", e)
            return False
