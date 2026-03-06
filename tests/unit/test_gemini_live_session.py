"""Tests for core.ai.session.GeminiLiveSession.

These tests use lightweight fakes/mocks for google.genai types and session.
They validate:
- config building (tools + voice_id)
- tool call dispatch
- send_loop queue consumption
- drain output on interruption

If the google-genai SDK types change, keep assertions focused on the fields
we set rather than exact SDK classes.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

# Provide a lightweight stub to avoid optional desktop dependencies in tests.
if "core.ai.agents.proactive" not in sys.modules:
    proactive_stub = ModuleType("core.ai.agents.proactive")

    class _VisionPulseAgent:  # pragma: no cover - test import shim
        pass

    proactive_stub.VisionPulseAgent = _VisionPulseAgent
    sys.modules["core.ai.agents.proactive"] = proactive_stub

from core.ai.session import GeminiLiveSession
from core.infra.config import AIConfig, GeminiModel


class _FakeToolRouter:
    def __init__(self):
        self.count = 1
        self.names = ["tool_a"]

    def get_declarations(self):
        return [{"name": "tool_a", "description": "x"}]

    async def dispatch(self, fc):
        return {"result": f"ok-{fc.name}"}


class _FakeGateway:
    def __init__(self):
        self.metrics = {}
        self.broadcast = AsyncMock()


@pytest.fixture
def cfg(monkeypatch):
    # AIConfig is a pydantic-settings BaseSettings; instantiate directly
    # with explicit values.
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    return AIConfig(
        api_version="v1alpha",
        model=GeminiModel.LIVE_FLASH,
        system_instruction="hi",
        enable_search_grounding=False,
        enable_affective_dialog=False,
        proactive_audio=False,
        thinking_budget=None,
        enable_proactive_vision=False,
    )


def test_build_session_config_includes_tools_and_voice_id(cfg):
    gateway = _FakeGateway()
    tool_router = _FakeToolRouter()

    soul = SimpleNamespace(
        manifest=SimpleNamespace(voice_id="Aoede", expertise={}),
        persona="persona",
        name="soul",
    )

    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
        tool_router=tool_router,
        soul_manifest=soul,
    )

    c = sess._build_session_config()
    assert c is not None
    # Tools list should exist and include router tool
    assert getattr(c, "tools", None) is not None
    assert len(c.tools) >= 1

    # Voice mapping
    if c.speech_config is not None:
        voice_name = (
            c.speech_config.voice_config.prebuilt_voice_config.voice_name
            if c.speech_config.voice_config
            else None
        )
        assert voice_name == "Aoede"


@pytest.mark.asyncio
async def test_send_loop_reads_from_in_queue_and_sends(cfg):
    gateway = _FakeGateway()
    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
    )
    sess._running = True

    fake_session = SimpleNamespace(send_realtime_input=AsyncMock())

    msg = {"data": b"123", "mime_type": "audio/pcm;rate=16000"}
    await sess._in_queue.put(msg)

    task = asyncio.create_task(sess._send_loop(fake_session))
    await asyncio.sleep(0.05)
    sess._running = False
    await asyncio.sleep(0.01)

    await task

    fake_session.send_realtime_input.assert_awaited()


def test_drain_output_empties_queue(cfg):
    gateway = _FakeGateway()
    out = asyncio.Queue()
    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=out,
        gateway=gateway,
    )

    out.put_nowait(b"a")
    out.put_nowait(b"b")

    sess._drain_output()
    assert out.empty()


def test_handle_usage_records_prompt_and_completion_tokens(cfg, monkeypatch):
    gateway = _FakeGateway()
    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
    )

    captured = {}

    def _fake_record_usage(session_id, prompt_tokens, completion_tokens, model):
        captured["session_id"] = session_id
        captured["prompt_tokens"] = prompt_tokens
        captured["completion_tokens"] = completion_tokens
        captured["model"] = model

    monkeypatch.setattr("core.ai.session.record_usage", _fake_record_usage)

    resp = SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=8)
    )

    sess._handle_usage(resp)

    assert captured["prompt_tokens"] == 12
    assert captured["completion_tokens"] == 8
    assert captured["model"] == cfg.model.value
    assert captured["session_id"]


@pytest.mark.asyncio
async def test_handle_tool_call_broadcasts_and_tracks_handoff(cfg):
    gateway = _FakeGateway()
    tool_router = _FakeToolRouter()
    on_tool_call = AsyncMock()

    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
        tool_router=tool_router,
        on_tool_call=on_tool_call,
    )

    session = SimpleNamespace(send_tool_response=AsyncMock(), send_realtime_input=AsyncMock())
    tool_call = SimpleNamespace(
        function_calls=[
            SimpleNamespace(
                name="delegate_to_agent",
                args={
                    "target_agent_id": "ArchitectExpert",
                    "task_description": "stability audit",
                },
            )
        ]
    )

    async def _dispatch(fc):
        return {
            "status": "handoff_initiated",
            "handoff_id": "h-123",
            "handoff_time": "2026-03-06T00:00:00Z",
            "result": f"handoff-{fc.name}",
        }

    tool_router.dispatch = _dispatch

    await sess._handle_tool_call(session, tool_call)

    session.send_tool_response.assert_awaited_once()
    assert "h-123" in sess._active_handoffs
    tracked = sess._active_handoffs["h-123"]
    assert tracked["target"] == "ArchitectExpert"
    assert tracked["task"] == "stability audit"

    # Let create_task broadcasts finish
    await asyncio.sleep(0)
    gateway.broadcast.assert_any_await("engine_state", {"state": "THINKING"})
    gateway.broadcast.assert_any_await(
        "tool_result",
        {
            "tool_name": "delegate_to_agent",
            "result": "handoff-delegate_to_agent",
            "status": "success",
            "code": None,
        },
    )
    on_tool_call.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_tool_call_injects_screenshot_bytes(cfg, tmp_path: Path):
    gateway = _FakeGateway()
    tool_router = _FakeToolRouter()

    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
        tool_router=tool_router,
    )

    image = tmp_path / "shot.jpg"
    image.write_bytes(b"jpeg-data")

    async def _dispatch(_fc):
        return {
            "result": "captured",
            "screenshot_path": str(image),
        }

    tool_router.dispatch = _dispatch
    session = SimpleNamespace(send_tool_response=AsyncMock(), send_realtime_input=AsyncMock())
    tool_call = SimpleNamespace(function_calls=[SimpleNamespace(name="vision_tool", args={})])

    await sess._handle_tool_call(session, tool_call)

    session.send_realtime_input.assert_awaited_once()
    assert not image.exists()


@pytest.mark.asyncio
async def test_backchannel_loop_sends_empathy_cue_after_thinking_streak(cfg, monkeypatch):
    gateway = _FakeGateway()
    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=asyncio.Queue(),
        gateway=gateway,
    )
    sess._running = True

    fake_audio_state = SimpleNamespace(is_playing=False, silence_type="thinking")
    monkeypatch.setattr("core.audio.state.audio_state", fake_audio_state)

    session = SimpleNamespace(send_realtime_input=AsyncMock())
    task = asyncio.create_task(sess._backchannel_loop(session))

    await asyncio.sleep(5.3)
    sess._running = False
    await task

    session.send_realtime_input.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_loop_drops_oldest_audio_and_handles_interrupt(cfg):
    gateway = _FakeGateway()
    on_interrupt = Mock()
    out = asyncio.Queue(maxsize=1)
    out.put_nowait(b"stale")

    sess = GeminiLiveSession(
        config=cfg,
        audio_in_queue=asyncio.Queue(),
        audio_out_queue=out,
        gateway=gateway,
        on_interrupt=on_interrupt,
    )
    sess._running = True

    part = SimpleNamespace(
        text="hello",
        inline_data=SimpleNamespace(data=b"fresh"),
    )
    response = SimpleNamespace(
        tool_call=None,
        usage_metadata=None,
        server_content=SimpleNamespace(
            model_turn=SimpleNamespace(parts=[part]),
            interrupted=True,
        ),
    )

    async def _turn_once():
        yield response
        sess._running = False

    session = SimpleNamespace(receive=lambda: _turn_once())

    await sess._receive_loop(session)
    await asyncio.sleep(0)

    # Queue had one old chunk; new one was enqueued then interruption drained it.
    assert out.empty()
    assert sess._output_queue_drops == 1
    assert gateway.metrics.get("gemini_output_queue_drops") == 1
    gateway.broadcast.assert_any_await("transcript", {"text": "hello"})
    gateway.broadcast.assert_any_await("engine_state", {"state": "SPEAKING"})
    on_interrupt.assert_called_once()
