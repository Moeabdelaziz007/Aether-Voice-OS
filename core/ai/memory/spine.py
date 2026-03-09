"""
Aether Voice OS — The Neural Spine.

A distributed semantic memory layer that persists context across expert handovers
and serves as the central Nervous System for diagnostic traces.
Provides "Warm Cache" loading for new experts and allows the SRE Watchdog
to inject "Hidden System Prompts" during failures.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from core.infra.transport.bus import GlobalBus

logger = logging.getLogger(__name__)


class NeuralSpine:
    """
    Distributed Context & Autonomous SRE Cache.
    Maintains a Redis-backed sliding window of 'Interaction Frames'.
    """

    def __init__(self, bus: Optional[GlobalBus] = None, max_frames: int = 50):
        self._bus = bus
        self._max_frames = max_frames
        self._key = "neural_spine:frames"
        self._system_prompt_key = "neural_spine:system_prompt"
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start listening to GlobalBus for memory events."""
        if not self._bus or not self._bus.is_connected:
            logger.warning(
                "NeuralSpine: GlobalBus not available. Memory will not persist."
            )
            return

        self._running = True

        # Subscribe to tool results and AI learnings
        await self._bus.subscribe("frontend_events", self._handle_event)
        await self._bus.subscribe("tool_result", self._handle_tool_result)
        await self._bus.subscribe("ai_learning", self._handle_learning)

        logger.info("✦ Neural Spine initialized. Listening for context frames.")

    async def stop(self) -> None:
        """Stop listening to GlobalBus."""
        self._running = False

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        """Process generic frontend events that might contain context."""
        event_type = event.get("type")
        if event_type == "tool_result":
            await self._add_frame("tool_result", event)

    async def _handle_tool_result(self, result: Dict[str, Any]) -> None:
        """Capture every tool_result from GWS Bridge or other tools."""
        await self._add_frame("tool", result)

    async def _handle_learning(self, learning: Dict[str, Any]) -> None:
        """Capture 'Learnings' from Gemini or internal logic."""
        await self._add_frame("learning", learning)

    async def _add_frame(self, frame_type: str, data: Dict[str, Any]) -> None:
        """Push a frame to the Redis-backed sliding window."""
        if not self._bus or not self._bus._client:
            return

        full_key = f"{self._bus._prefix}{self._key}"

        frame = {
            "type": frame_type,
            "data": data,
        }

        try:
            try:
                import msgpack

                payload = msgpack.packb(frame, use_bin_type=True)
            except ImportError:
                import json

                payload = json.dumps(frame)
            await self._bus._client.lpush(full_key, payload)
            await self._bus._client.ltrim(full_key, 0, self._max_frames - 1)
        except Exception as e:
            logger.error("NeuralSpine: Failed to append frame: %s", e)

    async def get_warm_cache(self) -> List[Dict[str, Any]]:
        """Retrieve the last N interaction frames for expert handover."""
        if not self._bus or not self._bus._client:
            return []

        full_key = f"{self._bus._prefix}{self._key}"
        try:
            frames_raw = await self._bus._client.lrange(
                full_key, 0, self._max_frames - 1
            )
            frames = []
            for f in frames_raw:
                try:
                    import msgpack

                    if isinstance(f, bytes):
                        try:
                            decoded = msgpack.unpackb(f, raw=False)
                            frames.append(decoded)
                            continue
                        except Exception:
                            pass
                except ImportError:
                    pass

                import json

                # Handle either string/bytes depending on Redis decode_responses
                if isinstance(f, bytes):
                    f = f.decode("utf-8")
                frames.append(json.loads(f))
            # Reverse to return chronological order (lpush makes index 0 the newest)
            return list(reversed(frames))
        except Exception as e:
            logger.error("NeuralSpine: Failed to retrieve cache: %s", e)
            return []

    async def inject_diagnostic_trace(self, trace: str) -> None:
        """
        Inject a diagnostic trace as a Hidden System Prompt.
        This allows the AI to react with 'I noticed the Workspace link is lagging...'.
        """
        if not self._bus or not self._bus._client:
            return

        full_key = f"{self._bus._prefix}{self._system_prompt_key}"
        try:
            await self._bus._client.set(full_key, trace, ex=60)  # Expire after 60s
            logger.info("NeuralSpine: Injected diagnostic trace: %s", trace)

            # Optionally push a frame so it's in the immediate context
            await self._add_frame("diagnostic", {"message": trace})

        except Exception as e:
            logger.error("NeuralSpine: Failed to inject diagnostic trace: %s", e)

    async def get_active_diagnostic(self) -> Optional[str]:
        """Fetch the currently active diagnostic trace, if any."""
        if not self._bus or not self._bus._client:
            return None

        full_key = f"{self._bus._prefix}{self._system_prompt_key}"
        try:
            trace = await self._bus._client.get(full_key)
            if isinstance(trace, bytes):
                return trace.decode("utf-8")
            return trace
        except Exception as e:
            logger.error("NeuralSpine: Failed to get active diagnostic: %s", e)
            return None


# Singleton instance
neural_spine = NeuralSpine()
