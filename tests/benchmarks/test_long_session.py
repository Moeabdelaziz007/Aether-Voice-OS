import asyncio
import time
import pytest
import json
import psutil
import os
from pathlib import Path
from core.infra.event_bus import EventBus, TelemetryEvent

@pytest.mark.asyncio
async def test_long_session_stability():
    """
    Systems Lab: Long Session Stability (Burn-in Test).
    Scenario: Run a high-load simulation for a set number of iterations 
    (simulating a long session) and monitor RAM/CPU growth.
    Note: For a real 30min test, this would be slow. Here we use high frequency 
    bursts to accelerate potential leak detection.
    """
    process = psutil.Process(os.getpid())
    bus = EventBus()
    await bus.start()
    
    initial_mem = process.memory_info().rss / 1024 / 1024 # MB
    
    # Simulation: 50,000 events in bursts
    iterations = 50
    events_per_burst = 1000
    
    history = []
    
    for i in range(iterations):
        for _ in range(events_per_burst):
            await bus.publish(TelemetryEvent(
                timestamp=time.time(),
                source="stability_test",
                latency_budget=1000,
                metric_name="ram_check",
                value=float(i)
            ))
        
        await asyncio.sleep(0.01) # Small rest
        current_mem = process.memory_info().rss / 1024 / 1024
        history.append({
            "iteration": i,
            "memory_mb": round(current_mem, 2)
        })
        
    final_mem = process.memory_info().rss / 1024 / 1024
    mem_growth = final_mem - initial_mem
    
    await bus.stop()
    
    metrics = {
        "benchmark": "long_session_stability",
        "duration_simulated_events": iterations * events_per_burst,
        "initial_memory_mb": round(initial_mem, 2),
        "final_memory_mb": round(final_mem, 2),
        "memory_growth_mb": round(mem_growth, 2),
        "history": history,
        "status": "success" if mem_growth < 50 else "warning" # 50MB growth for 50k events is safe
    }
    
    # Save report
    report_path = Path("tests/reports/stability_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🔋 Stability Test: Memory Growth: {mem_growth:.2f} MB")
    assert mem_growth < 100 # Safety limit
