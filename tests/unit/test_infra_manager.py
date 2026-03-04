import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch


# We use a scoped approach to mock missing dependencies to avoid global side effects
# that could interfere with other tests in a real environment.
def setup_mocks():
    mock_modules = [
        "firebase_admin",
        "firebase_admin.credentials",
        "firebase_admin.firestore",
        "google.cloud.firestore",
        "numpy",
        "pydantic",
        "pydantic_settings",
        "websockets",
        "google.genai",
        "pyaudio",
        "watchdog",
        "watchdog.observers",
        "watchdog.events",
    ]
    for module_name in mock_modules:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()


# Initialize mocks for this module
setup_mocks()

import pytest  # noqa: E402

from core.logic.managers.infra import InfraManager  # noqa: E402


@pytest.fixture
def mock_gateway():
    gateway = MagicMock()
    gateway._bus = MagicMock()
    return gateway


@pytest.fixture
def infra_manager(mock_gateway):
    # We still want to patch these in the test to ensure they are the ones we control
    with (
        patch("core.logic.managers.infra.FirebaseConnector"),
        patch("core.logic.managers.infra.SREWatchdog"),
    ):
        manager = InfraManager(mock_gateway)
        return manager


# Note: Using asyncio.run(infra_manager.initialize()) instead of @pytest.mark.asyncio
# because pytest-asyncio is not available in the current environment.


def test_infra_manager_initialize_success(infra_manager):
    infra_manager._firebase.initialize = AsyncMock(return_value=True)
    infra_manager._firebase.start_session = AsyncMock()

    result = asyncio.run(infra_manager.initialize())

    assert result is True
    infra_manager._firebase.initialize.assert_called_once()
    infra_manager._firebase.start_session.assert_called_once()


def test_infra_manager_initialize_failure(infra_manager):
    infra_manager._firebase.initialize = AsyncMock(return_value=False)
    infra_manager._firebase.start_session = AsyncMock()

    result = asyncio.run(infra_manager.initialize())

    assert result is False
    infra_manager._firebase.initialize.assert_called_once()
    infra_manager._firebase.start_session.assert_not_called()


def test_infra_manager_start_watchdog(infra_manager):
    infra_manager.start_watchdog()
    infra_manager._watchdog.start.assert_called_once()


def test_infra_manager_stop(infra_manager):
    infra_manager.stop()
    infra_manager._watchdog.stop.assert_called_once()


def test_infra_manager_end_session(infra_manager):
    infra_manager._firebase.is_connected = True
    infra_manager._firebase.end_session = AsyncMock()
    mock_router = MagicMock()
    mock_router.names = ["tool1", "tool2"]
    mock_router.count = 2

    asyncio.run(infra_manager.end_session(mock_router))

    infra_manager._firebase.end_session.assert_called_once_with(
        {
            "tools_used": ["tool1", "tool2"],
            "tool_count": 2,
        }
    )


def test_infra_manager_end_session_disconnected(infra_manager):
    infra_manager._firebase.is_connected = False
    infra_manager._firebase.end_session = AsyncMock()
    mock_router = MagicMock()

    asyncio.run(infra_manager.end_session(mock_router))

    infra_manager._firebase.end_session.assert_not_called()
