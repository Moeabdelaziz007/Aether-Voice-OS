#!/usr/bin/env python3
"""
Aether Voice OS — Automated E2E Voice Flow Benchmark
Measures Text-to-Audio (TTFB) Live Latency without requiring a microphone.
"""
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# Ensure Pydantic validation doesn't fail if only GEMINI_API_KEY is defined
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from core.ai.session.facade import GeminiLiveSession
from core.infra.config import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("e2e_benchmark")

async def run_automated_benchmark(iterations: int = 3):
    logger.info(f"Starting E2E Automated Benchmark ({iterations} iterations)")
    config = load_config()
    
    audio_in_queue = asyncio.Queue()
    audio_out_queue = asyncio.Queue()
    gateway = None
    
    session = GeminiLiveSession(
        config=config.ai, # ensure we pass AIConfig since config.py load_config returns AetherConfig
        audio_in_queue=audio_in_queue,
        audio_out_queue=audio_out_queue,
        gateway=gateway
    )
    
    await session.connect()
    
    stats = {
        "iterations": iterations,
        "ttfb_ms": [],
        "total_audio_chunks": [],
        "success_rate": 0,
        "errors": 0
    }
    
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(session.run())
            
            # Wait for session to initialize
            await asyncio.sleep(2.0)
            
            for i in range(iterations):
                logger.info(f"--- Iteration {i+1}/{iterations} ---")
                test_prompt = f"Please reply quickly. This is latency test iteration {i+1}."
                
                # Clear output queue from previous runs
                while not audio_out_queue.empty():
                    audio_out_queue.get_nowait()
                
                start_time = time.time()
                await session.send_text(test_prompt)
                
                # Wait for first audio chunk
                try:
                    # Time to First Byte (TTFB)
                    await asyncio.wait_for(audio_out_queue.get(), timeout=10.0)
                    ttfb = (time.time() - start_time) * 1000
                    logger.info(f"TTFB achieved: {ttfb:.2f} ms")
                    stats["ttfb_ms"].append(ttfb)
                    
                    # Drain the rest of the response to count chunks
                    chunks = 1
                    try:
                        while True:
                            await asyncio.wait_for(audio_out_queue.get(), timeout=2.0)
                            chunks += 1
                    except asyncio.TimeoutError:
                        pass
                        
                    logger.info(f"Iteration {i+1} completed. Total audio chunks: {chunks}")
                    stats["total_audio_chunks"].append(chunks)
                    
                except asyncio.TimeoutError:
                    logger.error("Timeout waiting for audio response")
                    stats["errors"] += 1
                
                # Wait before next iteration
                await asyncio.sleep(1.0)
                
            session._running = False
            
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        stats["errors"] += 1
        
    stats["success_rate"] = ((iterations - stats["errors"]) / iterations) * 100
    
    if stats["ttfb_ms"]:
        stats["avg_ttfb_ms"] = sum(stats["ttfb_ms"]) / len(stats["ttfb_ms"])
        stats["min_ttfb_ms"] = min(stats["ttfb_ms"])
        stats["max_ttfb_ms"] = max(stats["ttfb_ms"])
    else:
        stats["avg_ttfb_ms"] = 0
        
    print("\n" + "="*50)
    print(" E2E VOICE FLOW BENCHMARK RESULTS")
    print("="*50)
    print(json.dumps(stats, indent=2))
    
    report_file = ROOT / "tests" / "reports" / f"e2e_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True, parents=True)
    with open(report_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nReport saved to: {report_file}")
    
    return stats

if __name__ == "__main__":
    asyncio.run(run_automated_benchmark(iterations=3))
