import asyncio
import logging
import sys
import time
from pathlib import Path

import numpy as np

# Add project root to path to allow imports from core
sys.path.insert(0, str(Path(__file__).parent.parent))


async def run_interrupt_drain(queue_size: int, items_in_queue: int) -> float:
    """
    Simulates the audio queue draining logic from AetherEngine._on_interrupt.

    This function creates a queue, fills it to a specified level, and then
    measures the time it takes to completely drain it using the same logic
    as the main engine's barge-in handler.

    Returns:
        float: The latency in milliseconds.
    """
    audio_out_queue = asyncio.Queue(maxsize=queue_size)

    # Pre-fill the queue with dummy audio data
    for _ in range(items_in_queue):
        await audio_out_queue.put(b"\x00" * 1024)

    # --- Start Measurement ---
    start_time = time.perf_counter()

    while not audio_out_queue.empty():
        try:
            audio_out_queue.get_nowait()
            audio_out_queue.task_done()
        except asyncio.QueueEmpty:
            break

    end_time = time.perf_counter()
    # --- End Measurement ---

    latency_ms = (end_time - start_time) * 1000
    return latency_ms


def log_stats(logger, latencies: list, scenario: str):
    """Helper to calculate and log statistics."""
    avg_latency = np.mean(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    p95_latency = np.percentile(latencies, 95)

    logger.info(scenario)
    logger.info(f"  -> Average Latency: {avg_latency:.4f} ms")
    logger.info(f"  -> Min Latency:     {min_latency:.4f} ms")
    logger.info(f"  -> Max Latency:     {max_latency:.4f} ms")
    logger.info(f"  -> 95th Percentile: {p95_latency:.4f} ms\n")


async def main():
    """Main function to run and report on the benchmark."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("BargeInBenchmark")

    logger.info("🚀 Running Barge-in Latency Benchmark...")
    logger.info(
        "This test measures the time to drain the outgoing audio queue upon "
        "user interruption.\n"
    )

    queue_size = 15  # From core/engine.py
    num_runs = 1000

    logger.info(f"Configuration: Queue Size = {queue_size}, Test Runs = {num_runs}\n")

    # --- Benchmark Scenarios ---
    full_queue_latencies = [
        await run_interrupt_drain(queue_size, queue_size) for _ in range(num_runs)
    ]
    log_stats(
        logger,
        full_queue_latencies,
        f"Scenario 1: Queue is 100% full ({queue_size}/{queue_size} items)",
    )

    half_queue_latencies = [
        await run_interrupt_drain(queue_size, queue_size // 2) for _ in range(num_runs)
    ]
    log_stats(
        logger,
        half_queue_latencies,
        f"Scenario 2: Queue is 50% full ({queue_size // 2}/{queue_size} items)",
    )


if __name__ == "__main__":
    asyncio.run(main())
