"""Focused bootstrap tests for AetherEngine composition."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.infra.config import AetherConfig, AIConfig, AudioConfig, GatewayConfig


@pytest.fixture
def mock_config() -> AetherConfig:
    """Create a minimal in-memory config for engine construction."""
    return AetherConfig(
        _env_file=None,
        ai=AIConfig(_env_file=None, GOOGLE_API_KEY="dummy-test-key"),
        audio=AudioConfig(),
        gateway=GatewayConfig(),
    )


def test_engine_bootstrap_composes_core_collaborators(mock_config, monkeypatch):
    """Engine constructor should compose gateway/hive/session without type errors."""

    class FakeVectorStore:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

        def load(self, _filepath) -> bool:
            return True

    monkeypatch.setattr("core.tools.vector_store.LocalVectorStore", FakeVectorStore)
    monkeypatch.setattr("core.engine.FirebaseConnector", MagicMock)

    from core.engine import AetherEngine

    engine = AetherEngine(config=mock_config)

    assert engine._gateway is not None
    assert engine._hive is not None
    assert engine._session is not None
