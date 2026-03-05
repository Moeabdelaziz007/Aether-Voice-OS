import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger("AetherOS.LongTermMemory")

# ==========================================
# 🌌 Vector Memory Entry
# ==========================================


class MemoryEntry(BaseModel)):
    id: str
    vector: List[float]
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: float


# ==========================================
# 🌌 Long-Term Vector Memory
# Permanent storage with semantic retrieval.
# ==========================================


class LongTermMemory:
    """
    The 'Permanent Storage' for AetherOS.
    Abstracts vector database operations (Pinecone, Firestore, or Local FAISS).
    Allows the agent to 'remember' conversations from days ago.
    """

    def __init__(self, provider: str = "local"):
        self.provider = provider
        # Simulated local vector space for the Alpha Kernel
        self._store: List[MemoryEntry] = []
        logger.info(f"[Memory] Long-term storage initialized using: {provider}")

    async def save_memory(
        self,
        content: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Persist a thought into the vector space."""
        entry = MemoryEntry(
            id=f"mem_{int(time.time() * 1000)}",
            vector=vector,
            content=content,
            metadata=metadata or {},
            timestamp=time.time(),
        )
        self._store.append(entry)
        logger.info(f"[Memory] Persisted knowledge: {content[:40]}...")

    async def query_memory(
        self, vector: List[float], top_k: int = 3
    ) -> List[MemoryEntry]:
        """
        Semantic search for relevant past experiences.
        Uses cosine similarity for the local provider.
        """
        import numpy as np

        if not self._store:
            return []

        query_vec = np.array(vector)
        results = []

        for entry in self._store:
            entry_vec = np.array(entry.vector)
            # Cosine Similarity
            score = np.dot(query_vec, entry_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(entry_vec) + 1e-6
            )
            results.append((entry, score))

        # Sort by best match
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k]]

    def clear_all(self):
        """Nuclear option: Forget everything."""
        self._store = []
        logger.warning("[Memory] Long-term memory wiped.")
