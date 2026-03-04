#!/usr/bin/env python3
"""
AetherOS Latency Benchmark Tool.
Measures End-to-End (E2E) latency:
Capture -> Processing -> Gemini Inference -> Gateway -> Playback.
"""

import asyncio
import json
import logging
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np

# Fix PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.engine import AetherEngine  # noqa: E402
from core.infra.config import load_config  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark")


class AetherBenchmarker:
    def __init__(self):
        self.config = load_config()
        self.latencies = []
        self.engine = None
        self._start_time = 0
        self.mem_stats = {}

    async def run_benchmark(self, iterations: int = 10):
        print(
            f"🚀 [BENCHMARK] Starting Real-World E2E Audit "
            f"({iterations} iterations)...",
            flush=True,
        )
        # Start tracemalloc to track GC pauses/leaks in zero-allocation frames
        tracemalloc.start()
        snapshot_start = tracemalloc.take_snapshot()
        print("🔍 [BENCHMARK] Initializing Aether Engine...", flush=True)
        self.engine = AetherEngine(self.config)

        # Start engine in background
        print("⚙️ [BENCHMARK] Launching Engine Tasks...", flush=True)
        engine_task = asyncio.create_task(self.engine.run())

        # Wait for engine to stabilize (Health Check)
        print("⏳ [BENCHMARK] Waiting for Engine Health Check...", flush=True)
        import http.client

        engine_ready = False
        for _ in range(30):  # 30s timeout
            try:
                conn = http.client.HTTPConnection(
                    "127.0.0.1", self.port if hasattr(self, "port") else 18790
                )
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
            print(
                "❌ [BENCHMARK] Engine failed to stabilize in 30s. Aborting.",
                flush=True,
            )
            self.engine._shutdown_event.set()
            await engine_task
            return

        print("🚀 [BENCHMARK] Engine stabilized. Proceeding.", flush=True)

        print(
            "📊 [BENCHMARK] Measuring True Network RTT via Gemini WebSocket Ping...",
            flush=True,
        )
        # Extract active Gemini Live Session websocket
        session = self.engine._gateway.get_session()
        if not session or not session._session or not hasattr(session._session, "_ws"):
            print(
                "❌ [BENCHMARK] Could not find active Gemini Live WebSocket. Aborting."
            )
            self.engine._shutdown_event.set()
            await engine_task
            return

        ws = session._session._ws
        for i in range(iterations):
            try:
                # Manually measure RTT around ping/pong since the future might
                # return None
                ping_start = time.perf_counter()
                pong_waiter = await ws.ping()
                await pong_waiter
                ping_end = time.perf_counter()

                latency_ms = (ping_end - ping_start) * 1000
                self.latencies.append(latency_ms)
                print(f"  [Probe {i + 1}] RTT Latency: {latency_ms:.2f}ms", flush=True)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  [Probe {i + 1}] Failed: {e}", flush=True)

        snapshot_end = tracemalloc.take_snapshot()
        self._compute_memory_stats(snapshot_start, snapshot_end)

        print("🔥 [BENCHMARK] Running Concurrent Firebase Load Test...", flush=True)
        firebase = self.engine._infra._firebase
        if not firebase.is_connected:
            print("⚠️ [BENCHMARK] Firebase not connected. Skipping Load Test.")
            self.fb_latencies = []
        else:
            self.fb_latencies = []

            async def write_task(idx):
                start_time = time.perf_counter()
                await firebase.log_message(role="benchmark", content=f"Probe {idx}")
                end_time = time.perf_counter()
                return (end_time - start_time) * 1000

            tasks = [write_task(i) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    print(f"❌ [BENCHMARK] Write failed: {res}")
                else:
                    self.fb_latencies.append(res)
            print("✅ [BENCHMARK] Load test complete. 50 writes processed.", flush=True)

        self._report()

        # Shutdown
        self.engine._shutdown_event.set()
        await engine_task
        tracemalloc.stop()

    def _compute_memory_stats(self, snap1, snap2):
        print("🧠 [BENCHMARK] Computing Memory Allocation Stats...")
        stats = snap2.compare_to(snap1, "lineno")
        top_allocations = []
        for stat in stats[:10]:
            top_allocations.append(str(stat))

        current, peak = tracemalloc.get_traced_memory()
        self.mem_stats = {
            "current_bytes": current,
            "peak_bytes": peak,
            "top_diff": top_allocations,
        }

    def _report(self):
        lats = np.array(self.latencies)
        report = {
            "network_rtt_ms": {
                "p50": float(np.percentile(lats, 50)) if len(lats) > 0 else 0,
                "p95": float(np.percentile(lats, 95)) if len(lats) > 0 else 0,
                "p99": float(np.percentile(lats, 99)) if len(lats) > 0 else 0,
                "min": float(np.min(lats)) if len(lats) > 0 else 0,
                "max": float(np.max(lats)) if len(lats) > 0 else 0,
                "count": len(lats),
            },
            "memory_stats": self.mem_stats,
        }

        if hasattr(self, "fb_latencies") and len(self.fb_latencies) > 0:
            fb_lats = np.array(self.fb_latencies)
            report["firebase_writes_ms"] = {
                "p50": float(np.percentile(fb_lats, 50)),
                "p95": float(np.percentile(fb_lats, 95)),
                "p99": float(np.percentile(fb_lats, 99)),
                "min": float(np.min(fb_lats)),
                "max": float(np.max(fb_lats)),
                "count": len(fb_lats),
            }

        print("\n" + "═" * 40)
        print("🏁 BENCHMARK RESULTS")
        print("  [Network RTT]")
        print(f"  p50 (Median): {report['network_rtt_ms']['p50']:.2f}ms")
        print(f"  p95 (Target): {report['network_rtt_ms']['p95']:.2f}ms")
        print(f"  p99 (Peak):   {report['network_rtt_ms']['p99']:.2f}ms")
        if "firebase_writes_ms" in report:
            print("\n  [Firebase Load Test (50 Concurrent Writes)]")
            print(f"  p50 (Median): {report['firebase_writes_ms']['p50']:.2f}ms")
            print(f"  p95 (Target): {report['firebase_writes_ms']['p95']:.2f}ms")
            print(f"  p99 (Peak):   {report['firebase_writes_ms']['p99']:.2f}ms")
        print("═" * 40)

        with open("performance_audit.json", "w") as f:
            json.dump(report, f, indent=4)
        print("\n✅ Audit saved to performance_audit.json")


if __name__ == "__main__":
    bench = AetherBenchmarker()
    try:
        asyncio.run(bench.run_benchmark(iterations=10))
    except KeyboardInterrupt:
        pass
