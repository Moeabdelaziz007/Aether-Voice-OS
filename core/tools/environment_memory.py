"""
Aether Voice OS — Environment Memory (Spatial Grounding).

This tool allows the agent to semantically search through its visual history.
It uses the LocalVectorStore to index frame descriptions (from vision pulses).
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.tools.vector_store import LocalVectorStore

logger = logging.getLogger(__name__)

# Default path for environment index
ENV_INDEX_PATH = Path(".aether_env_index.pkl")


class EnvironmentMemory:
    """
    Manages the semantic indexing and retrieval of visual environment states.
    """

    def __init__(self, api_key: str):
        self._vector_store = LocalVectorStore(api_key=api_key)
        self._vector_store.load(ENV_INDEX_PATH)

    async def add_frame_description(
        self,
        description: str,
        timestamp_offset: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a semantic description of a visual frame to the memory.
        """
        now = datetime.now().isoformat()
        key = f"frame_{int(datetime.now().timestamp())}_{timestamp_offset}"

        full_metadata = {
            "timestamp": now,
            "offset_s": timestamp_offset,
            "type": "vision_pulse",
            **(metadata or {}),
        }

        # We index the description so we can search it later
        await self._vector_store.add_text(
            key=key, text=description, metadata=full_metadata
        )

        # Save incrementally
        self._vector_store.save(ENV_INDEX_PATH)
        logger.info(f"✦ Environment Memory: Indexed new frame at T+{timestamp_offset}s")

    async def query_environment(
        self, query: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search visual history for matches to the query.
        """
        logger.info(f"🧠 Environment Memory: Querying for '{query}'")

        query_vec = await self._vector_store.get_query_embedding(query)
        results = self._vector_store.search(query_vec, limit=limit)

        formatted_results = []
        for res in results:
            formatted_results.append(
                {
                    "description": self._vector_store._vectors.get(
                        res["key"]
                    ),  # Note: _vectors stores embeddings, text is in metadata or we should store text
                    "similarity": res["similarity"],
                    "timestamp": res["metadata"].get("timestamp"),
                    "offset": res["metadata"].get("offset_s"),
                }
            )

        return results


# Singleton instance access pattern common in Aether tools
_memory_instance: Optional[EnvironmentMemory] = None


def get_env_memory(api_key: str) -> EnvironmentMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EnvironmentMemory(api_key)
    return _memory_instance
