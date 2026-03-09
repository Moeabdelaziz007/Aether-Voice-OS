"""
Aether Voice OS — The Neural Spine.

A distributed semantic memory layer that orchestrates "Warm Context" by periodically 
summarizing the interaction stream using Gemini 2.0 Flash while maintaining a 
Redis-backed sliding window of interaction frames via GlobalBus.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from core.utils.logging import logger
from google import genai
from pydantic import BaseModel

from core.infra.transport.bus import GlobalBus


class NeuralSnapshot(BaseModel):
    summary: str
    vector_id: Optional[str] = None
    timestamp: float
    entities: List[str] = []

class NeuralSpine:
    """
    Distributed Context & Autonomous SRE Cache with Neural Compression.
    Maintains a Redis-backed sliding window of 'Interaction Frames' and
    periodically compresses them into snapshots.
    """

    def __init__(
        self, 
        bus: Optional[GlobalBus] = None, 
        api_key: Optional[str] = None,
        max_frames: int = 50,
        compression_interval_minutes: int = 5
    ):
        self._bus = bus
        self._api_key = api_key
        self._client = genai.Client(api_key=api_key) if api_key else None
        
        self._max_frames = max_frames
        self._compression_interval = compression_interval_minutes * 60
        self._last_compression = time.time()
        
        self._key = "neural_spine:frames"
        self._system_prompt_key = "neural_spine:system_prompt"
        
        self.history: List[Dict[str, Any]] = []
        self.current_summary: str = ""
        self._lock = asyncio.Lock()
        self._running = False

    async def start(self) -> None:
        """Start listening to GlobalBus for memory events."""
        if not self._bus or not self._bus.is_connected:
            logger.warning(
                "NeuralSpine: GlobalBus not available. Memory will not persist in Redis."
            )
        else:
            # Subscribe to tool results and AI learnings
            await self._bus.subscribe("frontend_events", self._handle_event)
            await self._bus.subscribe("tool_result", self._handle_tool_result)
            await self._bus.subscribe("ai_learning", self._handle_learning)
            logger.info("✦ Neural Spine: Redis sync active.")

        self._running = True
        logger.info("✦ Neural Spine initialized. Listening for context frames.")

    async def stop(self) -> None:
        """Stop processing memory."""
        self._running = False

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        """Process generic frontend events."""
        event_type = event.get("type")
        if event_type == "tool_result":
            await self.add_interaction("tool", str(event))

    async def _handle_tool_result(self, result: Dict[str, Any]) -> None:
        """Capture every tool_result."""
        await self.add_interaction("tool", str(result))

    async def _handle_learning(self, learning: Dict[str, Any]) -> None:
        """Capture 'Learnings' from internal logic."""
        await self.add_interaction("learning", str(learning))

    async def add_interaction(self, role: str, content: str):
        """Add a frame to persistent Redis and local history for compression."""
        async with self._lock:
            frame_data = {"role": role, "content": content}
            self.history.append(frame_data)
            
            # Redis Persistence
            if self._bus and self._bus.is_connected:
                await self._add_redis_frame(role, frame_data)
            
            # Auto-trigger compression if interval exceeded and client available
            if self._client and (time.time() - self._last_compression > self._compression_interval):
                asyncio.create_task(self.compress())

    async def _add_redis_frame(self, frame_type: str, data: Dict[str, Any]) -> None:
        """Push a frame to the Redis-backed sliding window."""
        if not self._bus or not self._bus._client:
            return

        full_key = f"{self._bus._prefix}{self._key}"
        frame = {"type": frame_type, "data": data}

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
            logger.error("NeuralSpine: Failed to append Redis frame: %s", e)

    async def compress(self):
        """Compresses the history into a Neural Snapshot using Gemini."""
        if not self._client or not self.history:
            return

        async with self._lock:
            text_to_compress = "\n".join([f"{h['role']}: {h['content']}" for h in self.history])
            
            prompt = f"""
            Compress the following AetherOS interaction history into a concise 'Neural Snapshot'.
            Focus on:
            1. Core user intent and current task.
            2. Technical decisions made.
            3. Explicit preferences mentioned.
            4. Unresolved blockers.
            
            History:
            {text_to_compress}
            
            Return ONLY a structured summary.
            """
            
            try:
                response = self._client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                
                self.current_summary = response.text
                self._last_compression = time.time()
                # Keep summary in history but clear noise
                self.history = [{"role": "system", "content": f"Previous context summary: {self.current_summary}"}]
                
                logger.info(f"Neural Spine: Context compressed. Summary length: {len(self.current_summary)}")
                
                if self._bus:
                    await self._bus.publish("neural:spine:compressed", {"summary": self.current_summary})
                
            except Exception as e:
                logger.error(f"Neural Spine compression failed: {e}")

    async def get_handover_context(self) -> str:
        """Returns the current warm context for expert handovers."""
        return self.current_summary or "No previous context available."

    async def get_warm_cache(self) -> List[Dict[str, Any]]:
        """Retrieve the last N interaction frames from Redis."""
        if not self._bus or not self._bus._client:
            return [{"role": "local_history", "content": str(self.history)}]

        full_key = f"{self._bus._prefix}{self._key}"
        try:
            frames_raw = await self._bus._client.lrange(full_key, 0, self._max_frames - 1)
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
                if isinstance(f, bytes):
                    f = f.decode("utf-8")
                frames.append(json.loads(f))
            return list(reversed(frames))
        except Exception as e:
            logger.error("NeuralSpine: Failed to retrieve cache: %s", e)
            return []

    async def inject_diagnostic_trace(self, trace: str) -> None:
        """Inject a diagnostic trace as a Hidden System Prompt."""
        if not self._bus or not self._bus._client:
            return

        full_key = f"{self._bus._prefix}{self._system_prompt_key}"
        try:
            await self._bus._client.set(full_key, trace, ex=60)
            logger.info("NeuralSpine: Injected diagnostic trace: %s", trace)
            await self.add_interaction("diagnostic", trace)
        except Exception as e:
            logger.error("NeuralSpine: Failed to inject diagnostic trace: %s", e)

    def clear(self):
        self.history = []
        self.current_summary = ""
        self._last_compression = time.time()

# Singleton instance
neural_spine = NeuralSpine()
