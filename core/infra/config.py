import base64
import json
import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseModel):
    """Audio I/O settings for capture/playback.

    Assumptions: mono PCM16, 16kHz capture (send_sample_rate), 24kHz playback
    (receive_sample_rate). chunk_size configures callback buffer size; queue
    sizes are kept small to bound latency.
    """
    mic_queue_max: int = 5
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 512
    format_width: int = 2
    vad_window_sec: float = 5.0
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None


class GeminiModel(str, Enum):
    """Model IDs for Gemini Live/Native Audio used by AIConfig."""
    FLASH_NATIVE_AUDIO = "gemini-2.5-flash-native-audio-preview-12-2025"
    LIVE_FLASH = "gemini-live-2.5-flash-preview"


class AIConfig(BaseSettings):
    """AI runtime settings loaded from environment via pydantic-settings.

    Controls model selection, API version, grounding, affective/backchannel
    features, proactive vision/audio, and optional thinking budget. Reads
    GOOGLE_API_KEY and related fields from a .env file by default.
    """
    api_key: str = Field(..., alias="GOOGLE_API_KEY")
    model: GeminiModel = GeminiModel.LIVE_FLASH
    api_version: str = "v1alpha"
    enable_affective_dialog: bool = True
    proactive_audio: bool = True
    enable_search_grounding: bool = True
    enable_proactive_vision: bool = True
    thinking_budget: Optional[int] = None
    system_instruction: str = (
        "You are Aether Sovereign, the ultimate neural interface and Autonomous "
        "Site Reliability Architect (ASRA). Built on Google ADK and Gemini 2.5 "
        "Flash Native Audio, you bridge the gap between human intention and "
        "technical execution. Mission: Proactive monitoring, diagnosis, and "
        "autonomous repair of complex systems. Framework: Use specialized ADK "
        "Agents (ArchitectAgent, DebuggerAgent) for deep domain tasks. "
        "Interaction: Maintain a calm, senior-architect tone. Respond in Arabic "
        "if the user speaks Arabic. Efficiency: Prioritize sub-200ms latency and "
        "high-fidelity tool execution."
    )

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        extra="ignore",
        env_file_encoding="utf-8",
    )


class GatewayConfig(BaseModel):
    """Gateway parameters for UI/gateway transport and health.

    Controls bind host/port, heartbeat timing, and receive sample rate for
    gateway streams.
    """
    host: str = "0.0.0.0"
    port: int = 18789
    tick_interval_s: float = 15.0
    max_missed_ticks: int = 2
    handshake_timeout_s: float = 10.0
    receive_sample_rate: int = 16000


class AetherConfig(BaseSettings):
    """
    Main configuration loaded from environment variables.
    """

    audio: AudioConfig = AudioConfig()
    ai: AIConfig = Field(default_factory=AIConfig)
    gateway: GatewayConfig = GatewayConfig()

    # Security: Base64 encoded Service Account JSON
    # This allows passing the full JSON key as a single env var in CI/CD
    # (e.g. Vercel/Railway).
    firebase_creds_base64: Optional[str] = Field(
        None, alias="FIREBASE_CREDENTIALS_BASE64"
    )

    log_level: str = "INFO"
    packages_dir: str = "packages"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_nested_delimiter="__", 
        extra="ignore",
    )


def load_config() -> AetherConfig:
    """Factory function to load and validate config with JSON fallback."""
    json_path = "aether_runtime_config.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
                for k, v in data.items():
                    if k not in os.environ:
                        os.environ[k] = str(v)
        except Exception as e:
            print(f"Warning: Failed to load {json_path}: {e}")

    try:
        # 1. Try with .env loading (standard local dev)
        return AetherConfig()
    except (PermissionError, OSError):
        # 2. Try without .env loading (restricted CI/Docker)
        try:
            return AetherConfig(_env_file=None)
        except Exception as e:
            # 3. Last resort fallback
            raise OSError(f"Critical configuration missing or restricted: {e}")
    except Exception as e:
        if "GOOGLE_API_KEY" not in os.environ and not os.path.exists(".env"):
            raise ValueError("GOOGLE_API_KEY is required and no .env file found.") from e
        # Re-try without env file if it's a validation error or something else
        try:
            return AetherConfig(_env_file=None)
        except Exception:
            raise OSError(f"Sandbox restriction or missing config: {e}")


def get_firebase_cert(config: AetherConfig) -> Optional[dict]:
    """
    Decodes the Base64 encoded Firebase credentials.
    Returns a dictionary suitable for firebase_admin.credentials.Certificate.
    """
    if config.firebase_creds_base64:
        try:
            # Decode Base64 -> JSON String -> Dict
            json_str = base64.b64decode(config.firebase_creds_base64).decode("utf-8")
            return json.loads(json_str)
        except Exception as e:
            print(f"CRITICAL: Failed to decode Firebase credentials: {e}")
            return None
    return None
