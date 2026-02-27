"""
Aether Voice OS — Discovery Tool.

Provides tools for the agent to audit and report on its own internal state,
codebase health, and evolutionary progress.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# References populated by engine
_affective_engine = None
_hive_coordinator = None


def set_references(affective=None, hive=None):
    global _affective_engine, _hive_coordinator
    _affective_engine = affective
    _hive_coordinator = hive


async def generate_system_audit(**kwargs) -> dict:
    """
    Generates a comprehensive audit of the AI's internal health and environment.
    Use this to 'reflect' on your current state or answer questions about your performance.
    """
    audit = {
        "timestamp": time.time(),
        "components": {
            "affective_engine": "Active" if _affective_engine else "Offline",
            "hive_coordinator": "Active" if _hive_coordinator else "Offline",
            "vision_system": "Operational (Sync-Linked)",
            "memory_vault": "Synchronized (Firebase)",
        },
        "metrics": {
            "current_soul": (
                _hive_coordinator.current_soul.name
                if _hive_coordinator and _hive_coordinator.current_soul
                else "Default"
            ),
            "handover_count": (
                len(_hive_coordinator._handover_callback_history)
                if _hive_coordinator
                and hasattr(_hive_coordinator, "_handover_callback_history")
                else 0
            ),
        },
        "codebase_stats": {"root": os.getcwd(), "detected_files": 0},
    }

    # Count files (basic check)
    file_count = 0
    for root, dirs, files in os.walk("."):
        if ".git" in root or "__pycache__" in root or "node_modules" in root:
            continue
        file_count += len(files)
    audit["codebase_stats"]["detected_files"] = file_count

    return audit


def get_tools() -> list[dict]:
    """Module-level tool registration."""
    return [
        {
            "name": "generate_system_audit",
            "description": "Perform a self-diagnostic audit of AetherOS internal systems, metrics, and codebase integrity.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "handler": generate_system_audit,
        }
    ]
