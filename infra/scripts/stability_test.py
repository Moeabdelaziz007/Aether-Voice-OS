import argparse
import asyncio
import json
import logging
import os
import time
from datetime import datetime

import psutil

from core.engine import AetherEngine
from core.infra.config import load_config
from core.infra.transport.bus import GlobalBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherStability")

class StabilityTester:
    def __init__(self, duration_sec: int = 60):
        self.duration_sec = duration_sec
        self.config = load_config()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration_sec,
            "telemetry": [],
            "bus_metrics": {}
        }

    async def run_resource_monitor(self):
        """Monitor CPU and RAM usage of the current process."""
        process = psutil.Process(os.getpid())
        end_time = time.time() + self.duration_sec
        
        print(f"📈 Starting Resource Monitor ({self.duration_sec}s)...", flush=True)
        while time.time() < end_time:
            mem_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=1.0)
            
            stats = {
                "time": time.time(),
                "cpu_percent": cpu_percent,
                "rss_mb": mem_info.rss / (1024 * 1024),
                "vms_mb": mem_info.vms / (1024 * 1024)
            }
            self.results["telemetry"].append(stats)
            if len(self.results["telemetry"]) % 10 == 0:
                print(f"  [TELEMETRY] CPU: {cpu_percent}% | RAM: {stats['rss_mb']:.2f}MB", flush=True)
            await asyncio.sleep(1.0)

    async def run_bus_stress(self, target_ops: int = 5000):
        """Stress test the GlobalBus with high-frequency messaging."""
        bus = GlobalBus()
        if not await bus.connect():
            print("❌ Bus Stress: Failed to connect to Redis.", flush=True)
            return

        print(f"⚡ Starting Bus Stress Test ({target_ops} msgs/sec target)...", flush=True)
        
        latencies = []
        start_time = time.perf_counter()
        count = 0
        
        # Test loop
        for i in range(target_ops):
            msg_start = time.perf_counter()
            await bus.publish("stress_test", {"id": i, "ts": msg_start})
            latencies.append(time.perf_counter() - msg_start)
            count += 1
            if count % 1000 == 0:
                print(f"  [BUS] Sent {count} messages...", flush=True)

        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        self.results["bus_metrics"] = {
            "total_messages": count,
            "duration_sec": total_duration,
            "throughput": count / total_duration,
            "avg_latency_ms": (sum(latencies) / len(latencies)) * 1000,
            "p99_latency_ms": sorted(latencies)[int(0.99 * len(latencies))] * 1000
        }
        
        print(f"✅ Bus Stress Complete: {count / total_duration:.2f} msgs/sec", flush=True)
        await bus.disconnect()

    async def execute(self, mode: str = "full"):
        if mode in ["full", "stability"]:
            # Start engine in background to test its idle leak profile
            engine = AetherEngine(self.config)
            engine_task = asyncio.create_task(engine.run())
            
            monitor_task = asyncio.create_task(self.run_resource_monitor())
            
            if mode == "full":
                await self.run_bus_stress()
            
            await monitor_task
            
            # Cleanup engine
            print("🛑 Shutting down engine...", flush=True)
            # Use a timeout or signal for the engine
            # For this script we just cancel
            engine_task.cancel()
        elif mode == "bus":
            await self.run_bus_stress()

        # Save results
        with open("stability_report.json", "w") as f:
            json.dump(self.results, f, indent=4)
        print("📊 Stability Report saved to stability_report.json", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "stability", "bus"], default="full")
    parser.add_argument("--duration", type=int, default=60)
    args = parser.parse_args()

    tester = StabilityTester(duration_sec=args.duration)
    asyncio.run(tester.execute(mode=args.mode))
