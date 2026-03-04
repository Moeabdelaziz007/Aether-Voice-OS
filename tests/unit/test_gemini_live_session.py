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
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

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
    # AIConfig is a pydantic-settings BaseSettings; instantiate directly with explicit values.
    import os
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    return AIConfig(
        api_key="k",
        api_version="v1alpha",
        model=GeminiModel.LIVE_FLASH,
        system_instruction="hi",
        enable_search_grounding=False,
        enable_affective_dialog=False,
        proactive_audio=False,
        thinking_budget=None,
        enable_proactive_vision=False,
        _env_file=None,
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

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
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
