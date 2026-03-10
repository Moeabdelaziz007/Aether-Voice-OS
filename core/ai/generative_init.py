"""
Aether Voice OS — Generative AI Configuration.

Centralized initialization for the google-genai SDK, providing
safe, optimized settings for the Live Agent's brain.
"""

import logging
import os
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def get_genai_client(api_key: Optional[str] = None, api_version: str = "v1alpha") -> genai.Client:
    """
    Initialize and return a production-ready Gemini client, optionally
    falling back to or wrapping google_adk initialization based on config.

    Args:
        api_key: Google AI API key. Defaults to GEMINI_API_KEY or GOOGLE_API_KEY.
        api_version: API version to use (e.g., 'v1alpha' for Live features).
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment")

    # Safe environment defaults
    if os.environ.get("AETHER_ENV") == "production":
        logger.info("Initializing genai client in production mode with strict bounds.")

    try:
        # Wrapper logic: we attempt to initialize genai.Client with safe boundaries
        client = genai.Client(api_key=key, http_options={"api_version": api_version})
        return client
    except Exception as e:
        logger.error(f"Failed to initialize google.genai Client: {e}")
        raise


def get_default_safety_settings() -> list[types.SafetySetting]:
    """Return standard safety boundaries for Aether."""
    return [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
    ]


def get_base_config() -> types.GenerateContentConfig:
    """Get the base generation config with Aether's personality constraints."""
    return types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=2048,
        safety_settings=get_default_safety_settings(),
    )
