import base64
import json
import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseModel):
    mic_queue_max: int = 20
    send_sample_rate: int = 16000
    vad_window_sec: float = 5.0
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None


class AIConfig(BaseSettings):
    api_key: str = Field(..., alias="GOOGLE_API_KEY")
    model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GatewayConfig(BaseModel):
    port: int = 8080


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
    """Factory function to load and validate config."""
    return AetherConfig()


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
