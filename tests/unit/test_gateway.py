import asyncio
import json
from unittest.mock import MagicMock

import pytest
import websockets

from core.infra.config import AIConfig, AudioConfig, GatewayConfig
from core.infra.transport.gateway import AetherGateway
from core.infra.transport.messages import MessageType


class SoulManifestStub:
    def __init__(self, name="AetherArchitect", voice_id="Puck"):
        from dataclasses import dataclass

        @dataclass
        class Manifest:
            name: str
            voice_id: str
            expertise: dict = None

        self.manifest = Manifest(name=name, voice_id=voice_id, expertise={"sysadmin": 1.0})
        self.manifest.persona = "Stub persona manifest"
        self.persona = "Stub persona"
        self.name = name


@pytest.fixture
def gateway_config():
    config = GatewayConfig()
    # Use a different port to avoid collisions
    config.port = 18800
    config.tick_interval_s = 0.5
    config.max_missed_ticks = 2
    config.handshake_timeout_s = 1.0
    return config


@pytest.fixture
async def gateway(gateway_config):
    ai_config = AIConfig(GOOGLE_API_KEY="test", _env_file=None)
    audio_config = AudioConfig()

    # Tool Router with concrete count
    tool_router = MagicMock()
    tool_router.count = 0
    tool_router.names = []

    # Soul with concrete attributes instead of MagicMocks
    active_soul_obj = SoulManifestStub()

    hive = MagicMock()
    hive.active_soul = active_soul_obj
    hive.get_active_soul.return_value = active_soul_obj
    hive.get_pending_handover_for_target.return_value = None

    # Also fix Signature verification so it passes with dummy 0*128 signature
    # Since AuthService relies on verify_signature, we mock it via patch
    from unittest.mock import patch

    patcher1 = patch("core.utils.security.verify_signature", return_value=True)
    patcher2 = patch("core.infra.transport.auth.AuthService.verify_signature", return_value=True)

    patcher1.start()
    patcher2.start()

    gw = AetherGateway(gateway_config, ai_config, audio_config, tool_router, hive)

    # Mock the GlobalBus so it doesn't try to connect to a missing Redis server
    # and time out for 5 seconds, which would fail the server start.
    gw._bus.connect = MagicMock(return_value=asyncio.sleep(0, result=True))

    task = asyncio.create_task(gw.run())
    # Give the server a moment to start
    await asyncio.sleep(0.1)
    yield gw
    await gw.stop()
    task.cancel()

    patcher1.stop()
    patcher2.stop()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_handshake_success(gateway, gateway_config):
    uri = f"ws://{gateway_config.host}:{gateway_config.port}"
    async with websockets.connect(uri) as ws:
        # Expect challenge
        challenge_raw = await ws.recv()
        challenge_msg = json.loads(challenge_raw)
        assert "challenge" in challenge_msg

        # Send response
        response = {
            "client_id": "test_client_123",
            "signature": "0" * 128,
            "capabilities": ["audio_levels"],
        }
        await ws.send(json.dumps(response))

        # Expect ACK
        ack_raw = await ws.recv()
        ack_msg = json.loads(ack_raw)
        assert ack_msg["type"] == MessageType.CONNECT_ACK.value
        assert "session_id" in ack_msg
        assert ack_msg["granted_capabilities"] == ["audio_levels"]

        assert "test_client_123" in gateway._clients


@pytest.mark.asyncio
async def test_handshake_timeout(gateway, gateway_config):
    uri = f"ws://{gateway_config.host}:{gateway_config.port}"
    async with websockets.connect(uri) as ws:
        # Expect challenge
        await ws.recv()
        # Do not send response, wait for server to disconnect us

        # Server sends error message first
        error_raw = await ws.recv()
        error_msg = json.loads(error_raw)
        assert error_msg["type"] == MessageType.ERROR.value
        assert error_msg["code"] == 401

        with pytest.raises(websockets.exceptions.ConnectionClosed):
            await ws.recv()


@pytest.mark.asyncio
async def test_heartbeat_tick_and_pong(gateway, gateway_config):
    uri = f"ws://{gateway_config.host}:{gateway_config.port}"
    async with websockets.connect(uri) as ws:
        await ws.recv()  # Challenge
        await ws.send(json.dumps({"client_id": "test_ticker", "signature": "0" * 128}))
        await ws.recv()  # ACK

        # Wait for TICK
        tick_raw = await ws.recv()
        tick_msg = json.loads(tick_raw)
        assert tick_msg["type"] == MessageType.TICK.value

        # Send PONG
        await ws.send(json.dumps({"type": MessageType.PONG.value}))

        # Assert no disconnection after another tick interval
        await asyncio.sleep(gateway_config.tick_interval_s * 1.5)
        assert "test_ticker" in gateway._clients


@pytest.mark.asyncio
async def test_pruning_dead_clients(gateway, gateway_config):
    uri = f"ws://{gateway_config.host}:{gateway_config.port}"
    async with websockets.connect(uri) as ws:
        await ws.recv()  # Challenge
        await ws.send(json.dumps({"client_id": "dead_client", "signature": "0" * 128}))
        await ws.recv()  # ACK

        assert "dead_client" in gateway._clients

        # Wait for max_missed_ticks to elapse without sending PONG
        wait_time = gateway_config.tick_interval_s * (gateway_config.max_missed_ticks + 1.5)
        await asyncio.sleep(wait_time)

        # Client should be pruned
        assert "dead_client" not in gateway._clients


@pytest.mark.asyncio
async def test_broadcast(gateway, gateway_config):
    uri = f"ws://{gateway_config.host}:{gateway_config.port}"
    async with websockets.connect(uri) as ws1, websockets.connect(uri) as ws2:
        # Authenticate client 1
        await ws1.recv()
        await ws1.send(json.dumps({"client_id": "c1", "signature": "0" * 128}))
        await ws1.recv()

        # Authenticate client 2
        await ws2.recv()
        await ws2.send(json.dumps({"client_id": "c2", "signature": "0" * 128}))
        await ws2.recv()

        # Broadcast message
        payload = {"level": 0.8}
        await gateway.broadcast("audio_level", payload)

        # Receive on ws1
        msg1raw = await ws1.recv()
        msg1 = json.loads(msg1raw)
        assert msg1["type"] == "audio_level"
        assert msg1["payload"]["level"] == 0.8

        # Receive on ws2
        msg2raw = await ws2.recv()
        msg2 = json.loads(msg2raw)
        assert msg2["type"] == "audio_level"
        assert msg2["payload"]["level"] == 0.8
