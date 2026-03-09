"""
Aether Voice OS — Calendar Skills.
Integration for Google Calendar using Google ADK patterns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from core.infra.config import load_config

logger = logging.getLogger(__name__)


async def create_event(
    title: str,
    start_time: str,
    end_time: str,
    attendees: Optional[list[str]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Mock implementation for creating a calendar event.
    Returns A2A status codes for robust error handling.
    """
    config = load_config()
    # Mocking usage of config.ai.api_key for Google API initialization
    logger.info(
        "Attempting to create event '%s' at %s using key ...%s",
        title,
        start_time,
        config.ai.api_key[-4:] if config.ai.api_key else "None",
    )

    # Mock Auth / Quota failure for testing robust error handling (A2A Protocol)
    if "error" in title.lower():
        return {
            "status": "error",
            "message": "Quota Exceeded or Auth Failure.",
            "x-a2a-status": 429,
        }

    return {
        "status": "success",
        "message": f"Event '{title}' successfully created at {start_time}",
        "x-a2a-status": 200,
    }


async def list_events(
    time_min: str, time_max: str, max_results: int = 5, **kwargs
) -> Dict[str, Any]:
    """
    Mock implementation for listing upcoming calendar events.
    Returns A2A status codes for robust error handling.
    """
    config = load_config()
    # Mocking usage of config.ai.api_key for Google API initialization
    logger.info(
        "Listing events between %s and %s using key ...%s",
        time_min,
        time_max,
        config.ai.api_key[-4:] if config.ai.api_key else "None",
    )

    # Mock Auth / Quota failure
    if "error" in time_min.lower():
        return {
            "status": "error",
            "message": "Auth Failure.",
            "x-a2a-status": 401,
        }

    return {
        "status": "success",
        "events": [
            {
                "id": "event_1",
                "summary": "Team Sync",
                "start": "10:00 AM",
                "end": "11:00 AM",
            },
            {
                "id": "event_2",
                "summary": "Project Review",
                "start": "1:00 PM",
                "end": "2:30 PM",
            },
        ],
        "message": f"Found 2 events between {time_min} and {time_max}.",
        "x-a2a-status": 200,
    }


def get_tools() -> list[dict]:
    """
    Module-level tool registration.
    Called by ToolRouter.register_module() to auto-discover all tools.
    """
    return [
        {
            "name": "create_event",
            "description": (
                "Create a new event on the user's Google Calendar with a title, "
                "start time, end time, and optional attendees. "
                "Use when the user asks to schedule a meeting or event."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or summary of the event",
                    },
                    "start_time": {
                        "type": "string",
                        "description": (
                            "Start time in ISO format "
                            "(e.g., '2023-10-27T10:00:00-07:00')"
                        ),
                    },
                    "end_time": {
                        "type": "string",
                        "description": (
                            "End time in ISO format "
                            "(e.g., '2023-10-27T11:00:00-07:00')"
                        ),
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses",
                    },
                },
                "required": ["title", "start_time", "end_time"],
            },
            "handler": create_event,
            "latency_tier": "p95_sub_2s",
            "idempotent": False,
        },
        {
            "name": "list_events",
            "description": (
                "List events from the user's Google Calendar between two dates. "
                "Use when the user asks what is on their schedule or calendar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_min": {
                        "type": "string",
                        "description": (
                            "Start of the time range in ISO format "
                            "(e.g., '2023-10-27T00:00:00-07:00')"
                        ),
                    },
                    "time_max": {
                        "type": "string",
                        "description": (
                            "End of the time range in ISO format "
                            "(e.g., '2023-10-28T00:00:00-07:00')"
                        ),
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return",
                    },
                },
                "required": ["time_min", "time_max"],
            },
            "handler": list_events,
            "latency_tier": "p95_sub_2s",
            "idempotent": True,
        },
    ]
