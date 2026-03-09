"""
Aether Voice OS — Gmail Skills.
Integration for Gmail using Google ADK patterns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from core.infra.config import load_config

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
    """
    Mock implementation for sending an email.
    Returns A2A status codes for robust error handling.
    """
    config = load_config()
    # Mocking usage of config.ai.api_key for Google API initialization
    logger.info(
        "Attempting to send email to %s using key ...%s",
        to,
        config.ai.api_key[-4:] if config.ai.api_key else "None",
    )
    # Mock Auth / Quota failure for testing robust error handling (A2A Protocol)
    if "error" in to.lower():
        return {
            "status": "error",
            "message": "Quota Exceeded or Auth Failure.",
            "x-a2a-status": 429,
        }

    return {
        "status": "success",
        "message": f"Email successfully sent to {to}",
        "x-a2a-status": 200,
    }


async def search_emails(query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
    """
    Mock implementation for searching emails.
    Returns A2A status codes for robust error handling.
    """
    config = load_config()
    # Mocking usage of config.ai.api_key for Google API initialization
    logger.info(
        "Searching emails with query: '%s' using key ...%s",
        query,
        config.ai.api_key[-4:] if config.ai.api_key else "None",
    )

    # Mock Auth / Quota failure
    if "error" in query.lower():
        return {
            "status": "error",
            "message": "Auth Failure.",
            "x-a2a-status": 401,
        }

    return {
        "status": "success",
        "emails": [
            {"id": "1", "subject": "Meeting Notes", "snippet": "Here are the notes..."},
            {"id": "2", "subject": "Project Update", "snippet": "The project is..."},
        ],
        "message": f"Found 2 emails matching '{query}'.",
        "x-a2a-status": 200,
    }


def get_tools() -> list[dict]:
    """
    Module-level tool registration.
    Called by ToolRouter.register_module() to auto-discover all tools.
    """
    return [
        {
            "name": "send_email",
            "description": (
                "Send an email to a recipient with a subject and body. "
                "Use when the user asks to email someone."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content",
                    },
                },
                "required": ["to", "subject", "body"],
            },
            "handler": send_email,
            "latency_tier": "p95_sub_2s",
            "idempotent": False,
        },
        {
            "name": "search_emails",
            "description": (
                "Search the user's Gmail inbox using a query string. "
                "Use when the user asks to find an email or check their inbox."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'from:boss@company.com')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to return",
                    },
                },
                "required": ["query"],
            },
            "handler": search_emails,
            "latency_tier": "p95_sub_2s",
            "idempotent": True,
        },
    ]
