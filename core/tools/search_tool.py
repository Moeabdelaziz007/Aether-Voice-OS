"""
Aether Voice OS — Search Tool (Google Search Grounding).

Enables Gemini to ground its responses in real-time web results.
This prevents hallucination by giving the model access to live
information via Google Search.

Architecture:
  User asks a factual question → Gemini uses Google Search →
  Returns grounded response with citations.

Note: Google Search grounding is declared as a special tool type
in LiveConnectConfig, NOT as a function declaration. The model
automatically decides when to use it based on the query.
"""

from __future__ import annotations

import logging

from google.genai import types

logger = logging.getLogger(__name__)


def get_search_tool() -> types.Tool:
    """
    Create a Google Search grounding tool for Gemini.

    This is added alongside function-calling tools in
    the LiveConnectConfig. When Gemini needs factual info,
    it will automatically query Google Search and include
    the results in its response.

    Returns:
        A types.Tool configured for Google Search grounding.
    """
    return types.Tool(google_search=types.GoogleSearch())


def get_tools() -> list[dict]:
    """
    Module-level ADK registration.

    Note: Google Search is a built-in Gemini tool, not a function
    that needs a handler. It's registered separately in the session
    config via get_search_tool(). This get_tools() is provided for
    consistency with the module pattern but returns an empty list.
    """
    return []
