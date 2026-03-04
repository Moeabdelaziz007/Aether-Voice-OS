"""
Aether Voice OS — Cloud Vector Store (Firestore RAG).

Migrates the local vector store to Google Cloud Firestore for enterprise scalability.
Uses Gemini for embedding generation and Firestore for persistent storage.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from firebase_admin import firestore
from google import genai

from core.infra.cloud.firebase.interface import FirebaseConnector

logger = logging.getLogger(__name__)


class FirestoreVectorStore:
    """A Cloud-Native vector store using Firestore for persistence."""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._connector = FirebaseConnector()
        self._collection_name = "aether_embeddings"
        self._local_cache_vectors: Dict[str, np.ndarray] = {}
        self._local_cache_metadata: Dict[str, Dict] = {}

    async def initialize(self) -> bool:
        """Initialize the Firebase connection."""
        return await self._connector.initialize()

    async def add_text(
        self, key: str, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Embed text and add to Firestore."""
        if not self._connector.is_connected:
            await self.initialize()

        try:
            res = self._client.models.embed_content(
                model=self._model,
                contents=text,
                config={"task_type": "RETRIEVAL_DOCUMENT"},
            )
            embedding = res.embeddings[0].values
            
            # Sanitize key for Firestore (replace : with _)
            safe_key = key.replace(":", "_").replace("/", "_")
            
            doc_data = {
                "key": key,
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "indexed_at": firestore.SERVER_TIMESTAMP
            }

            if self._connector._db:
                self._connector._db.collection(self._collection_name).document(safe_key).set(doc_data)
                logger.info("Vector indexed in Firestore: %s", key)
            else:
                logger.warning("Firestore not connected. Vector not saved to cloud.")
                
        except Exception as e:
            logger.error("Failed to embed and upload text for %s: %s", key, e)

    async def search(self, query_vector: np.ndarray, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search. 
        Note: Firestore doesn't support vector search natively in all regions yet
        without specific extensions or pgvector. We implement a refined scan-and-compute 
        for this V6 prototype.
        """
        if not self._connector.is_connected or not self._connector._db:
            logger.warning("Firestore not connected for search.")
            return []

        try:
            # For the prototype, we fetch all vectors (or a significant subset) 
            # and perform cosine similarity calculation.
            # IN PRODUCTION: Use Firebase Vector Search Extension or Vertex AI Search.
            docs = self._connector._db.collection(self._collection_name).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                vector = np.array(data.get("embedding", []))
                
                if len(vector) == 0:
                    continue
                    
                # Cosine similarity = (A . B) / (||A|| * ||B||)
                similarity = np.dot(query_vector, vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(vector)
                )
                
                results.append({
                    "key": data.get("key"),
                    "text": data.get("text"),
                    "similarity": float(similarity),
                    "metadata": data.get("metadata", {})
                })

            # Sort by similarity descending
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error("Failed to search Firestore vectors: %s", e)
            return []

    async def get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a search query."""
        res = self._client.models.embed_content(
            model=self._model, contents=query, config={"task_type": "RETRIEVAL_QUERY"}
        )
        return np.array(res.embeddings[0].values)
