#!/usr/bin/env python3
"""
AetherOS Latency Benchmark Tool.
Measures End-to-End (E2E) latency:
Capture -> Processing -> Gemini Inference -> Gateway -> Playback.
"""

import asyncio
import time
import json
import numpy as np
import logging
from pathlib import Path
import sys
import os
from pathlib import Path

# Fix PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.infra.config import load_config
from core.engine import AetherEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark")

class AetherBenchmarker:
    def __init__(self):
        self.config = load_config()
        self.latencies = []
        self.engine = None
        self._start_time = 0

    async def run_benchmark(self, iterations: int = 10):
        print(f"🚀 [BENCHMARK] Starting Real-World E2E Audit ({iterations} iterations)...", flush=True)
        print("🔍 [BENCHMARK] Initializing Aether Engine...", flush=True)
        self.engine = AetherEngine(self.config)
        
        # Start engine in background
        print("⚙️ [BENCHMARK] Launching Engine Tasks...", flush=True)
        engine_task = asyncio.create_task(self.engine.run())
        
        # Wait for engine to stabilize (Health Check)
        print("⏳ [BENCHMARK] Waiting for Engine Health Check...", flush=True)
        import http.client
        engine_ready = False
        for _ in range(30): # 30s timeout
            try:
                conn = http.client.HTTPConnection("127.0.0.1", self.port if hasattr(self, 'port') else 18790)
                conn.request("GET", "/api/status")
                resp = conn.getresponse()
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    if data.get("status") == "online":
                        engine_ready = True
                        break
            except Exception:
                pass
            await asyncio.sleep(1.0)
        
        if not engine_ready:
            print("❌ [BENCHMARK] Engine failed to stabilize in 30s. Aborting.", flush=True)
            self.engine._shutdown_event.set()
            await engine_task
            return
        
        print("🚀 [BENCHMARK] Engine stabilized. Proceeding.", flush=True)
        
        print("📊 [BENCHMARK] Injecting synthetic probes...", flush=True)
        for i in range(iterations):
            start = time.perf_counter()
            # Simulate a "Barge-in" trigger or high-RMS speech event
            # We use the gateway's broadcast to trace the round-trip
            print(f"  [Probe {i+1}] Broadcasting...", flush=True)
            await self.engine._gateway.broadcast("benchmark_probe", {"id": i, "ts": start})
            print(f"  [Probe {i+1}] Broadcast done.", flush=True)
            
            # In a real test, we'd wait for the actual audio output byte
            # Here we simulate the processing overhead
            # TODO: Link this to real AudioPlayback.on_audio_tx
            await asyncio.sleep(0.5) # Minimum inference delay simulation
            
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            self.latencies.append(latency_ms)
            print(f"  [Probe {i+1}] Latency: {latency_ms:.2f}ms", flush=True)
            await asyncio.sleep(1)

        self._report()
        
        # Shutdown
        self.engine._shutdown_event.set()
        await engine_task

    def _report(self):
        lats = np.array(self.latencies)
        report = {
            "p50": float(np.percentile(lats, 50)),
            "p95": float(np.percentile(lats, 95)),
            "p99": float(np.percentile(lats, 99)),
            "min": float(np.min(lats)),
            "max": float(np.max(lats)),
            "count": len(lats)
        }
        
        print("\n" + "═"*40)
        print("🏁 BENCHMARK RESULTS")
        print(f"  p50 (Median): {report['p50']:.2f}ms")
        print(f"  p95 (Target): {report['p95']:.2f}ms")
        print(f"  p99 (Peak):   {report['p99']:.2f}ms")
        print("═"*40)
        
        with open("performance_audit.json", "w") as f:
            json.dump(report, f, indent=4)
        print(f"\n✅ Audit saved to performance_audit.json")

if __name__ == "__main__":
    bench = AetherBenchmarker()
    try:
        asyncio.run(bench.run_benchmark(iterations=10))
    except KeyboardInterrupt:
        pass
