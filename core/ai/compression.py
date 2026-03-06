"""
Aether Voice OS — Neural Summarizer (Context Compression).

Condenses conversation history and working memory into "Semantic Seeds"
to optimize handover performance and minimize token bloat.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from google import genai
from google.genai import types

from core.ai.handover.protocol_models import HandoverContext
from core.infra.config import AIConfig

logger = logging.getLogger(__name__)


class NeuralSummarizer:
    """
    Condenses rich AI context into compact semantic structures.

    Architecture:
      - Analyzes ConversationHistory + WorkingMemory.
      - Extracts: Key Entities, Unresolved Intents, Emotional Trajectory, and Task Progress.
      - Produces a "Semantic Seed" (Compact JSON or Narrative).
    """

    def __init__(self, config: AIConfig) -> None:
        self._config = config
        self._client = genai.Client(api_key=config.api_key)
        self._model_id = (
            "gemini-2.0-flash-lite"  # Fast and inexpensive for compression tasks
        )

    async def compress(self, context: HandoverContext) -> Dict[str, Any]:
        """
        Compresses a full HandoverContext into a Semantic Seed.
        """
        if not context.conversation_history and not context.working_memory:
            return {}

        # Prepare payload for LLM
        history_text = "\n".join(
            [
                f"{entry.speaker}: {entry.message}"
                for entry in context.conversation_history
            ]
        )

        prompt = f"""
        Analyze the following conversation history and working memory from an AI session.
        Compress it into a high-density "Semantic Seed" for a target agent.
        
        CONVERSATION HISTORY:
        {history_text}
        
        WORKING MEMORY:
        {context.working_memory.model_dump_json()}
        
        TASK:
        {context.task}
        
        OUTPUT FORMAT (JSON ONLY):
        {{
          "entities": ["list of key entities discussed"],
          "intent_summary": "one sentence summary of user intent",
          "unresolved_items": ["list of pending tasks or questions"],
          "emotional_trajectory": "summary of user sentiment/vibe",
          "critical_knowledge": "any specific facts the next agent MUST know",
          "token_density_ratio": 0.1
        }}
        """

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self._model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            if response and response.text:
                seed = json.loads(response.text)
                logger.info(
                    "✦ Neural compression successful. Ratio: %s",
                    seed.get("token_density_ratio", "N/A"),
                )
                return seed

        except Exception as e:
            logger.error("Failed to compress context: %s", e)
            # Fallback to a very basic summary if LLM fails
            return {
                "error": "Compression failed",
                "fallback_summary": context.task[:100],
            }

        return {}

    def should_compress(self, context: HandoverContext) -> bool:
        """Heuristic to decide if context is large enough to warrant compression."""
        # Simple threshold: > 20 messages or > 5000 chars in memory
        num_msgs = len(context.conversation_history)
        mem_size = len(str(context.working_memory))

        return num_msgs > 20 or mem_size > 5000
