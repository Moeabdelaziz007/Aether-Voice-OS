"""
Aether Voice OS — ADK Voice Tool Tests.

Tests the VoiceTool lifecycle (setup → execute → teardown),
state machine transitions, tool declaration, and tool call interface.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.config import AetherConfig, AIConfig, AudioConfig, GatewayConfig
from core.tools.voice_tool import VoiceState, VoiceTool

# ── Fixtures ────────────────────────────────────────────────


@pytest.fixture
def mock_config():
    """Create a valid test config without hitting real env vars."""
    return AetherConfig(
        ai=AIConfig(api_key="test-key-fake"),
        audio=AudioConfig(),
        gateway=GatewayConfig(),
    )


@pytest.fixture
def voice_tool():
    """Create a VoiceTool instance in IDLE state."""
    return VoiceTool()


# ── State Machine Tests ─────────────────────────────────────


class TestVoiceToolState:
    """Test VoiceTool state machine transitions."""

    def test_initial_state_is_idle(self, voice_tool):
        assert voice_tool.state == VoiceState.IDLE

    def test_is_active_when_idle(self, voice_tool):
        assert voice_tool.is_active is False

    def test_state_transitions_on_set(self, voice_tool):
        """Verify _set_state properly transitions."""
        voice_tool._set_state(VoiceState.INITIALIZING)
        assert voice_tool.state == VoiceState.INITIALIZING

        voice_tool._set_state(VoiceState.LISTENING)
        assert voice_tool.state == VoiceState.LISTENING
        assert voice_tool.is_active is True

    def test_is_active_states(self, voice_tool):
        """Only LISTENING, PROCESSING, SPEAKING are active."""
        for state in (VoiceState.LISTENING, VoiceState.PROCESSING, VoiceState.SPEAKING):
            voice_tool._set_state(state)
            assert voice_tool.is_active is True

        for state in (
            VoiceState.IDLE,
            VoiceState.INITIALIZING,
            VoiceState.ERROR,
            VoiceState.STOPPED,
        ):
            voice_tool._set_state(state)
            assert voice_tool.is_active is False

    def test_state_change_callback(self):
        """Verify on_state_change callback fires."""
        changes = []
        tool = VoiceTool(on_state_change=lambda old, new: changes.append((old, new)))
        tool._set_state(VoiceState.INITIALIZING)
        tool._set_state(VoiceState.LISTENING)
        assert len(changes) == 2
        assert changes[0] == (VoiceState.IDLE, VoiceState.INITIALIZING)
        assert changes[1] == (VoiceState.INITIALIZING, VoiceState.LISTENING)


# ── ADK Tool Declaration Tests ──────────────────────────────


class TestADKDeclaration:
    """Test ADK-compatible tool interface."""

    def test_tool_name(self, voice_tool):
        assert voice_tool.NAME == "aether_voice"

    def test_tool_description_not_empty(self, voice_tool):
        assert len(voice_tool.DESCRIPTION) > 10

    def test_adk_declaration_structure(self, voice_tool):
        decl = voice_tool.to_adk_declaration()
        assert decl["name"] == "aether_voice"
        assert "description" in decl
        assert "parameters" in decl
        assert decl["parameters"]["type"] == "object"
        assert "action" in decl["parameters"]["properties"]
        assert set(decl["parameters"]["properties"]["action"]["enum"]) == {
            "start",
            "stop",
            "status",
        }

    def test_adk_declaration_has_required_fields(self, voice_tool):
        decl = voice_tool.to_adk_declaration()
        assert "required" in decl["parameters"]
        assert "action" in decl["parameters"]["required"]


# ── Tool Call Interface Tests ────────────────────────────────


class TestToolCallInterface:
    """Test handle_tool_call dispatcher."""

    @pytest.mark.asyncio
    async def test_status_call(self, voice_tool):
        result = await voice_tool.handle_tool_call("status")
        assert result["state"] == "idle"
        assert result["is_active"] is False

    @pytest.mark.asyncio
    async def test_unknown_action(self, voice_tool):
        result = await voice_tool.handle_tool_call("invalid_action")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_stop_call_when_idle(self, voice_tool):
        result = await voice_tool.handle_tool_call("stop")
        assert "message" in result


# ── Setup / Teardown Lifecycle Tests ─────────────────────────


class TestLifecycle:
    """Test setup/teardown lifecycle."""

    @pytest.mark.asyncio
    async def test_setup_creates_components(self, mock_config):
        tool = VoiceTool(config=mock_config)
        await tool.setup()

        assert tool._audio_in is not None
        assert tool._audio_out is not None
        assert tool._capture is not None
        assert tool._playback is not None
        assert tool._session is not None
        assert tool._shutdown_event is not None
        assert tool.state == VoiceState.INITIALIZING

    @pytest.mark.asyncio
    async def test_teardown_sets_stopped(self, mock_config):
        tool = VoiceTool(config=mock_config)
        await tool.setup()
        await tool.teardown()
        assert tool.state == VoiceState.STOPPED

    @pytest.mark.asyncio
    async def test_teardown_without_setup(self):
        """Teardown should not crash even without setup."""
        tool = VoiceTool()
        await tool.teardown()
        assert tool.state == VoiceState.STOPPED


# ── Engine Tool Registration Tests ───────────────────────────


class TestEngineRegistration:
    """Test ADK tool registration with the engine."""

    def test_register_tool(self, mock_config):
        from core.engine import AetherEngine

        engine = AetherEngine(config=mock_config)
        tool = VoiceTool()
        engine.register_tool(tool.NAME, tool)
        assert "aether_voice" in engine._tools
        assert engine._tools["aether_voice"] is tool

    def test_register_multiple_tools(self, mock_config):
        from core.engine import AetherEngine

        engine = AetherEngine(config=mock_config)
        tool1 = VoiceTool()
        engine.register_tool("voice", tool1)
        engine.register_tool("search", MagicMock())
        assert len(engine._tools) == 2


# ── Interrupt / Barge-in Tests ───────────────────────────────


class TestBargeIn:
    """Test barge-in (interrupt) handling."""

    @pytest.mark.asyncio
    async def test_handle_interrupt_sets_listening(self, mock_config):
        tool = VoiceTool(config=mock_config)
        await tool.setup()
        tool._set_state(VoiceState.SPEAKING)
        tool._handle_interrupt()
        assert tool.state == VoiceState.LISTENING

    @pytest.mark.asyncio
    async def test_interrupt_drains_playback(self, mock_config):
        tool = VoiceTool(config=mock_config)
        await tool.setup()
        # Put some fake data in the output queue
        tool._audio_out.put_nowait(b"fake_audio_1")
        tool._audio_out.put_nowait(b"fake_audio_2")
        assert tool._audio_out.qsize() == 2

        # Interrupt should drain via playback
        tool._playback.interrupt()
        # Queue should NOT be drained since playback.interrupt
        # only drains its own queue reference — but the internal
        # queue IS the same object, so it should be empty
        assert tool._audio_out.qsize() == 0
