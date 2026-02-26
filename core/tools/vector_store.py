"""
Aether Voice OS — Local Vector Store (Reflexive Index).

Provides no-cost semantic search for tool routing and memory retrieval.
Uses numpy for cosine similarity and Gemini for embedding generation.
"""
from __future__ import annotations

import logging
import numpy as np
from typing import Any, Optional
from google import genai

logger = logging.getLogger(__name__)

class LocalVectorStore:
    """A lightweight, local-first vector store for semantic routing."""
    
    def __init__(self, api_key: str, model: str = "gemini-embedding-001") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._vectors: dict[str, np.ndarray] = {}
        self._metadata: dict[str, dict] = {}

    async def add_text(self, key: str, text: str, metadata: Optional[dict] = None) -> None:
        """Embed text and add to the local index."""
        try:
            res = self._client.models.embed_content(
                model=self._model,
                contents=text,
                config={"task_type": "RETRIEVAL_DOCUMENT"}
            )
            embedding = np.array(res.embeddings[0].values)
            self._vectors[key] = embedding
            self._metadata[key] = metadata or {}
            logger.info("Vector indexed: %s", key)
        except Exception as e:
            logger.error("Failed to embed text for %s: %s", key, e)

    def search(self, query_vector: np.ndarray, limit: int = 1) -> list[dict]:
        """Perform cosine similarity search against indexed vectors."""
        if not self._vectors:
            return []

        results = []
        for key, vector in self._vectors.items():
            # Cosine similarity = (A . B) / (||A|| * ||B||)
            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector)
            )
            results.append({
                "key": key,
                "similarity": float(similarity),
                "metadata": self._metadata[key]
            })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

    async def get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a search query."""
        res = self._client.models.embed_content(
            model=self._model,
            contents=query,
            config={"task_type": "RETRIEVAL_QUERY"}
        )
        return np.array(res.embeddings[0].values)
