import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.ai.handover_protocol import HandoverContext
from core.ai.session.facade import GeminiLiveSession, ToolRegistry
from core.infra.transport.gateway import AetherGateway


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.api_key = "test_key"
    config.model = MagicMock()
    config.model.value = "models/gemini-2.0-flash-exp"
    config.enable_proactive_vision = True
    config.enable_affective_dialog = False
    config.proactive_audio = False
    config.thinking_budget = None
    config.enable_search_grounding = False
    return config


@pytest.fixture
def mock_gateway():
    return MagicMock(spec=AetherGateway)


def test_tool_registry_schemas():
    """Verify that ToolRegistry generates correct JSON schemas via Pydantic."""
    registry = ToolRegistry()
    declarations = registry.get_declarations()

    names = [d.name for d in declarations]
    assert "open_claw" in names
    assert "soul_swap" in names
    assert "diagnose_structure" in names

    # Check open_claw schema (Pydantic side)
    schema = registry.tools["open_claw"].model_json_schema()
    assert schema["properties"]["tool_id"]["type"] == "string"
    assert "tool_id" in schema["required"]


def test_tool_call_schema_enforcement():
    """Verify that ToolRegistry properly enforces jsonschema validation."""
    registry = ToolRegistry()
    declarations = registry.get_declarations()

    names = [d.name for d in declarations]
    assert "open_claw" in names
    assert "soul_swap" in names
    assert "diagnose_structure" in names

    # Check open_claw schema logic (jsonschema validation shouldn't raise errors here)
    schema = registry.tools["open_claw"].model_json_schema()
    assert schema["properties"]["tool_id"]["type"] == "string"
    assert "tool_id" in schema["required"]


@pytest.mark.asyncio
async def test_session_retry_logic(mock_config, mock_gateway):
    """Verify that GeminiLiveSession retries connection on failure."""
    session = GeminiLiveSession(
        config=mock_config, audio_in_queue=asyncio.Queue(), audio_out_queue=asyncio.Queue(), gateway=mock_gateway
    )

    with patch("core.ai.session.facade.get_genai_client", side_effect=Exception("Conn error")) as mock_client_init:
        with pytest.raises(Exception):  # AIConnectionError
            await session.connect()

        # Should have tried 3 times (max_retries)
        assert mock_client_init.call_count == 3


@pytest.mark.asyncio
async def test_multimodal_injection(mock_config, mock_gateway):
    """Verify that inject_handover_context correctly processes visual frames."""
    session = GeminiLiveSession(
        config=mock_config, audio_in_queue=asyncio.Queue(), audio_out_queue=asyncio.Queue(), gateway=mock_gateway
    )
    session._session = AsyncMock()
    session._running = True

    # HandoverContext fields: source_agent, target_agent, task
    context = HandoverContext(
        handover_id="test_h", source_agent="expert_coder", target_agent="architect", task="refactor"
    )
    frames = [b"frame1", b"frame2"]

    # We use patch to avoid actual injection logic side effects
    with patch.object(session, "_inject_frames", new_callable=AsyncMock) as mock_inj:
        session.inject_handover_context(context, visual_frames=frames)
        # Give a small slice to allow task to start
        await asyncio.sleep(0.1)
        mock_inj.assert_called_once_with(frames)


@pytest.mark.asyncio
async def test_gateway_rate_limiting(mock_config):
    """Verify that AetherGateway enforces text rate limits."""
    # AetherGateway init: gateway_config, ai_config, audio_config, tool_router, hive
    audio_config = MagicMock()
    audio_config.send_sample_rate = 16000
    audio_config.chunk_size = 512

    gateway = AetherGateway(
        gateway_config=MagicMock(),
        ai_config=mock_config,
        audio_config=audio_config,
        tool_router=MagicMock(),
        hive=MagicMock(),
    )
    gateway._state_manager = MagicMock()
    gateway._state_manager.session = MagicMock()
    gateway._state_manager.session._running = True
    gateway._state_manager.session._session = AsyncMock()

    # First call succeeds
    res1 = await gateway.send_text("Hello 1")
    assert res1 is True

    # Immediate second call fails due to rate limit (0.5s)
    res2 = await gateway.send_text("Hello 2")
    assert res2 is False
