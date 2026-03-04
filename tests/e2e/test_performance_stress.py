"""
Aether Voice OS — Performance Stress Test.
-----------------------------------------
Benchmarks latency for handshake, audio ingestion, and telemetry overhead.
"""

import asyncio
import json
import time
import pytest
import websockets
import nacl.signing
from pathlib import Path

# Aether Core Imports
from core.infra.transport.gateway import AetherGateway
from core.ai.hive import HiveCoordinator
from core.tools.router import ToolRouter
from core.services.registry import AetherRegistry

class PerfGatewayConfig:
    def __init__(self, port=18996):
        self.port = port
        self.host = "127.0.0.1"
        self.tick_interval_s = 0.5
        self.max_missed_ticks = 2
        self.handshake_timeout_s = 2.0
        self.receive_sample_rate = 16000

class PerfAIConfig:
    def __init__(self):
        from tests.e2e.test_system_alpha_e2e import E2EModel, E2EAudioConfig
        self.audio = E2EAudioConfig()
        self.api_key = "dummy"
        self.api_version = "v1beta"
        self.model = E2EModel("models/gemini-2.0-flash-exp")
        self.system_instruction = "Performance Probe."
        self.enable_affective_dialog = False
        self.enable_search_grounding = False
        self.thinking_budget = 0
        self.proactive_audio = False
        self.debug = False

@pytest.mark.asyncio
async def test_handshake_latency():
    print("\n[PERF] Benchmarking Handshake Latency...")
    
    # Setup
    signing_key = nacl.signing.SigningKey.generate()
    client_id = signing_key.verify_key.encode().hex().lower()
    
    reg_path = Path("/tmp/aether_perf_registry")
    if reg_path.exists():
        import shutil
        shutil.rmtree(reg_path)
    reg_path.mkdir(parents=True)
    (reg_path / client_id).mkdir()
    with open(reg_path / client_id / "manifest.json", "w") as f:
        json.dump({
            "name": client_id,
            "version": "1.0.0",
            "persona": "Perf Probe",
            "public_key": client_id
        }, f)
        
    registry = AetherRegistry(packages_dir=str(reg_path))
    registry.scan()
    from tests.e2e.test_system_alpha_e2e import E2EAudioConfig
    gateway = AetherGateway(
        gateway_config=PerfGatewayConfig(),
        audio_config=E2EAudioConfig(),
        ai_config=PerfAIConfig(),
        tool_router=ToolRouter(),
        hive=HiveCoordinator(registry=registry, router=ToolRouter())
    )
    
    # Mock GlobalBus to avoid Redis timeout
    from unittest.mock import AsyncMock
    gateway._bus.connect = AsyncMock(return_value=True)
    
    gw_task = asyncio.create_task(gateway.run())
    await asyncio.sleep(0.5)
    
    latencies = []
    
    for i in range(5):
        start_time = time.perf_counter()
        async with websockets.connect(f"ws://127.0.0.1:18996") as ws:
            # 1. Challenge
            msg = json.loads(await ws.recv())
            # 2. Response
            token_bytes = bytes.fromhex(msg["challenge"])
            sig = signing_key.sign(token_bytes).signature.hex()
            await ws.send(json.dumps({
                "type": "connect.response",
                "client_id": client_id,
                "signature": sig
            }))
            # 3. ACK
            ack = json.loads(await ws.recv())
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            print(f"[PERF] Iteration {i+1}: {latency_ms:.2f}ms")
            assert ack["type"] == "connect.ack"

    avg_latency = sum(latencies) / len(latencies)
    print(f"[PERF] Average Handshake Latency: {avg_latency:.2f}ms")
    
    # Target: < 200ms for local handshake
    assert avg_latency < 200
    
    gw_task.cancel()
    try: await gw_task
    except asyncio.CancelledError: pass

if __name__ == "__main__":
    pytest.main([__file__, "-s"])
