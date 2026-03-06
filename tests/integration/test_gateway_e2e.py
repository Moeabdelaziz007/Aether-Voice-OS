"""Gateway E2E integration and protocol contract tests."""

import asyncio
import base64
import json
import os
from unittest.mock import AsyncMock

import nacl.signing
import pytest
import websockets


class MockAudioConfig:
    mic_queue_max = 5


class MockModel:
    def __init__(self, value):
        self.value = value


class UnifiedMockAIConfig:
    def __init__(self):
        self.audio = MockAudioConfig()
        self.api_key = "dummy"
        self.api_version = "v1beta"
        self.model = MockModel("gemini-live-2.5-flash-preview")
        self.system_instruction = "Test Instruction"
        self.enable_affective_dialog = True
        self.enable_search_grounding = True
        self.thinking_budget = 0
        self.proactive_audio = False
        self.debug = False


class MockGatewayConfig:
    def __init__(self, port):
        self.port = port
        self.host = "0.0.0.0"
        self.tick_interval_s = 15.0
        self.max_missed_ticks = 2
        self.handshake_timeout_s = 10.0
        self.receive_sample_rate = 16000


class MockManifest:
    def __init__(self, name):
        self.name = name
        self.persona = "You are the Aether Architect Expert."
        self.expertise = ["Cloud Architecture", "AI Systems"]


class MockSoul:
    def __init__(self, name):
        self.manifest = MockManifest(name)
        self.persona = self.manifest.persona
        self.expertise = self.manifest.expertise


class FakeHive:
    def __init__(self, soul):
        self._active_soul = soul
        self._last_handover_id = None

    def set_pre_warm_callback(self, _cb):
        return None

    @property
    def active_soul(self):
        return self._active_soul

    def get_pending_handover_for_target(self, _name):
        return None

    def cleanup_handovers(self):
        return None

    def prepare_handoff(self, *args, **kwargs):
        return False, None, "not used"

    def complete_handoff(self, *_args, **_kwargs):
        return False

    def rollback_handover(self, *_args, **_kwargs):
        return False


def _hook_compatible_event(raw: dict) -> tuple[str, dict]:
    """Mirror portal fallback parsing: payload envelope OR flat legacy shape."""
    payload = raw.get("payload") if isinstance(raw.get("payload"), dict) else raw
    return raw.get("type", ""), payload


@pytest.mark.asyncio
async def test_gateway_handshake_and_contract_events_e2e():
    from core.infra.transport.gateway import AetherGateway
    from core.tools.router import ToolRouter

    gw_cfg = MockGatewayConfig(port=18840)
    ai_cfg = UnifiedMockAIConfig()

    os.environ["GOOGLE_API_KEY"] = "dummy"

    tool_router = ToolRouter()
    hive = FakeHive(MockSoul("ArchitectExpert"))

    gateway = AetherGateway(
        gateway_config=gw_cfg,
        ai_config=ai_cfg,
        audio_config=MockAudioConfig(),
        tool_router=tool_router,
        hive=hive,
    )
    gateway._bus.connect = AsyncMock(return_value=True)

    gw_task = asyncio.create_task(gateway.run())
    await asyncio.sleep(1)

    signing_key = nacl.signing.SigningKey.generate()
    client_id = signing_key.verify_key.encode().hex()

    try:
        uri = f"ws://localhost:{gw_cfg.port}"
        async with websockets.connect(uri) as websocket:
            challenge_msg = json.loads(await websocket.recv())
            assert challenge_msg["type"] == "connect.challenge"
            assert challenge_msg["version"] == "2.1"

            challenge_bytes = bytes.fromhex(challenge_msg["challenge"])
            signature = signing_key.sign(challenge_bytes)
            await websocket.send(
                json.dumps(
                    {
                        "type": "connect.response",
                        "version": "2.1",
                        "client_id": client_id,
                        "signature": signature.signature.hex(),
                        "capabilities": ["audio.input"],
                    }
                )
            )

            response = json.loads(await websocket.recv())
            assert response["type"] == "connect.ack"
            assert response["version"] == "2.1"

            # Validate canonical event envelopes emitted by backend
            await gateway.broadcast("engine_state", {"state": "LISTENING"})
            event = json.loads(await websocket.recv())
            event_type, payload = _hook_compatible_event(event)
            assert event_type == "engine_state"
            assert payload["state"] == "LISTENING"
            assert event["version"] == "2.1"

            await gateway.broadcast("transcript", {"role": "ai", "text": "hello"})
            event = json.loads(await websocket.recv())
            event_type, payload = _hook_compatible_event(event)
            assert event_type == "transcript"
            assert payload["role"] == "ai"
            assert payload["text"] == "hello"

            await gateway.broadcast("tool_result", {"tool_name": "demo", "result": "ok"})
            event = json.loads(await websocket.recv())
            event_type, payload = _hook_compatible_event(event)
            assert event_type == "tool_result"
            assert payload["tool_name"] == "demo"

            await gateway.broadcast("interrupt", {"reason": "barge-in"})
            event = json.loads(await websocket.recv())
            event_type, payload = _hook_compatible_event(event)
            assert event_type == "interrupt"
            assert payload["reason"] == "barge-in"

    finally:
        gw_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await gw_task


@pytest.mark.asyncio
async def test_gateway_accepts_canonical_and_legacy_audio_messages():
    from core.infra.transport.gateway import AetherGateway
    from core.tools.router import ToolRouter

    gw_cfg = MockGatewayConfig(port=18841)
    ai_cfg = UnifiedMockAIConfig()
    os.environ["GOOGLE_API_KEY"] = "dummy"

    tool_router = ToolRouter()
    hive = FakeHive(MockSoul("ArchitectExpert"))

    gateway = AetherGateway(
        gateway_config=gw_cfg,
        ai_config=ai_cfg,
        audio_config=MockAudioConfig(),
        tool_router=tool_router,
        hive=hive,
    )
    gateway._bus.connect = AsyncMock(return_value=True)

    gw_task = asyncio.create_task(gateway.run())
    await asyncio.sleep(1)

    signing_key = nacl.signing.SigningKey.generate()
    client_id = signing_key.verify_key.encode().hex()

    try:
        uri = f"ws://localhost:{gw_cfg.port}"
        async with websockets.connect(uri) as websocket:
            challenge_msg = json.loads(await websocket.recv())
            challenge_bytes = bytes.fromhex(challenge_msg["challenge"])
            signature = signing_key.sign(challenge_bytes)
            await websocket.send(
                json.dumps(
                    {
                        "type": "connect.response",
                        "client_id": client_id,
                        "signature": signature.signature.hex(),
                        "capabilities": ["audio.input"],
                    }
                )
            )
            _ = json.loads(await websocket.recv())

            sample = b"\x00\x01\x02\x03"
            await websocket.send(
                json.dumps(
                    {
                        "type": "audio.chunk",
                        "version": "2.1",
                        "payload": {
                            "mime_type": "audio/pcm;rate=16000",
                            "data": base64.b64encode(sample).decode(),
                        },
                    }
                )
            )

            legacy = {
                "realtimeInput": {
                    "mediaChunks": [
                        {
                            "mimeType": "audio/pcm;rate=16000",
                            "data": base64.b64encode(sample).decode(),
                        }
                    ]
                }
            }
            await websocket.send(json.dumps(legacy))

            first = await asyncio.wait_for(gateway.audio_in_queue.get(), timeout=2)
            second = await asyncio.wait_for(gateway.audio_in_queue.get(), timeout=2)

            assert first["data"] == sample
            assert second["data"] == sample

    finally:
        gw_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await gw_task
