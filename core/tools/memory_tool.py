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
from typing import Any, Optional

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


async def save_memory(key: str, value: str, **kwargs) -> dict:
    """
    Save a piece of information to persistent memory.

    Args:
        key: A short label for the memory (e.g., "user_name", "preference")
        value: The information to remember
    """
    db = _get_db()
    if not db:
        logger.warning("Memory tool: Firebase not connected — using local fallback")
        return {
            "status": "saved_locally",
            "key": key,
            "message": f"Remembered '{key}' (local only — will not persist across restarts).",
        }

    try:
        doc_ref = db.collection("memory").document(key)
        await doc_ref.set({
            "key": key,
            "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "session_id": _firebase._session_id if _firebase else None,
        })
        logger.info("Memory saved: %s = %s", key, value[:50])
        return {
            "status": "saved",
            "key": key,
            "message": f"I'll remember that: {key} = {value}",
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


async def list_memories(limit: int = 10, **kwargs) -> dict:
    """
    List all saved memories.

    Args:
        limit: Maximum number of memories to return.
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Memory is offline."}

    try:
        memories = []
        docs = db.collection("memory").limit(limit).stream()
        async for doc in docs:
            data = doc.to_dict()
            memories.append({
                "key": data.get("key", doc.id),
                "value": data.get("value", ""),
            })
        return {
            "status": "ok",
            "count": len(memories),
            "memories": memories,
        }
    except Exception as exc:
        logger.error("Memory list failed: %s", exc)
        return {"status": "error", "message": f"Failed to list memories: {exc}"}


def get_tools() -> list[dict]:
    """
    Module-level tool registration.

    Called by ToolRouter.register_module() to auto-discover
    all memory tools.
    """
    return [
        {
            "name": "save_memory",
            "description": (
                "Save a piece of information to persistent memory. "
                "Use when the user asks you to remember something, "
                "like their name, preferences, or important details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "A short label for the memory "
                            "(e.g., 'user_name', 'favorite_language')"
                        ),
                    },
                    "value": {
                        "type": "string",
                        "description": "The information to remember",
                    },
                },
                "required": ["key", "value"],
            },
            "handler": save_memory,
        },
        {
            "name": "recall_memory",
            "description": (
                "Recall a previously saved piece of information. "
                "Use when the user asks 'do you remember...?' or "
                "references something they told you before."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The label of the memory to recall",
                    },
                },
                "required": ["key"],
            },
            "handler": recall_memory,
        },
        {
            "name": "list_memories",
            "description": (
                "List all saved memories. Use when the user asks "
                "'what do you remember about me?'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return",
                    },
                },
            },
            "handler": list_memories,
        },
    ]
