import asyncio
import json
import logging
import os
import threading
import time
from unittest.mock import MagicMock

import pytest
import requests
import websockets

from core.infra.config import AIConfig, AudioConfig, GatewayConfig
from core.infra.transport.gateway import AetherGateway
from core.services.admin_api import AdminAPIServer
import core.utils.security as sec
import core.infra.transport.auth as auth_mod


logging.basicConfig(level=logging.DEBUG)


class SoulManifestStub:
    def __init__(self, name="AetherArchitect", voice_id="Puck"):
        from dataclasses import dataclass

        @dataclass
        class Manifest:
            name: str
            voice_id: str
            expertise: dict = None

        self.manifest = Manifest(
            name=name, voice_id=voice_id, expertise={"sysadmin": 1.0}
        )
        self.persona = "Stub persona manifest"
        self.name = name


@pytest.fixture
async def aether_services():
    """Start both the Gateway and the Admin API to test their integration."""
    # Start Admin API
    admin_api = AdminAPIServer(port=18790)
    admin_api.start()

    # Configure Gateway
    gateway_config = GatewayConfig()
    gateway_config.port = 18789
    gateway_config.tick_interval_s = 0.5
    gateway_config.max_missed_ticks = 2
    gateway_config.handshake_timeout_s = 1.0

    ai_config = AIConfig(GOOGLE_API_KEY="test", _env_file=None)
    audio_config = AudioConfig()

    tool_router = MagicMock()
    tool_router.count = 0
    tool_router.names = []

    active_soul_obj = SoulManifestStub()
    hive = MagicMock()
    hive.active_soul = active_soul_obj
    hive.get_active_soul.return_value = active_soul_obj
    hive.get_pending_handover_for_target.return_value = None

    # Mock signature verification for E2E speed/ease
    from unittest.mock import patch
    patcher1 = patch('core.utils.security.verify_signature', return_value=True)
    patcher2 = patch('core.infra.transport.auth.AuthService.verify_signature', return_value=True)

    # Mock Gemini connection to avoid real API Calls / 404 errors in tests
    patcher3 = patch('core.ai.session.facade.GeminiLiveSession.connect', return_value=asyncio.sleep(0))
    patcher4 = patch('core.ai.session.facade.GeminiLiveSession.run', return_value=asyncio.sleep(1000)) # Block run loop
    
    mock_sec = patcher1.start()
    mock_auth = patcher2.start()
    mock_connect = patcher3.start()
    mock_run = patcher4.start()

    gw = AetherGateway(gateway_config, ai_config, audio_config, tool_router, hive)
    gw._bus.connect = MagicMock(return_value=asyncio.sleep(0, result=True))

    task = asyncio.create_task(gw.run())
    await asyncio.sleep(0.5)  # Wait for services to start

    yield gw

    admin_api.stop()
    await gw.stop()
    task.cancel()

    patcher1.stop()
    patcher2.stop()
    patcher3.stop()
    patcher4.stop()

    try:
        await task
    except asyncio.CancelledError:
        pass


def test_admin_api_cors_security():
    """Verify Admin API CORS headers strictly follow the whitelist."""
    admin_api = AdminAPIServer(port=18790)
    admin_api.start()
    time.sleep(0.1)

    try:
        url = "http://127.0.0.1:18790/health"

        # 1. Allowed Origin
        headers = {"Origin": "http://localhost:3000"}
        resp = requests.options(url, headers=headers)
        assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"

        # 2. Another Allowed Origin
        headers = {"Origin": "tauri://localhost"}
        resp = requests.options(url, headers=headers)
        assert resp.headers.get("Access-Control-Allow-Origin") == "tauri://localhost"

        # 3. Disallowed Origin
        headers = {"Origin": "http://malicious.com"}
        resp = requests.options(url, headers=headers)
        assert "Access-Control-Allow-Origin" not in resp.headers
    finally:
        admin_api.stop()


@pytest.mark.asyncio
async def test_e2e_frontend_to_gateway_secure_connection(aether_services):
    """
    Simulates the frontend connecting to the gateway, performing the Ed25519
    secure handshake, and maintaining a heartbeat gracefully.
    """
    uri = "ws://127.0.0.1:18789"
    async with websockets.connect(uri) as ws:
        # Step 1: Gateway sends challenge
        challenge_raw = await ws.recv()
        challenge_msg = json.loads(challenge_raw)
        assert "challenge" in challenge_msg

        # Step 2: Client signs challenge (mocked) and sends response
        response = {
            "client_id": "nextjs_frontend",
            "signature": "0" * 128,  # Mocked valid signature
            "capabilities": ["audio_levels", "ui_sync"],
        }
        await ws.send(json.dumps(response))

        # Step 3: Server acknowledges
        ack_raw = await ws.recv()
        ack_msg = json.loads(ack_raw)
        # MessageType.CONNECT_ACK.value is 'connect.ack'
        assert ack_msg["type"] == "connect.ack"
        assert ack_msg["session_id"] is not None

        # Step 4: Ensure heartbeat ticks work without errors
        tick_raw = await ws.recv()
        tick_msg = json.loads(tick_raw)
        # MessageType.TICK.value is 'tick'
        assert tick_msg["type"] == "tick"

        # Disconnect gracefully
        await ws.close()
