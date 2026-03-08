import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger("AetherOS.LongTermMemory")

# ==========================================
# 🌌 Vector Memory Entry
# ==========================================


class MemoryEntry(BaseModel):
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

    Now supports Firestore backend for cloud persistence.
    """

    def __init__(
        self,
        provider: str = "firestore",
        api_key: Optional[str] = None,
    ):
        self.provider = provider
        self._api_key = api_key
        self._local_store: List[MemoryEntry] = []  # type: ignore
        self._firestore_store: Any = None  # type: ignore

        if provider == "firestore":
            # Import Firestore backend
            from core.tools.firestore_vector_store import FirestoreVectorStore
            key = api_key if api_key else "demo-key"
            self._firestore_store: Any = FirestoreVectorStore(api_key=key)
            logger.info("[Memory] Long-term storage using Firestore (Cloud)")
        else:
            msg = f"[Memory] Long-term storage initialized using: {provider}"
            logger.info(msg)

    async def save_memory(
        self,
        content: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Persist a thought into the vector space."""
        if self._firestore_store:
            # Use Firestore backend
            key = f"mem_{int(time.time() * 1000)}"
            await self._firestore_store.add_text(key, content, metadata)
            # Truncate long content
            truncated = content[:40]
            if len(content) > 40:
                truncated += "..."
            logger.info(
                "[Memory] Persisted knowledge to Firestore: %s",
                truncated
            )
        else:
            # Local storage fallback
            entry = MemoryEntry(
                id=f"mem_{int(time.time() * 1000)}",
                vector=vector,
                content=content,
                metadata=metadata or {},
                timestamp=time.time(),
            )
            self._local_store.append(entry)
            logger.info(f"[Memory] Persisted knowledge: {content[:40]}...")

    async def query_memory(
        self, vector: List[float], top_k: int = 3
    ) -> List[MemoryEntry]:
        """
        Semantic search for relevant past experiences.
        Uses cosine similarity for local provider,
        or Firestore vector search for cloud provider.
        """
        import numpy as np

        if self._firestore_store:
            # Use Firestore backend search
            query_array = np.array(vector)
            results = await self._firestore_store.search(query_array, limit=top_k)
            # Convert to MemoryEntry format
            return [
                MemoryEntry(
                    id=r.get('key', 'unknown'),
                    vector=[],  # Firestore doesn't return vectors
                    content=r.get('text', ''),
                    metadata=r.get('metadata', {}),
                    timestamp=time.time()
                )
                for r in results
            ]

        # Local storage fallback
        if not self._local_store:
            return []

        query_vec = np.array(vector)
        results = []

        for entry in self._local_store:
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
        self._local_store = []
        self._firestore_store = None
        logger.warning("[Memory] Long-term memory wiped.")
