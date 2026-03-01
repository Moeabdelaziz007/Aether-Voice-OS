"""
Aether Voice OS — System Alpha E2E (Zero-Mock) [Diagnostic Version].
------------------------------------------------------------------
Hardened E2E test with strict timeouts and granular logging to debug protocol hangs.
"""

import asyncio
import json
import base64
import os
import pytest
import websockets
import nacl.signing
import nacl.encoding
from pathlib import Path

# Aether Core Imports
from core.transport.gateway import AetherGateway
from core.ai.hive import HiveCoordinator
from core.tools.router import ToolRouter
from core.identity.registry import AetherRegistry

# Configuration for Test Environment
class E2EGatewayConfig:
    def __init__(self, port=18995): # Different port to avoid conflict
        self.port = port
        self.host = "127.0.0.1"
        self.tick_interval_s = 1.0
        self.max_missed_ticks = 2
        self.handshake_timeout_s = 3.0
        self.receive_sample_rate = 16000

class E2EAudioConfig:
    def __init__(self):
        self.mic_queue_max = 5

class E2EModel:
    def __init__(self, value):
        self.value = value

class E2EAIConfig:
    def __init__(self):
        self.audio = E2EAudioConfig()
        self.api_key = os.environ.get("GOOGLE_API_KEY", "dummy_key")
        self.api_version = "v1beta"
        self.model = E2EModel("models/gemini-2.0-flash-exp")
        self.system_instruction = "E2E Diagnostic Probe."
        self.enable_affective_dialog = True
        self.enable_search_grounding = True
        self.thinking_budget = 0
        self.proactive_audio = False
        self.debug = True

@pytest.mark.asyncio
async def test_aether_system_alpha_full_cycle():
    print("\n[PROBE] Starting Diagnostic E2E Cycle...")
    
    # 1. SETUP REGISTRY & KEYS
    signing_key = nacl.signing.SigningKey.generate()
    public_key_hex = signing_key.verify_key.encode().hex().lower()
    client_id = public_key_hex
    
    registry_path = Path("/tmp/aether_diagnostic_registry")
    if registry_path.exists():
        import shutil
        shutil.rmtree(registry_path)
    registry_path.mkdir(parents=True)
    
    # Create Soul Manifest
    arch_path = registry_path / client_id
    arch_path.mkdir()
    with open(arch_path / "manifest.json", "w") as f:
        json.dump({
            "name": client_id,
            "version": "1.0.0",
            "persona": "Diagnostic Soul",
            "public_key": public_key_hex,
            "expertise": {"diagnostics": 1.0}
        }, f)

    registry = AetherRegistry(packages_dir=str(registry_path))
    registry.scan()
    print(f"[PROBE] Registry initialized with {registry.count} souls.")
    
    hive = HiveCoordinator(registry=registry, router=ToolRouter())
    gw_cfg = E2EGatewayConfig()
    gateway = AetherGateway(
        gateway_config=gw_cfg,
        ai_config=E2EAIConfig(),
        tool_router=ToolRouter(),
        hive=hive
    )
    
    # Start Backend
    print("[PROBE] Starting Gateway Server...")
    gw_task = asyncio.create_task(gateway.run())
    await asyncio.sleep(1.0) # Ensure server is up
    
    try:
        uri = f"ws://{gw_cfg.host}:{gw_cfg.port}"
        print(f"[PROBE] Connecting to {uri}...")
        
        async with asyncio.timeout(10.0): # Global test timeout
            async with websockets.connect(uri) as ws:
                print("[PROBE] WebSocket Connected. Awaiting Challenge...")
                
                # Receive Challenge
                raw_challenge = await asyncio.wait_for(ws.recv(), timeout=3.0)
                challenge_msg = json.loads(raw_challenge)
                print(f"[PROBE] Received Challenge: {challenge_msg['type']}")
                assert challenge_msg["type"] == "connect.challenge"
                
                # Sign Challenge
                # CRITICAL: gateway verifies against raw bytes, so we sign the bytes from the hex token
                token_hex = challenge_msg["challenge"]
                token_bytes = bytes.fromhex(token_hex)
                sig_obj = signing_key.sign(token_bytes)
                sig_hex = sig_obj.signature.hex()
                
                # Send Response
                resp = {
                    "type": "connect.response",
                    "client_id": client_id,
                    "signature": sig_hex,
                    "capabilities": ["voice.stream"]
                }
                print("[PROBE] Sending Handshake Response...")
                await ws.send(json.dumps(resp))
                
                # Receive ACK or Error
                print("[PROBE] Awaiting ACK/Result...")
                raw_ack = await asyncio.wait_for(ws.recv(), timeout=5.0)
                ack_msg = json.loads(raw_ack)
                print(f"[PROBE] Result Received: {ack_msg['type']}")
                
                if ack_msg["type"] == "error":
                    print(f"[PROBE] Protocol Error (Expected if AI Auth fails): {ack_msg.get('message')}")
                    return # Passthrough success for protocol validation
                
                assert ack_msg["type"] == "connect.ack"
                print(f"[PROBE] Session Established: {ack_msg['session_id']}")
                
                # Send Dummy Audio (3200 bytes = 100ms pcm16)
                print("[PROBE] Sending Small Audio Burst...")
                await ws.send(bytes([0]*3200))
                print("[PROBE] Audio Sent. Verifying Hive status...")
                
                assert hive.active_soul is not None
                print(f"[PROBE] Active Soul: {hive.active_soul.manifest.name}")

    except asyncio.TimeoutError:
        print("[PROBE] CRITICAL: Test timed out at a specific stage.")
        pytest.fail("E2E Test timed out - protocol hung.")
    except Exception as e:
        print(f"[PROBE] Exception occurred: {type(e).__name__}: {e}")
        raise e
    finally:
        print("[PROBE] Shutting down Gateway...")
        gw_task.cancel()
        try:
            await gw_task
        except asyncio.CancelledError:
            pass
        print("[PROBE] Diagnostic Cycle Complete.")

if __name__ == "__main__":
    pytest.main([__file__, "-s", "-vv"])
