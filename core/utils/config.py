import base64
import json
import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseModel):
    mic_queue_max: int = 5
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 512
    format_width: int = 2
    vad_window_sec: float = 5.0
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None


from enum import Enum


class GeminiModel(str, Enum):
    FLASH_NATIVE_AUDIO = "gemini-2.5-flash-native-audio-preview-12-2025"
    LIVE_FLASH = "gemini-live-2.5-flash-preview"


class AIConfig(BaseSettings):
    api_key: str = Field(..., alias="GOOGLE_API_KEY")
    model: GeminiModel = GeminiModel.LIVE_FLASH
    enable_affective_dialog: bool = True
    proactive_audio: bool = True
    enable_search_grounding: bool = True
    thinking_budget: int = 0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GatewayConfig(BaseModel):
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
    # This allows passing the full JSON key as a single env var in CI/CD (e.g. Vercel/Railway)
    firebase_creds_base64: Optional[str] = Field(
        None, alias="FIREBASE_CREDENTIALS_BASE64"
    )

    log_level: str = "INFO"
    packages_dir: str = "packages"

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
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
        return AetherConfig()
    except Exception as e:
        # Re-raise as EnvironmentError for test compatibility if it's a validation error
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
