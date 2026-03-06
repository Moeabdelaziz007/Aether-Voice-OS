from unittest.mock import MagicMock

from core.infra.config import AIConfig, AudioConfig, GatewayConfig
from core.infra.transport.gateway import AetherGateway


def _build_gateway() -> AetherGateway:
    ai_config = AIConfig(GOOGLE_API_KEY="test", _env_file=None)
    audio_config = AudioConfig()
    tool_router = MagicMock()
    hive = MagicMock()
    hive.set_pre_warm_callback = MagicMock()
    return AetherGateway(GatewayConfig(), ai_config, audio_config, tool_router, hive)


def test_verify_jwt_rejects_when_secret_missing(monkeypatch):
    gw = _build_gateway()
    monkeypatch.delenv("AETHER_JWT_SECRET", raising=False)
    monkeypatch.delenv("AETHER_JWT_ISSUER", raising=False)
    monkeypatch.delenv("AETHER_JWT_AUDIENCE", raising=False)
    assert gw._verify_jwt("dummy.token.value") is False


def test_verify_jwt_rejects_when_required_claims_missing(monkeypatch):
    gw = _build_gateway()
    monkeypatch.setenv("AETHER_JWT_SECRET", "secret")
    monkeypatch.setenv("AETHER_JWT_ISSUER", "aether")
    monkeypatch.setenv("AETHER_JWT_AUDIENCE", "aether-clients")

    # token missing `exp` and `sub`
    import jwt

    token = jwt.encode({"iss": "aether", "aud": "aether-clients", "iat": 1700000000}, "secret", algorithm="HS256")
    assert gw._verify_jwt(token) is False


def test_verify_jwt_rejects_wrong_issuer_audience(monkeypatch):
    gw = _build_gateway()
    monkeypatch.setenv("AETHER_JWT_SECRET", "secret")
    monkeypatch.setenv("AETHER_JWT_ISSUER", "aether")
    monkeypatch.setenv("AETHER_JWT_AUDIENCE", "aether-clients")

    import jwt
    import time

    token = jwt.encode(
        {
            "iss": "wrong-issuer",
            "aud": "wrong-audience",
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "sub": "client-123",
        },
        "secret",
        algorithm="HS256",
    )
    assert gw._verify_jwt(token) is False
