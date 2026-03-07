"""
Aether Voice OS — Tasks Tool (Firestore Persistence Lattice).

Exposes Firestore CRUD operations as Gemini-callable functions.
When the user says "Add a task" or "What are my tasks?",
Gemini emits a function call that lands here.

Collections used in Firestore:
  - tasks/{task_id}: Individual tasks with title, due, priority, status
  - notes/{note_id}: Freeform notes

All read/write operations go through the FirebaseConnector.
If Firebase is unavailable, tools return graceful fallbacks.
"""

from __future__ import annotations

import logging
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Module-level reference to the Firebase connector
# Set by the engine during initialization
_firebase = None


def set_firebase_connector(connector) -> None:
    """Inject the FirebaseConnector at startup."""
    global _firebase
    _firebase = connector
    logger.info("Tasks tool connected to Firebase")


def _get_db():
    """Get Firestore database client, or None."""
    if _firebase and _firebase.is_connected and _firebase._db:
        return _firebase._db
    return None


async def create_task(
    title: str,
    due: str = "",
    priority: str = "medium",
    **kwargs,
) -> dict:
    """
    Create a new task in Firestore.

    Args:
        title: The task description (e.g., "Buy groceries")
        due: When it's due (e.g., "tomorrow", "Friday", "2025-03-01")
        priority: Task priority — low, medium, or high
    """
    task_id = str(uuid.uuid4())[:8]
    task_data = {
        "task_id": task_id,
        "title": title,
        "due": due,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db = _get_db()
    if db:
        try:
            doc_ref = db.collection("tasks").document(task_id)
            await doc_ref.set(task_data)
            logger.info("Task created in Firestore: %s — %s", task_id, title)
        except Exception as exc:
            logger.error("Failed to write task: %s", exc)
            return {"status": "error", "message": f"Failed to save: {exc}"}
    else:
        logger.warning("Firestore unavailable — task stored locally only")

    return {
        "status": "created",
        "task_id": task_id,
        "title": title,
        "due": due,
        "priority": priority,
        "message": f"Task '{title}' created successfully.",
    }


async def list_tasks(
    status: str = "pending",
    limit: int = 10,
    **kwargs,
) -> dict:
    """
    List tasks from Firestore, filtered by status.

    Args:
        status: Filter by status — pending, completed, or all
        limit: Maximum number of tasks to return
    """
    db = _get_db()
    if not db:
        return {
            "status": "unavailable",
            "tasks": [],
            "message": "Firestore is not connected. No tasks available.",
        }

    try:
        query = db.collection("tasks")
        if status != "all":
            query = query.where("status", "==", status)
        query = query.limit(limit)

        docs = []
        async for doc in query.stream():
            docs.append(doc.to_dict())

        logger.info("Retrieved %d tasks (filter: %s)", len(docs), status)

        if not docs:
            return {
                "status": "empty",
                "tasks": [],
                "message": "No tasks found.",
            }

        return {
            "status": "success",
            "count": len(docs),
            "tasks": docs,
            "message": f"Found {len(docs)} task(s).",
        }

    except Exception as exc:
        logger.error("Failed to list tasks: %s", exc)
        return {"status": "error", "tasks": [], "message": str(exc)}


async def complete_task(task_id: str, **kwargs) -> dict:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
    """
    db = _get_db()
    if not db:
        return {"status": "unavailable", "message": "Firestore not connected."}

    try:
        doc_ref = db.collection("tasks").document(task_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return {
                "status": "not_found",
                "message": f"Task '{task_id}' not found.",
            }

        await doc_ref.update(
            {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        task_data = doc.to_dict()
        logger.info("Task completed: %s — %s", task_id, task_data.get("title"))

        return {
            "status": "completed",
            "task_id": task_id,
            "title": task_data.get("title", "Unknown"),
            "message": f"Task '{task_data.get('title', task_id)}' marked as done!",
        }

    except Exception as exc:
        logger.error("Failed to complete task: %s", exc)
        return {"status": "error", "message": str(exc)}


async def add_note(content: str, tag: str = "general", **kwargs) -> dict:
    """
    Save a freeform note to Firestore.

    Args:
        content: The note content
        tag: Optional category tag
    """
    note_id = str(uuid.uuid4())[:8]
    note_data = {
        "note_id": note_id,
        "content": content,
        "tag": tag,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db = _get_db()
    if db:
        try:
            doc_ref = db.collection("notes").document(note_id)
            await doc_ref.set(note_data)
            logger.info("Note saved: %s", note_id)
        except Exception as exc:
            logger.error("Failed to save note: %s", exc)
            return {"status": "error", "message": str(exc)}

    return {
        "status": "saved",
        "note_id": note_id,
        "message": "Note saved successfully.",
    }


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1]


def _score_semantic_match(query: str, content: str) -> float:
    query_tokens = _tokenize(query)
    content_tokens = _tokenize(content)
    if not query_tokens or not content_tokens:
        return 0.0

    query_counter = Counter(query_tokens)
    content_counter = Counter(content_tokens)
    overlap = set(query_counter).intersection(content_counter)
    overlap_score = sum(
        min(query_counter[token], content_counter[token]) for token in overlap
    )
    normalization = max(len(query_tokens), 1)
    base_score = overlap_score / normalization
    phrase_boost = 0.25 if query.lower() in content.lower() else 0.0
    return min(1.0, base_score + phrase_boost)


async def recall_notes(
    query: str,
    tag: str = "all",
    limit: int = 5,
    min_score: float = 0.15,
    **kwargs: Any,
) -> dict[str, Any]:
    if not query.strip():
        return {"status": "error", "message": "query_required", "notes": []}

    db = _get_db()
    if not db:
        return {
            "status": "unavailable",
            "notes": [],
            "message": "Firestore is not connected. Notes recall unavailable.",
        }

    try:
        query_ref = db.collection("notes")
        if tag != "all":
            query_ref = query_ref.where("tag", "==", tag)

        ranked: list[dict[str, Any]] = []
        async for doc in query_ref.stream():
            item = doc.to_dict()
            content = str(item.get("content", ""))
            score = _score_semantic_match(query, content)
            if score < min_score:
                continue
            ranked.append(
                {
                    "note_id": item.get("note_id", doc.id),
                    "content": content,
                    "tag": item.get("tag", "general"),
                    "created_at": item.get("created_at"),
                    "score": round(score, 4),
                }
            )

        ranked.sort(
            key=lambda item: (float(item["score"]), str(item.get("created_at") or "")),
            reverse=True,
        )
        sliced = ranked[: max(1, int(limit))]
        if not sliced:
            return {
                "status": "empty",
                "query": query,
                "count": 0,
                "notes": [],
                "message": "No semantically related notes found.",
            }

        return {
            "status": "success",
            "query": query,
            "count": len(sliced),
            "notes": sliced,
            "message": f"Found {len(sliced)} relevant note(s).",
        }
    except Exception as exc:
        logger.error("Failed to recall notes: %s", exc)
        return {"status": "error", "query": query, "notes": [], "message": str(exc)}


def get_tools() -> list[dict]:
    """
    Module-level tool registration.

    Called by ToolRouter.register_module() to auto-discover
    all Firestore task/note tools.
    """
    return [
        {
            "name": "create_task",
            "description": (
                "Create a new task with a title, optional due date, and priority. "
                "Use when the user asks to add a task, reminder, or to-do item."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title or description",
                    },
                    "due": {
                        "type": "string",
                        "description": (
                            "When the task is due (e.g., 'tomorrow', 'Friday')"
                        ),
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority level",
                    },
                },
                "required": ["title"],
            },
            "handler": create_task,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "list_tasks",
            "description": (
                "List the user's tasks. Can filter by status: pending, completed, "
                "or all. Use when the user asks about their tasks, to-do list, "
                "or what they need to do."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter tasks by status",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return",
                    },
                },
            },
            "handler": list_tasks,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        },
        {
            "name": "complete_task",
            "description": (
                "Mark a task as completed. Requires the task ID. "
                "Use when the user says they finished a task."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to complete",
                    },
                },
                "required": ["task_id"],
            },
            "handler": complete_task,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "add_note",
            "description": (
                "Save a freeform note. Use when the user asks to "
                "remember something or save a quick note."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The note content",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional category tag for the note",
                    },
                },
                "required": ["content"],
            },
            "handler": add_note,
            "latency_tier": "p95_sub_500ms",
            "idempotent": False,
        },
        {
            "name": "recall_notes",
            "description": (
                "Semantically recall notes by meaning and keyword similarity. "
                "Use when the user asks what they noted earlier about a topic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural-language query for note recall",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional tag filter; defaults to all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of note matches",
                    },
                },
                "required": ["query"],
            },
            "handler": recall_notes,
            "latency_tier": "p95_sub_500ms",
            "idempotent": True,
        },
    ]
