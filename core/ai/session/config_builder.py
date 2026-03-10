from __future__ import annotations

import logging

from google.genai import types

logger = logging.getLogger(__name__)


def build_session_config(session) -> types.LiveConnectConfig:
    """Build the Gemini Live session config from facade state."""
    tools = []

    if session._tool_router and session._tool_router.count > 0:
        declarations = session._tool_router.get_declarations()
        tools.append(types.Tool(function_declarations=declarations))
        logger.info(
            "Session configured with %d tools: %s",
            len(declarations),
            session._tool_router.names,
        )

    if session._config.enable_search_grounding:
        tools.append(types.Tool(google_search=types.GoogleSearch()))
        logger.info("Google Search grounding enabled")

    system_instruction = session._build_system_instruction()

    speech_config = None
    if session._soul and hasattr(session._soul, "manifest") and session._soul.manifest.voice_id:
        voice_name = session._soul.manifest.voice_id
        logger.info("A2A [SESSION] Applying Expert Voice: %s", voice_name)
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name))
        )

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=system_instruction,
        tools=tools,
        speech_config=speech_config,
    )

    if session._config.enable_affective_dialog:
        config.enable_affective_dialog = True
    if session._config.proactive_audio:
        config.proactivity = {"proactive_audio": True}
    if session._config.thinking_budget is not None:
        config.thinking_config = types.ThinkingConfig(
            thinking_budget=session._config.thinking_budget,
        )

    # Required for real-time transcript overlay
    config.input_audio_transcription = True
    config.output_audio_transcription = True

    return config
