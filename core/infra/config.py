import base64
import json
import logging
import os
from enum import Enum
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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

    # Dynamic AEC parameters (adjustable during runtime)
    aec_step_size: float = 0.5
    aec_filter_length_ms: float = 100.0
    aec_convergence_threshold_db: float = 15.0

    # Dynamic VAD parameters
    vad_energy_threshold: float = 0.02
    vad_soft_threshold_multiplier: float = 0.7

    # Jitter buffer parameters
    jitter_buffer_target_ms: float = 60.0
    jitter_buffer_max_ms: float = 200.0

    # Mute/unmute timing
    mute_delay_samples: int = 800
    unmute_delay_samples: int = 1200

    @field_validator("send_sample_rate", "receive_sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: int) -> int:
        """Ensure sample rate is a supported value."""
        supported = [8000, 16000, 24000, 44100, 48000]
        if v not in supported:
            raise ValueError(f"Sample rate {v} not supported. Use one of: {supported}")
        return v

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, v: int) -> int:
        """Ensure chunk size is power-of-2 and reasonable."""
        if v < 64 or v > 8192:
            raise ValueError(f"Chunk size must be 64-8192, got {v}")
        if v & (v - 1) != 0:
            raise ValueError(f"Chunk size should be power-of-2, got {v}")
        return v

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: int) -> int:
        """Aether supports mono only currently."""
        if v != 1:
            raise ValueError(
                f"Aether currently supports mono (channels=1) only, got {v}"
            )
        return v

    @field_validator("aec_step_size")
    @classmethod
    def validate_aec_step_size(cls, v: float) -> float:
        """NLMS step size must be in (0, 1]."""
        if not 0.0 < v <= 1.0:
            raise ValueError(f"AEC step_size must be in (0, 1], got {v}")
        return v

    @field_validator("aec_filter_length_ms")
    @classmethod
    def validate_filter_length(cls, v: float) -> float:
        """Filter length should be reasonable."""
        if not 10.0 <= v <= 500.0:
            raise ValueError(f"Filter length must be 10-500ms, got {v}")
        return v

    @field_validator("aec_convergence_threshold_db")
    @classmethod
    def validate_erle_threshold(cls, v: float) -> float:
        """ERLE threshold should be achievable."""
        if not 5.0 <= v <= 30.0:
            raise ValueError(f"ERLE threshold must be 5-30dB, got {v}")
        return v

    @field_validator("vad_energy_threshold")
    @classmethod
    def validate_vad_threshold(cls, v: float) -> float:
        """VAD threshold must be positive and small."""
        if not 0.001 <= v <= 0.5:
            raise ValueError(f"VAD threshold must be 0.001-0.5, got {v}")
        return v

    @field_validator("jitter_buffer_target_ms", "jitter_buffer_max_ms")
    @classmethod
    def validate_jitter_ms(cls, v: float) -> float:
        """Jitter buffer timing must be reasonable."""
        if not 10.0 <= v <= 500.0:
            raise ValueError(f"Jitter buffer must be 10-500ms, got {v}")
        return v

    @model_validator(mode="after")
    def validate_jitter_consistency(self) -> "AudioConfig":
        """Ensure target <= max for jitter buffer."""
        if self.jitter_buffer_target_ms > self.jitter_buffer_max_ms:
            raise ValueError(
                f"Jitter target ({self.jitter_buffer_target_ms}ms) "
                f"cannot exceed max ({self.jitter_buffer_max_ms}ms)"
            )
        return self

    @model_validator(mode="after")
    def validate_sample_rate_ratio(self) -> "AudioConfig":
        """Ensure receive/send ratio is reasonable."""
        ratio = self.receive_sample_rate / self.send_sample_rate
        if ratio not in [1.0, 1.5, 2.0, 3.0]:
            logger.warning(
                f"Unusual sample rate ratio: {ratio:.2f}. "
                f"Typical ratios: 1.5 (24k/16k) or 2.0 (48k/24k)"
            )
        return self


class GeminiModel(str, Enum):
    """Model IDs for Gemini 2.5 specialized intelligence matrix."""

    # Real-time Voice & Audio Reasoning
    LIVE_FLASH = "gemini-2.0-flash-exp"
    FLASH_NATIVE_AUDIO = "gemini-2.5-flash-native-audio-preview-12-2025"
    FLASH_TTS = "gemini-2.5-flash-tts-preview"

    # Multi-step Reasoning & Coding
    PRO = "gemini-2.5-pro-preview-03-2026"
    FLASH = "gemini-2.5-flash-preview-09-2025"
    LITE = "gemini-2.5-flash-lite-preview"

    # Agentic & Specialized Models
    COMPUTER_USE = "gemini-2.5-computer-use-preview-10-2025"
    DEEP_RESEARCH = "gemini-deep-research-preview"
    EMBEDDINGS = "text-embedding-004"
    ROBOTICS = "gemini-robotics-er-1.5-preview"


def _get_env_file():
    """Safely get the .env file path if it's accessible."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
    )
    if os.path.exists(path):
        try:
            # Check if we have permission to read it
            with open(path, "r"):
                pass
            return path
        except (PermissionError, OSError):
            pass
    return None


class AIConfig(BaseSettings):
    """AI runtime settings loaded from environment via pydantic-settings.

    Controls model selection, API version, grounding, affective/backchannel
    features, proactive vision/audio, and optional thinking budget. Reads
    GOOGLE_API_KEY and related fields from a .env file by default.
    """

    api_key: str = Field(
        ...,
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY", "api_key")
    )
    model: GeminiModel = GeminiModel.LIVE_FLASH
    api_version: str = "v1"
    enable_affective_dialog: bool = True
    proactive_audio: bool = True
    enable_search_grounding: bool = True
    enable_proactive_vision: bool = True
    thinking_budget: Optional[int] = None
    voice_name: str = "Aoede"
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
        env_file=_get_env_file(),
        extra="ignore",
        env_file_encoding="utf-8",
        env_file_required=False,
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
    log_file: Optional[str] = "logs/aether.log"
    admin_port: int = 18790
    packages_dir: str = "packages"

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_nested_delimiter="__",
        extra="ignore",
        env_file_required=False,
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
            logger.warning(f"Failed to load {json_path}: {e}")

    # EMERGENCY: If GOOGLE_API_KEY is missing, providing a mock ONLY IF benchmarking is explicit
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        if os.getenv("AETHER_BENCHMARK_MODE", "false").lower() == "true":
            os.environ["GOOGLE_API_KEY"] = "AIza_MOCK_KEY_FOR_BENCHMARK"

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
