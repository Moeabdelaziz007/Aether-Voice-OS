from __future__ import annotations

from types import SimpleNamespace

from core.ai.session.config_builder import build_session_config
from core.infra.config import AIConfig, GeminiModel


def test_build_session_config_applies_thinking_budget():
    facade = SimpleNamespace(
        _config=AIConfig(
            GOOGLE_API_KEY="k",
            _env_file=None,
            api_version="v1alpha",
            model=GeminiModel.LIVE_FLASH,
            thinking_budget=32,
            enable_search_grounding=False,
            proactive_audio=False,
            enable_affective_dialog=False,
            system_instruction="hi",
        ),
        _tool_router=None,
        _soul=None,
        _build_system_instruction=lambda: "sys",
    )
    config = build_session_config(facade)
    assert config.thinking_config.thinking_budget == 32
