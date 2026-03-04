import asyncio
import time
import json
import os

async def measure_block(func, *args, **kwargs):
    start = time.perf_counter()
    loop = asyncio.get_running_loop()

    ticks = []
    async def ticker():
        for _ in range(20):
            await asyncio.sleep(0.001)
            ticks.append(time.perf_counter())
        return ticks

    t_task = asyncio.create_task(ticker())
    await func(*args, **kwargs)

    await t_task
    # Calculate max delay between ticks
    delays = [ticks[i+1] - ticks[i] for i in range(len(ticks)-1)]
    max_delay = max(delays) if delays else 0

    end = time.perf_counter()
    return end - start, max_delay

async def run_sync_io():
    results = {"large_data": ["a" * 100] * 10000}
    with open(".test_tmp1.log", "w") as f:
        f.write("A"*1000000)
    with open(".test_tmp2.json", "w") as f:
        json.dump(results, f, indent=4)

async def run_async_io():
    results = {"large_data": ["a" * 100] * 10000}
    def _write_log():
        with open(".test_tmp1.log", "w") as f:
            f.write("A"*1000000)
    def _write_json():
        with open(".test_tmp2.json", "w") as f:
            json.dump(results, f, indent=4)

    await asyncio.to_thread(_write_log)
    await asyncio.to_thread(_write_json)

async def main():
    print("Running Sync...")
    s_dur, s_block = await measure_block(run_sync_io)
    print(f"Sync IO duration: {s_dur:.4f}s")
    print(f"Max sync event loop blocking delay: {s_block:.4f}s\n")

    print("Running Async...")
    a_dur, a_block = await measure_block(run_async_io)
    print(f"Async IO duration: {a_dur:.4f}s")
    print(f"Max async event loop blocking delay: {a_block:.4f}s")

    os.remove(".test_tmp1.log")
    os.remove(".test_tmp2.json")

if __name__ == "__main__":
    asyncio.run(main())
