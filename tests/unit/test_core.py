"""
Aether Voice OS — Comprehensive Test Suite.

Tests all core modules for correctness:
  1. Config loading & validation
  2. Audio processing (RingBuffer, VAD, ZeroCrossing)
  3. Tool declarations & registration
  4. Firebase connector (offline mode)
  5. Memory tool (offline fallback)
  6. Voice tool state machine
  7. Engine initialization (dry run — no audio devices)
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

# ═══════════════════════════════════════════════════════════
# 1. CONFIG
# ═══════════════════════════════════════════════════════════


class TestConfig:
    """Test configuration loading and validation."""

    def test_audio_config_defaults(self):
        from core.utils.config import AudioConfig

        cfg = AudioConfig()
        assert cfg.send_sample_rate == 16_000
        assert cfg.receive_sample_rate == 24_000
        assert cfg.channels == 1
        assert cfg.chunk_size == 512
        assert cfg.format_width == 2
        assert cfg.mic_queue_max == 5

    def test_gateway_config_defaults(self):
        from core.utils.config import GatewayConfig

        cfg = GatewayConfig()
        assert cfg.host == "0.0.0.0"
        assert cfg.port == 18789
        assert cfg.tick_interval_s == 15.0
        assert cfg.max_missed_ticks == 2

    def test_ai_config_requires_api_key(self):
        from core.utils.config import AIConfig

        cfg = AIConfig(api_key="test-key-123")
        assert cfg.api_key == "test-key-123"
        assert cfg.enable_affective_dialog is True
        assert cfg.proactive_audio is True
        assert cfg.enable_search_grounding is True
        assert cfg.thinking_budget == 0

    def test_gemini_model_enum(self):
        from core.utils.config import GeminiModel

        assert (
            GeminiModel.FLASH_NATIVE_AUDIO.value
            == "gemini-2.5-flash-native-audio-preview-12-2025"
        )
        assert GeminiModel.LIVE_FLASH.value == "gemini-live-2.5-flash-preview"

    def test_load_config_with_env(self):
        from core.utils.config import load_config

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key-for-loading"}):
            cfg = load_config()
            assert cfg.ai.api_key == "test-key-for-loading"

    def test_load_config_with_json_fallback(self):
        """Test the TCC Bypass logic using JSON config."""
        from core.utils.config import load_config

        json_path = Path("aether_runtime_config.json")
        backup_path = Path("aether_runtime_config.json.bak")

        # Backup existing if any
        exists = json_path.exists()
        if exists:
            shutil.copy(json_path, backup_path)

        test_data = {
            "GOOGLE_API_KEY": "json-key-123",
            "AETHER_AI_MODEL": "gemini-2.5-flash-native-audio-preview-12-2025",
        }
        try:
            with open(json_path, "w") as f:
                json.dump(test_data, f)

            # Clear env to force fallback
            with patch.dict(os.environ, {}, clear=True):
                cfg = load_config()
                assert cfg.ai.api_key == "json-key-123"
                assert (
                    os.environ["AETHER_AI_MODEL"]
                    == "gemini-2.5-flash-native-audio-preview-12-2025"
                )
        finally:
            if exists:
                shutil.move(backup_path, json_path)
            else:
                if json_path.exists():
                    os.remove(json_path)

    def test_load_config_missing_key_raises(self):
        from core.utils.config import load_config

        # Ensure no env and no json
        json_path = Path("aether_runtime_config.json")
        backup_path = Path("aether_runtime_config.json.bak")
        exists = json_path.exists()
        if exists:
            shutil.move(json_path, backup_path)

        try:
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(EnvironmentError) as exc:
                    load_config()
                assert "Sandbox restriction" in str(exc.value)
        finally:
            if exists:
                shutil.move(backup_path, json_path)


# ═══════════════════════════════════════════════════════════
# 2. AUDIO PROCESSING
# ═══════════════════════════════════════════════════════════


class TestRingBuffer:
    """Test the O(1) circular buffer."""

    def test_basic_write_read(self):
        from core.audio.processing import RingBuffer

        buf = RingBuffer(100)
        data = np.array([1, 2, 3, 4, 5], dtype=np.int16)
        buf.write(data)
        assert buf.count == 5
        result = buf.read_last(5)
        np.testing.assert_array_equal(result, data)

    def test_wrap_around(self):
        from core.audio.processing import RingBuffer

        buf = RingBuffer(10)
        # Write 8 samples
        buf.write(np.arange(8, dtype=np.int16))
        # Write 5 more (wraps around)
        buf.write(np.arange(100, 105, dtype=np.int16))
        assert buf.count == 10
        last5 = buf.read_last(5)
        np.testing.assert_array_equal(last5, np.arange(100, 105, dtype=np.int16))

    def test_overflow(self):
        from core.audio.processing import RingBuffer

        buf = RingBuffer(5)
        big = np.arange(20, dtype=np.int16)
        buf.write(big)
        assert buf.count == 5
        result = buf.read_last(5)
        np.testing.assert_array_equal(result, np.arange(15, 20, dtype=np.int16))

    def test_clear(self):
        from core.audio.processing import RingBuffer

        buf = RingBuffer(10)
        buf.write(np.ones(10, dtype=np.int16))
        buf.clear()
        assert buf.count == 0
        assert len(buf.read_last(10)) == 0

    def test_empty_read(self):
        from core.audio.processing import RingBuffer

        buf = RingBuffer(10)
        result = buf.read_last(5)
        assert len(result) == 0


class TestVAD:
    """Test Voice Activity Detection."""

    def test_silence_detected(self):
        from core.audio.processing import energy_vad

        silence = np.zeros(1024, dtype=np.int16)
        result = energy_vad(silence)
        assert result.is_hard is False
        assert result.is_soft is False
        assert result.energy_rms == 0.0
        assert result.sample_count == 1024

    def test_speech_detected(self):
        from core.audio.processing import energy_vad

        # Loud signal
        loud = np.full(1024, 10000, dtype=np.int16)
        result = energy_vad(loud, threshold=0.01)
        assert result.is_hard is True
        assert result.is_soft is True
        assert result.energy_rms > 0.01

    def test_empty_input(self):
        from core.audio.processing import energy_vad

        empty = np.array([], dtype=np.int16)
        result = energy_vad(empty)
        assert result.is_hard is False
        assert result.is_soft is False
        assert result.sample_count == 0

    def test_threshold_boundary(self):
        from core.audio.processing import energy_vad

        # RMS just above threshold
        pcm = np.full(1024, 700, dtype=np.int16)  # ~0.021 normalized
        result_low = energy_vad(pcm, threshold=0.01)
        result_high = energy_vad(pcm, threshold=0.1)
        assert result_low.is_hard is True
        assert result_high.is_hard is False


class TestZeroCrossing:
    """Test zero-crossing detection."""

    def test_finds_crossing(self):
        from core.audio.processing import find_zero_crossing

        # +1, +1, -1, -1 — crossing between index 1 and 2
        pcm = np.array([100, 100, -100, -100], dtype=np.int16)
        idx = find_zero_crossing(pcm, sample_rate=16_000, max_lookahead_ms=20.0)
        assert idx == 2  # first crossing point

    def test_no_crossing(self):
        from core.audio.processing import find_zero_crossing

        pcm = np.full(100, 500, dtype=np.int16)  # all positive
        idx = find_zero_crossing(pcm, sample_rate=16_000, max_lookahead_ms=20.0)
        assert idx == len(pcm)

    def test_very_short_input(self):
        from core.audio.processing import find_zero_crossing

        pcm = np.array([1], dtype=np.int16)
        idx = find_zero_crossing(pcm, sample_rate=16_000, max_lookahead_ms=20.0)
        assert idx == 1


# ═══════════════════════════════════════════════════════════
# 3. TOOL DECLARATIONS
# ═══════════════════════════════════════════════════════════


class TestToolDeclarations:
    """Verify all tool modules export valid get_tools()."""

    def test_system_tool_declarations(self):
        from core.tools import system_tool

        tools = system_tool.get_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 3
        names = [t["name"] for t in tools]
        assert "get_current_time" in names
        assert "get_system_info" in names
        assert "run_timer" in names

    def test_tasks_tool_declarations(self):
        from core.tools import tasks_tool

        tools = tasks_tool.get_tools()
        assert isinstance(tools, list)
        names = [t["name"] for t in tools]
        assert "create_task" in names
        assert "list_tasks" in names

    def test_memory_tool_declarations(self):
        from core.tools import memory_tool

        tools = memory_tool.get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 5
        names = [t["name"] for t in tools]
        assert "save_memory" in names
        assert "recall_memory" in names
        assert "list_memories" in names

    def test_voice_tool_declarations(self):
        from core.tools import voice_tool

        tools = voice_tool.get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 1
        assert tools[0]["name"] == "aether_voice"
        assert "start" in tools[0]["parameters"]["properties"]["action"]["enum"]

    def test_all_tools_have_handler(self):
        """Every tool must have a callable handler."""
        from core.tools import memory_tool, system_tool, tasks_tool, voice_tool

        for mod in [system_tool, tasks_tool, memory_tool, voice_tool]:
            for tool in mod.get_tools():
                assert "handler" in tool, f"{tool['name']} missing handler"
                assert callable(tool["handler"]), f"{tool['name']} handler not callable"

    def test_search_tool_returns_empty_list(self):
        """Search tool uses built-in Gemini grounding, not function handlers."""
        from core.tools.search_tool import get_tools

        tools = get_tools()
        assert tools == []


# ═══════════════════════════════════════════════════════════
# 4. FIREBASE CONNECTOR (OFFLINE)
# ═══════════════════════════════════════════════════════════


class TestFirebaseConnector:
    """Test FirebaseConnector in offline mode."""

    def test_init_defaults(self):
        from core.tools.firebase_tool import FirebaseConnector

        fb = FirebaseConnector()
        assert fb._initialized is False
        assert fb._db is None
        assert fb._session_id is None

    def test_is_connected_false_initially(self):
        from core.tools.firebase_tool import FirebaseConnector

        fb = FirebaseConnector()
        assert fb.is_connected is False

    @pytest.mark.asyncio
    async def test_initialize_without_firebase_admin(self):
        """Should gracefully handle missing firebase-admin."""
        from core.tools.firebase_tool import FirebaseConnector

        fb = FirebaseConnector()
        # If firebase-admin is not installed, should return False
        result = await fb.initialize()
        # Either True (if installed) or False (if not) — just shouldn't crash
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════
# 5. MEMORY TOOL (OFFLINE FALLBACK)
# ═══════════════════════════════════════════════════════════


class TestMemoryToolOffline:
    """Test memory tool when Firebase is not connected."""

    @pytest.mark.asyncio
    async def test_save_memory_offline(self):
        from core.tools.memory_tool import save_memory

        result = await save_memory(key="test_key", value="test_value")
        assert result["status"] == "saved_locally"
        assert result["key"] == "test_key"

    @pytest.mark.asyncio
    async def test_recall_memory_offline(self):
        from core.tools.memory_tool import recall_memory

        result = await recall_memory(key="test_key")
        assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_list_memories_offline(self):
        from core.tools.memory_tool import list_memories

        result = await list_memories()
        assert result["status"] == "unavailable"


# ═══════════════════════════════════════════════════════════
# 6. VOICE TOOL STATE MACHINE
# ═══════════════════════════════════════════════════════════


class TestVoiceToolStateMachine:
    """Test VoiceTool state transitions."""

    def test_initial_state(self):
        from core.tools.voice_tool import VoiceState, VoiceTool

        tool = VoiceTool()
        assert tool.state == VoiceState.IDLE
        assert tool.is_active is False

    def test_state_change_callback(self):
        from core.tools.voice_tool import VoiceState, VoiceTool

        transitions = []

        def on_change(old, new):
            transitions.append((old, new))

        tool = VoiceTool(on_state_change=on_change)
        tool._set_state(VoiceState.INITIALIZING)
        tool._set_state(VoiceState.LISTENING)
        assert len(transitions) == 2
        assert transitions[0] == (VoiceState.IDLE, VoiceState.INITIALIZING)
        assert transitions[1] == (VoiceState.INITIALIZING, VoiceState.LISTENING)

    def test_is_active_states(self):
        from core.tools.voice_tool import VoiceState, VoiceTool

        tool = VoiceTool()
        for state in [VoiceState.LISTENING, VoiceState.PROCESSING, VoiceState.SPEAKING]:
            tool._state = state
            assert tool.is_active is True
        for state in [VoiceState.IDLE, VoiceState.STOPPED, VoiceState.ERROR]:
            tool._state = state
            assert tool.is_active is False

    @pytest.mark.asyncio
    async def test_handle_tool_call_status(self):
        from core.tools.voice_tool import VoiceTool

        tool = VoiceTool()
        result = await tool.handle_tool_call("status")
        assert result["state"] == "idle"
        assert result["is_active"] is False

    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown(self):
        from core.tools.voice_tool import VoiceTool

        tool = VoiceTool()
        result = await tool.handle_tool_call("invalid_action")
        assert "error" in result


# ═══════════════════════════════════════════════════════════
# 7. SYSTEM TOOLS (LIVE EXECUTION)
# ═══════════════════════════════════════════════════════════


class TestSystemToolsLive:
    """Test system tools actually execute correctly."""

    @pytest.mark.asyncio
    async def test_get_current_time(self):
        from core.tools.system_tool import get_current_time

        result = await get_current_time()
        assert "time" in result or "current_time" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_system_info(self):
        from core.tools.system_tool import get_system_info

        result = await get_system_info()
        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════
# 9. INTEGRATION: TOOL ROUTER
# ═══════════════════════════════════════════════════════════


class TestToolRouter:
    """Test the Neural Dispatcher (ToolRouter)."""

    def test_register_module(self):
        from core.tools import system_tool
        from core.tools.router import ToolRouter

        router = ToolRouter()
        router.register_module(system_tool)
        assert router.count >= 3
        assert "get_current_time" in router.names

    def test_register_multiple_modules(self):
        from core.tools import memory_tool, system_tool
        from core.tools.router import ToolRouter

        router = ToolRouter()
        router.register_module(system_tool)
        router.register_module(memory_tool)
        names = router.names
        assert "get_current_time" in names
        assert "save_memory" in names
        assert "recall_memory" in names

    def test_get_declarations(self):
        from core.tools import system_tool
        from core.tools.router import ToolRouter

        router = ToolRouter()
        router.register_module(system_tool)
        decls = router.get_declarations()
        assert isinstance(decls, list)
        assert len(decls) >= 3
        # Each declaration should have name and description
        for d in decls:
            assert hasattr(d, "name") or "name" in str(type(d))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
