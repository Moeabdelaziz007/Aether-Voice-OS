"""
Aether Voice OS — System Tool.

Local system actions that the agent can perform.
These run directly on the host machine, providing
the agent with awareness of time, date, and basic
environment information.

All functions are pure — no side effects beyond returning data.
"""
from __future__ import annotations

import logging
import platform
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def get_current_time(**kwargs) -> dict:
    """
    Returns the current date and time.

    This is one of the most commonly invoked tools —
    when a user asks "What time is it?" Gemini emits
    this function call.
    """
    now = datetime.now()
    utc_now = datetime.now(timezone.utc)

    return {
        "local_time": now.strftime("%I:%M %p"),
        "local_date": now.strftime("%A, %B %d, %Y"),
        "utc_time": utc_now.strftime("%H:%M:%S UTC"),
        "timezone": str(now.astimezone().tzinfo),
        "unix_timestamp": int(now.timestamp()),
    }


async def get_system_info(**kwargs) -> dict:
    """Returns basic information about the host system."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


async def run_timer(minutes: int = 1, label: str = "Timer", **kwargs) -> dict:
    """
    Acknowledge a timer request.

    Note: The actual countdown is informational — we return
    confirmation so Gemini can tell the user. A real timer
    would require a background scheduler integration.
    """
    end_time = datetime.now()
    end_time = end_time.replace(minute=end_time.minute + minutes)

    return {
        "status": "timer_set",
        "label": label,
        "duration_minutes": minutes,
        "will_fire_at": end_time.strftime("%I:%M %p"),
        "message": f"Timer '{label}' set for {minutes} minute(s).",
    }


def get_tools() -> list[dict]:
    """
    Module-level tool registration.

    Called by ToolRouter.register_module() to auto-discover
    all tools in this module.
    """
    return [
        {
            "name": "get_current_time",
            "description": (
                "Returns the current local time, date, and timezone. "
                "Use when the user asks what time or date it is."
            ),
            "parameters": {},
            "handler": get_current_time,
        },
        {
            "name": "get_system_info",
            "description": (
                "Returns information about the host system: OS, version, "
                "hostname. Use when the user asks about their computer."
            ),
            "parameters": {},
            "handler": get_system_info,
        },
        {
            "name": "run_timer",
            "description": (
                "Sets a timer for a specified number of minutes with a label. "
                "Use when the user asks to set a timer or reminder."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Number of minutes for the timer",
                    },
                    "label": {
                        "type": "string",
                        "description": "A label for the timer",
                    },
                },
                "required": ["minutes"],
            },
            "handler": run_timer,
        },
    ]
