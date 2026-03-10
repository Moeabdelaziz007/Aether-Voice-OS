"""
Aether Voice OS — RAG Tool (Semantic Codebase Search).

Allows Gemini and the Proactive Agent to search the local codebase semantically.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from core.tools.vector_store import LocalVectorStore

logger = logging.getLogger(__name__)

# Global reference to the shared index, set by the engine during startup
_shared_index: Optional[LocalVectorStore] = None


def set_shared_index(index: LocalVectorStore) -> None:
    """Inject the global vector store."""
    global _shared_index
    _shared_index = index


async def search_codebase(query: str, limit: int = 3) -> dict[str, Any]:
    """
    Search the local AetherOS codebase for relevant code snippets or documentation.
    Use this to understand the implementation details of specific features or find bugs.

    Args:
        query: The semantic search query (e.g.
            "Where is the frustration trigger defined?").
        limit: Max number of chunks to return (default 3).
    """
    if not _shared_index:
        return {"error": "Local codebase index is not initialized or loaded."}

    try:
        query_vec = await _shared_index.get_query_embedding(query)
        results = _shared_index.search(query_vec, limit=limit)

        if not results:
            return {"message": "No relevant codebase chunks found."}

        formatted_results = []
        for r in results:
            # We recover the text using the chunk ID if needed, but the index currently
            # only stores embeddings. Assume metadata includes file and chunk info.
            # For now, return file paths and similarity so Gemini knows where to look.
            file_path = r["metadata"].get("file", "Unknown")
            chunk_idx = r["metadata"].get("chunk", 0)
            formatted_results.append(
                {
                    "file": file_path,
                    "chunk": chunk_idx,
                    "similarity": round(r["similarity"], 3),
                }
            )

        return {
            "query": query,
            "results": formatted_results,
            "instruction": ("Use the vision_tool or system_tool to read the specific file if more context is needed."),
        }
    except Exception as e:
        logger.error("RAG Tool search failed: %s", e)
        return {"error": str(e)}


def get_tools() -> list[dict[str, Any]]:
    """Export tool configuration to the Neural Dispatcher."""
    return [
        {
            "name": "search_codebase",
            "description": ("Perform a semantic search across the entire AetherOS codebase."),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": ("The search query, e.g., 'How is the Thalamic Gate implemented?'"),
                    },
                    "limit": {
                        "type": "INTEGER",
                        "description": "Number of results to return (max 5).",
                    },
                },
                "required": ["query"],
            },
            "handler": search_codebase,
            "latency_tier": "p95_sub_2s",
            "idempotent": True,
        }
    ]
