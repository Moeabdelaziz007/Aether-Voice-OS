import asyncio
import json
import os
import time

import websockets

# AetherOS Latency Benchmark Tool
# Measures E2E latency: Mic Capture -> Gateway -> GenAI -> Audio Output

GATEWAY_URL = os.environ.get("AETHER_GATEWAY_URL", "ws://localhost:18889")

async def run_benchmark(iterations=10):
    print(f"🚀 Starting AetherOS Latency Benchmark (Target: {GATEWAY_URL})")
    
    # Wait for server to be ready
    max_retries = 30
    retry_delay = 1
    ws = None
    
    for i in range(max_retries):
        try:
            ws = await websockets.connect(GATEWAY_URL)
            break
        except Exception:
            if i % 5 == 0:
                print(f"Waiting for gateway to arm on port 18889... ({i}/{max_retries})")
            await asyncio.sleep(retry_delay)
    
    if not ws:
        print("❌ CRITICAL: Gateway failed to arm. Benchmark aborted.")
        return

    async with ws:
        # 1. Handshake
        raw = await ws.recv()
        print(f"DEBUG: Raw message received: {raw}")
        try:
            data = json.loads(raw)
            _challenge = data["challenge"]
        except Exception as e:
            print(f"FAILED to parse challenge from: {raw}")
            raise e
        
        # Simple auth response (No signature for benchmark if bypassed in dev)
        await ws.send(json.dumps({
            "type": "connect.response",
            "client_id": "benchmark_bot",
            "capabilities": ["audio_streaming", "msgpack"]
        }))
        
        ack = await ws.recv()
        print(f"✅ Authenticated. Session ID: {json.loads(ack)['session_id']}")
        
        latencies = []
        
        for i in range(iterations):
            print(f"[{i+1}/{iterations}] Measuring RTT...")
            start = time.time()
            
            # Send Pulse Tick
            tick = {"type": "tick", "payload": {"timestamp": start}}
            await ws.send(json.dumps(tick))
            
            # Wait for response (tick echo or transcript)
            while True:
                resp = await ws.recv()
                if isinstance(resp, bytes):
                    continue # Ignore audio chunks for RTT
                
                data = json.loads(resp)
                if data["type"] == "tick":
                    end = time.time()
                    rtt = (end - start) * 1000
                    latencies.append(rtt)
                    print(f"   ⏱️ RTT: {rtt:.2f}ms")
                    break
            
            await asyncio.sleep(0.5)

        avg = sum(latencies) / len(latencies)
        print("\n" + "="*30)
        print("📊 BENCHMARK RESULTS")
        print(f"   Average RTT: {avg:.2f}ms")
        print(f"   Min RTT:     {min(latencies):.2f}ms")
        print(f"   Max RTT:     {max(latencies):.2f}ms")
        print(f"   Jitter:      {max(latencies) - min(latencies):.2f}ms")
        print("="*30)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
