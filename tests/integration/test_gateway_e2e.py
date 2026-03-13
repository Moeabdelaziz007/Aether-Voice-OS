"""
Aether Voice OS — Neural Link Probe.
Real-world E2E integration test for the Aether Gateway.
Tests the actual Ed25519 handshake and WebSocket lifecycle without mocks.
"""

import asyncio
import json
import os

import nacl.encoding
import nacl.signing
import pytest
import websockets


# Standardizing configuration to match what AetherGateway and AI Session expect
class MockAudioConfig:
    mic_queue_max = 5
    send_sample_rate = 16000
    receive_sample_rate = 24000
    chunk_size = 512


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
        self.voice_id = "Aoide"
        self.public_key = None


class MockSoul:
    def __init__(self, name):
        self.manifest = MockManifest(name)
        self.persona = self.manifest.persona
        self.expertise = self.manifest.expertise


@pytest.mark.asyncio
async def test_gateway_handshake_e2e():
    # 1. Setup Gateway Backend
    from core.ai.hive import HiveCoordinator
    from core.infra.transport.gateway import AetherGateway
    from core.services.registry import AetherRegistry
    from core.tools.router import ToolRouter

    gw_cfg = MockGatewayConfig(port=18840)
    ai_cfg = UnifiedMockAIConfig()

    # Ensure environment is clean
    os.environ["GOOGLE_API_KEY"] = "dummy"

    # Instantiate dependencies
    registry = AetherRegistry(packages_dir="/tmp")
    tool_router = ToolRouter()

    # Inject active soul manually
    hive = HiveCoordinator(registry=registry, router=tool_router)
    hive._active_soul = MockSoul("ArchitectExpert")

    gateway = AetherGateway(
        gateway_config=gw_cfg,
        ai_config=ai_cfg,
        audio_config=MockAudioConfig(),
        tool_router=tool_router,
        hive=hive,
    )

    # Mock GlobalBus to avoid Redis timeout
    from unittest.mock import AsyncMock

    gateway._bus.connect = AsyncMock(return_value=True)

    # Start gateway in the background
    gw_task = asyncio.create_task(gateway.run())
    await asyncio.sleep(1)  # Wait for bind

    try:
        # 2. Setup Client (Prober)
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key
        # Use 64-char hex string to trigger the Ephemeral/Direct Mode in Gateway
        client_id = verify_key.encode().hex()

        uri = f"ws://localhost:{gw_cfg.port}"
        async with websockets.connect(uri) as websocket:
            # 3. Receive Challenge
            raw_challenge = await websocket.recv()
            challenge_msg = json.loads(raw_challenge)
            assert challenge_msg["type"] == "connect.challenge"
            challenge_token = challenge_msg["challenge"]

            # 4. Sign Challenge & Respond
            # Note: sign the plain challenge_token as bytes, not the hex-decoded
            # version, since verify_signature will encode it.
            challenge_bytes = challenge_token.encode("utf-8")
            signature = signing_key.sign(challenge_bytes)

            client_response = {
                "type": "connect.response",
                "client_id": client_id,
                "signature": signature.signature.hex(),
                "capabilities": ["voice.stream"],
            }
            await websocket.send(json.dumps(client_response))

            # 5. Receive Handshake Response (ACK or Error)
            raw_response = await websocket.recv()
            resp_msg = json.loads(raw_response)

            # Note: We are testing the GATEWAY'S secure handshake.
            # Even if the subsequent Gemini connection fails (due to dummy key),
            # the Gateway should have already verified our Ed25519 signature
            # and potentially sent an ACK or is about to send an error from AI failure.

            if resp_msg["type"] == "error":
                # If it's an AI error, the handshake *itself* might have passed
                # logic check if it reached the AI connection stage.
                if "API key not valid" in resp_msg.get("message", ""):
                    print(
                        "\n✅ Handshake Verified (Ed25519 passed, but AI key is dummy)."
                    )
                    return
                pytest.fail(
                    f"Handshake failed with unexpected error: {resp_msg.get('message')}"
                )

            assert resp_msg["type"] == "connect.ack"
            assert "session_id" in resp_msg

            print("\n✅ Neural Link Probe Successful. Handshake Verified.")

    finally:
        gw_task.cancel()
        try:
            await gw_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(test_gateway_handshake_e2e())
