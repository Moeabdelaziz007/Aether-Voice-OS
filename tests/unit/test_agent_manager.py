import asyncio
import logging
import sys
from unittest.mock import MagicMock, patch


def setup_mocks():
    mock_modules = [
        "firebase_admin",
        "firebase_admin.credentials",
        "firebase_admin.firestore",
        "google",
        "google.cloud",
        "google.cloud.firestore",
        "google.genai",
        "google.genai.types",
        "numpy",
        "opentelemetry",
        "opentelemetry.trace",
        "opentelemetry.metrics",
        "opentelemetry.trace.status",
        "opentelemetry.exporter",
        "opentelemetry.exporter.otlp",
        "opentelemetry.exporter.otlp.proto",
        "opentelemetry.exporter.otlp.proto.grpc",
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
        "opentelemetry.exporter.otlp.proto.grpc.metric_exporter",
        "opentelemetry.sdk",
        "opentelemetry.sdk.trace",
        "opentelemetry.sdk.trace.export",
        "opentelemetry.sdk.metrics",
        "opentelemetry.sdk.metrics.export",
        "opentelemetry.sdk.resources",
        "pydantic",
        "pydantic_settings",
        "websockets",
        "pyaudio",
        "watchdog",
        "watchdog.observers",
        "watchdog.events",
    ]
    for module_name in mock_modules:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()


setup_mocks()

import pytest  # noqa: E402

from core.logic.managers.agents import AgentManager  # noqa: E402

# We mock AetherConfig directly to avoid spec issues if it is mocked by sys.modules
# from core.infra.config import AetherConfig


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.packages_dir = "test_dir"
    config.ai = MagicMock()
    config.ai.api_key = "test_key"
    return config


@pytest.fixture
def agent_manager(mock_config):
    mock_router = MagicMock()
    mock_on_handover = MagicMock()

    with (
        patch("core.logic.managers.agents.AetherRegistry"),
        patch("core.logic.managers.agents.HiveCoordinator"),
    ):
        manager = AgentManager(mock_config, mock_router, mock_on_handover)
        return manager


def test_on_package_change_hot_reload(agent_manager, caplog):
    caplog.set_level(logging.INFO)

    asyncio.run(agent_manager._on_package_change("test_pkg", {"some": "data"}))

    assert "Hot-Reloading package: test_pkg" in caplog.text


def test_on_package_change_unload(agent_manager, caplog):
    caplog.set_level(logging.INFO)

    asyncio.run(agent_manager._on_package_change("test_pkg", None))

    assert "Unloading package: test_pkg" in caplog.text


def test_scan_registry(agent_manager):
    agent_manager.scan_registry()
    agent_manager._registry.scan.assert_called_once()
    agent_manager._registry.start_watcher.assert_called_once()


def test_stop_watcher(agent_manager):
    agent_manager.stop_watcher()
    agent_manager._registry.stop_watcher.assert_called_once()
