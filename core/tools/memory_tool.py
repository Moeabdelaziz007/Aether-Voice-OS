"""
Aether Voice OS — Memory Tool (Session Context Persistence).

Gives the agent persistent memory across conversation turns
and even across sessions. Backed by Firestore.

When the user says "Remember that my name is Moe" or
"What did I tell you earlier?", Gemini emits a function call
that lands here.

Collections:
  /memory/{key} — key-value store for agent memory
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level reference to the Firebase connector
_firebase = None


def set_firebase_connector(connector) -> None:
    """Inject the FirebaseConnector at startup."""
    global _firebase
    _firebase = connector


def _get_db():
    """Get Firestore database client, or None."""
    if _firebase and _firebase.is_connected:
        return _firebase._db
    return None


async def save_memory(
    key: str,
    value: str,
    priority: str = "medium",
    tags: Optional[list[str]] = None,
    **kwargs,
) -> dict:
    """
    Save a piece of information to persistent memory.

    Args:
        key: A short label for the memory (e.g., "user_name", "preference")
        value: The information to remember
        priority: Importance of this memory (low, medium, high). Defaults to medium.
        tags: Optional list of categories/tags (e.g., ["contacts", "work", "hobby"])
    """
    db = _get_db()
    if not db:
        logger.warning("Memory tool: Firebase not connected — using local fallback")
        return {
            "status": "saved_locally",
            "key": key,
            "message": f"Remembered '{key}' (local only — will not persist).",
        }

    valid_priorities = ["low", "medium", "high"]
    priority = priority.lower() if priority.lower() in valid_priorities else "medium"
    tags = tags or []

    try:
        doc_ref = db.collection("memory").document(key)
        await doc_ref.set(
            {
                "key": key,
                "value": value,
                "priority": priority,
                "tags": tags,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "session_id": _firebase._session_id if _firebase else None,
            }
        )
        logger.info("Memory saved [%s]: %s = %s", priority, key, value[:50])
        return {
            "status": "saved",
            "key": key,
            "priority": priority,
            "message": f"Synapse update: I've stored '{key}' as {priority} priority memory.",
        }
    except Exception as exc:
        logger.error("Memory save failed: %s", exc)
        return {"status": "error", "message": f"Failed to save memory: {exc}"}


async def recall_memory(key: str, **kwargs) -> dict:
    """
    Recall a previously saved piece of information.

    Args:
        key: The label of the memory to recall
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Memory is offline."}

    try:
        doc_ref = db.collection("memory").document(key)
        doc = await doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            logger.info("Memory recalled: %s", key)
            return {
                "status": "found",
                "key": key,
                "value": data.get("value", ""),
                "priority": data.get("priority", "medium"),
                "tags": data.get("tags", []),
                "saved_at": data.get("updated_at", "unknown"),
            }
        else:
            return {
                "status": "not_found",
                "key": key,
                "message": f"I don't have any memory saved under '{key}'.",
            }
    except Exception as exc:
        logger.error("Memory recall failed: %s", exc)
        return {"status": "error", "message": f"Failed to recall memory: {exc}"}


async def list_memories(
    limit: int = 10, priority: Optional[str] = None, **kwargs
) -> dict:
    """
    List saved memories, optionally filtered by priority.

    Args:
        limit: Maximum number of memories to return.
        priority: Filter by 'low', 'medium', or 'high'.
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Memory is offline."}

    try:
        memories = []
        query = db.collection("memory")
        if priority:
            query = query.where("priority", "==", priority.lower())

        docs = query.limit(limit).stream()
        async for doc in docs:
            data = doc.to_dict()
            memories.append(
                {
                    "key": data.get("key", doc.id),
                    "value": data.get("value", ""),
                    "priority": data.get("priority", "medium"),
                    "tags": data.get("tags", []),
                }
            )
        return {
            "status": "ok",
            "count": len(memories),
            "memories": memories,
        }
    except Exception as exc:
        logger.error("Memory list failed: %s", exc)
        return {"status": "error", "message": f"Failed to list memories: {exc}"}


async def semantic_search(tags: list[str], limit: int = 5, **kwargs) -> dict:
    """
    Search for memories using tags. This acts as a semantic-assisted lookup.

    Args:
        tags: List of tags to search for.
        limit: Maximum results.
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Memory is offline."}

    try:
        memories = []
        # Firestore array_contains_any supports up to 10 tags
        query = (
            db.collection("memory")
            .where("tags", "array_contains_any", tags)
            .limit(limit)
        )
        docs = query.stream()
        async for doc in docs:
            data = doc.to_dict()
            memories.append(
                {
                    "key": data.get("key", doc.id),
                    "value": data.get("value", ""),
                    "priority": data.get("priority", "medium"),
                }
            )

        return {
            "status": "ok",
            "matches": len(memories),
            "memories": memories,
        }
    except Exception as exc:
        logger.error("Semantic search failed: %s", exc)
        return {"status": "error", "message": f"Search failed: {exc}"}


async def prune_memories(priority: str = "low", **kwargs) -> dict:
    """
    Delete all memories of a specific priority. Use for memory hygiene.

    Args:
        priority: The priority to prune ('low', 'medium', or 'high').
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Memory is offline."}

    try:
        count = 0
        docs = (
            db.collection("memory").where("priority", "==", priority.lower()).stream()
        )
        async for doc in docs:
            await doc.reference.delete()
            count += 1

        logger.info("Pruned %d %s-priority memories", count, priority)
        return {
            "status": "pruned",
            "count": count,
            "message": f"Successfully cleared {count} {priority}-importance items from memory.",
        }
    except Exception as exc:
        logger.error("Pruning failed: %s", exc)
        return {"status": "error", "message": f"Pruning failed: {exc}"}


def get_tools() -> list[dict]:
    """Module-level tool registration for Neural Dispatcher."""
    return [
        {
            "name": "save_memory",
            "description": (
                "Save information to persistent memory with priority and tags. "
                "Higher priority memories are kept longer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Unique label for the memory",
                    },
                    "value": {
                        "type": "string",
                        "description": "Information to remember",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Importance level",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Categorization tags",
                    },
                },
                "required": ["key", "value"],
            },
            "handler": save_memory,
        },
        {
            "name": "recall_memory",
            "description": "Recall a previously saved piece of information by key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Memory key to find"},
                },
                "required": ["key"],
            },
            "handler": recall_memory,
        },
        {
            "name": "list_memories",
            "description": "List all saved memories, optionally filtering by priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max documents"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
            "handler": list_memories,
        },
        {
            "name": "semantic_search",
            "description": "Search memories by descriptive tags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer"},
                },
                "required": ["tags"],
            },
            "handler": semantic_search,
        },
        {
            "name": "prune_memories",
            "description": "Clear out low-importance memories to free up context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
            "handler": prune_memories,
        },
    ]
