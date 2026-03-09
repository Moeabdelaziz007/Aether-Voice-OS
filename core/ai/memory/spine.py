"""
Neural Spine — High-Performance Context Compression
Orchestrates "Warm Context" by periodically summarizing the interaction stream
using Gemini 2.0 Flash to maintain a compact, high-fidelity neural state.
"""

import asyncio
import time
from typing import List, Optional

from core.utils.logging import logger
from google import genai
from pydantic import BaseModel

from core.infra.event_bus import EventBus


class NeuralSnapshot(BaseModel):
    summary: str
    vector_id: Optional[str] = None
    timestamp: float
    entities: List[str] = []

class NeuralSpine:
    def __init__(self, api_key: str, interval_minutes: int = 5):
        self.client = genai.Client(api_key=api_key)
        self.interval = interval_minutes * 60
        self.history: List[dict] = []
        self.last_compression = time.time()
        self.current_summary: str = ""
        self._lock = asyncio.Lock()
        
    async def add_interaction(self, role: str, content: str):
        async with self._lock:
            self.history.append({"role": role, "content": content})
            
            # Auto-trigger compression if interval exceeded
            if time.time() - self.last_compression > self.interval:
                asyncio.create_task(self.compress())

    async def compress(self):
        """Compresses the history into a Neural Snapshot using Gemini."""
        if not self.history:
            return

        async with self._lock:
            # Prepare the prompt for compression
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
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                
                self.current_summary = response.text
                self.last_compression = time.time()
                # Clear history after successful compression to keep the 'spine' warm but slim
                self.history = [{"role": "system", "content": f"Previous context summary: {self.current_summary}"}]
                
                logger.info(f"Neural Spine: Context compressed successfully. New summary length: {len(self.current_summary)}")
                
                # Notify system of state change
                EventBus().emit("neural:spine:compressed", {"summary": self.current_summary})
                
            except Exception as e:
                logger.error(f"Neural Spine compression failed: {e}")

    async def get_handover_context(self) -> str:
        """Returns the current warm context for expert handovers."""
        return self.current_summary or "No previous context available."

    def clear(self):
        self.history = []
        self.current_summary = ""
        self.last_compression = time.time()
