"""
Aether Voice OS — Configuration.

Single source of truth for all runtime settings.
Loaded from environment variables and .env files via pydantic-settings.
Frozen after initialization (immutable at runtime).
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseSettings):
    """Audio capture and playback settings."""
    model_config = SettingsConfigDict(env_prefix="AETHER_AUDIO_")

    send_sample_rate: int = Field(16_000, description="Mic input sample rate (Hz)")
    receive_sample_rate: int = Field(24_000, description="Gemini output sample rate (Hz)")
    channels: int = Field(1, description="Mono audio")
    chunk_size: int = Field(512, description="PyAudio frames per buffer read")
    format_width: int = Field(2, description="Bytes per sample (2 = 16-bit)")
    mic_queue_max: int = Field(5, description="Back-pressure limit on mic queue")


class GeminiModel(str, Enum):
    """Supported Gemini Live models."""
    FLASH_NATIVE_AUDIO = "gemini-2.5-flash-native-audio-preview-12-2025"
    LIVE_FLASH = "gemini-live-2.5-flash-preview"


class AIConfig(BaseSettings):
    """Gemini Live API settings."""
    model_config = SettingsConfigDict(env_prefix="AETHER_AI_")

    api_key: str = Field(..., description="Google API key (GOOGLE_API_KEY also accepted)")
    model: GeminiModel = Field(
        GeminiModel.FLASH_NATIVE_AUDIO,
        description="Gemini model ID",
    )
    api_version: str = Field("v1alpha", description="API version for advanced features")
    enable_affective_dialog: bool = Field(True, description="Emotion-aware responses")
    proactive_audio: bool = Field(True, description="Model decides when to respond")
    enable_proactive_vision: bool = Field(False, description="Enable proactive vision context")
    enable_search_grounding: bool = Field(True, description="Google Search grounding for fact-checking")
    thinking_budget: Optional[int] = Field(0, description="Thinking token budget (0 disables for minimal latency)")
    system_instruction: str = Field(
        "You are Aether — a calm, wise, deeply technical AI companion. "
        "You speak Arabic naturally and switch to English for code. "
        "You are a philosophical systems architect.",
        description="System prompt for the voice session",
    )


class GatewayConfig(BaseSettings):
    """WebSocket gateway settings."""
    model_config = SettingsConfigDict(env_prefix="AETHER_GW_")

    host: str = Field("0.0.0.0", description="Bind address")
    port: int = Field(18789, description="WebSocket port")
    tick_interval_s: float = Field(15.0, description="Heartbeat interval (seconds)")
    handshake_timeout_s: float = Field(5.0, description="Auth handshake timeout")
    max_missed_ticks: int = Field(2, description="Ticks missed before pruning client")


class AetherConfig(BaseSettings):
    """
    Root configuration — composes all sub-configs.

    Loads from:
      1. Environment variables (highest priority)
      2. .env file in project root
      3. Defaults defined here (lowest priority)
    """
    model_config = SettingsConfigDict(
        # We handle env_file manually in load_config() to bypass TCC/Sandbox stat() blocks
        env_file=None, 
        case_sensitive=False,
        extra="ignore",
    )

    # Sub-configs are instantiated independently so each reads its own env prefix
    audio: AudioConfig = Field(default_factory=AudioConfig)
    ai: AIConfig = Field(default_factory=lambda: AIConfig(api_key=""))  # type: ignore[arg-type]
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)

    # Identity
    packages_dir: str = Field("brain/packages", description="Path to .ath package registry")
    log_level: str = Field("INFO", description="Logging level")


def load_config() -> AetherConfig:
    """
    Factory that constructs config with proper API key resolution.

    Bypasses macOS Sandbox issues by falling back to aether_runtime_config.json
    if .env or environment variables are blocked/missing.
    """
    import os
    import json
    from pathlib import Path

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("AETHER_AI_API_KEY")

    # Sandbox Bypass: Try reading from our custom JSON if env is empty
    if not api_key:
        fallback_path = Path("aether_runtime_config.json")
        if fallback_path.exists():
            try:
                with open(fallback_path, "r") as f:
                    data = json.load(f)
                    api_key = data.get("GOOGLE_API_KEY")
                    # Inject other keys into environ so sub-configs see them
                    for k, v in data.items():
                        if k not in os.environ:
                            os.environ[k] = str(v)
                if api_key:
                    from logging import getLogger
                    getLogger(__name__).info("Bypassed Sandbox: Loaded config from JSON fallback")
            except Exception:
                pass

    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY or AETHER_AI_API_KEY must be set. "
            "Sandbox restriction: .env is blocked. "
            "Created aether_runtime_config.json to bypass — ensure it has your API key."
        )

    ai = AIConfig(api_key=api_key)
    return AetherConfig(ai=ai)
