from __future__ import annotations
import logging
import os
from typing import List, Optional, Any
from google.genai import types
from core.ai.generative_init import get_genai_client

logger = logging.getLogger(__name__)

class AetherContextCacheManager:
    """
    Manages Google GenAI Context Caching for Aether sessions.
    Reduces latency for long-running multimodal sessions by caching 
    system instructions and semantic memory snapshots.
    """

    def __init__(self, api_key: str):
        self.client = get_genai_client(api_key=api_key)
        self._active_caches: dict[str, Any] = {}

    async def create_memory_cache(
        self, 
        model_name: str, 
        system_instruction: str, 
        memories: List[str],
        ttl_seconds: int = 3600
    ) -> Optional[str]:
        """
        Creates a new CachedContent resource in Google Cloud.
        """
        try:
            # Combine system instruction with semantic memories
            full_context = f"{system_instruction}\n\nRELEVANT_MEMORIES:\n" + "\n".join(memories)
            
            # Using the v1beta API features via google-genai SDK
            # Note: Cache creation is a synchronous blocking call in some SDK versions, 
            # but we'll treat it as a resource manager.
            
            display_name = f"aether_neural_cache_{int(os.times().elapsed)}"
            
            # In google-genai SDK, caching is managed via the 'caches' property
            cache = self.client.caches.create(
                model=model_name,
                config=types.CreateCachedContentConfig(
                    display_name=display_name,
                    system_instruction=full_context,
                    ttl=f"{ttl_seconds}s"
                )
            )
            
            logger.info(f"✦ Context Cache Created: {cache.name}")
            return cache.name
        except Exception as e:
            logger.error(f"Failed to create context cache: {e}")
            return None

    def get_cache_config(self, cache_name: str) -> types.LiveConnectConfig:
        """Returns a config that points to the cached content."""
        return types.LiveConnectConfig(
            cached_content=cache_name
        )
