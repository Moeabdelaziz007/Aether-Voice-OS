"""
Aether Voice OS — Hive Collective Memory.

Provides a sharedFirestore namespace for expert souls to persist
architectural state and high-level intent across handoffs.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Shared instance of FirebaseConnector
_firebase = None


def set_firebase_connector(connector: Any) -> None:
    global _firebase
    _firebase = connector


async def write_collective_memory(
    key: str, value: Any, tags: Optional[list[str]] = None
) -> dict[str, object]:
    """
    Write a value to the Hive Collective Memory.

    Args:
        key: The unique identifier for this memory slot.
        value: The data to store (JSON serializable).
        tags: Optional list of domains this memory relates to (e.g.
            ["code", "database"]).
    """
    if not _firebase or not _firebase.is_connected:
        return {
            "status": "error",
            "message": "Hive Memory offline (Firebase not connected)",
        }

    memory_data: dict[str, object] = {
        "key": key,
        "value": value,
        "tags": tags or [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": _firebase._session_id,
    }

    try:
        doc_ref = _firebase._db.collection("hive_memory").document(key)
        await doc_ref.set(memory_data, merge=True)
        logger.info("A2A [MEMORY] Persisted collective state: %s", key)
        return {"status": "success", "message": f"Memory '{key}' synced to Hive."}
    except Exception as e:
        logger.error("Hive Memory write failed: %s", e)
        return {"status": "error", "message": str(e)}


async def read_collective_memory(key: str) -> dict[str, object]:
    """Read a value from the Hive Collective Memory."""
    if not _firebase or not _firebase.is_connected:
        return {
            "status": "error",
            "data": {"value": None},
            "message": "Hive Memory offline"
        }

    try:
        doc_ref = _firebase._db.collection("hive_memory").document(key)
        doc = await doc_ref.get()
        if doc.exists:
            return {"status": "success", "data": doc.to_dict()}
        return {
            "status": "not_found",
            "data": {"value": None},
            "message": f"Memory slot '{key}' is empty."
        }
    except Exception as e:
        logger.error("Hive Memory read failed: %s", e)
        return {"status": "error", "message": str(e)}


def get_tools() -> list[dict[str, object]]:
    """Module registration for Collective Memory tools."""
    return [
        {
            "name": "write_memory",
            "description": (
                "Store state in the Hive Collective Memory for other expert "
                "souls to see."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "object"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["key", "value"],
            },
            "handler": write_collective_memory,
        },
        {
            "name": "read_memory",
            "description": (
                "Retrieve state from the Hive Collective Memory stored by "
                "previous experts."
            ),
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
            "handler": read_collective_memory,
        },
    ]
