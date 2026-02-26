import asyncio
import time

import pytest

from core.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_tool_router_stress():
    """Stress test the Neural Dispatcher with high-concurrency tool calls."""
    router = ToolRouter()

    # 1. Register a dummy tool
    async def fast_tool(x: int) -> int:
        return x * 2

    router.register(
        name="fast_tool",
        description="A very fast tool for stress testing",
        parameters={"type": "object", "properties": {"x": {"type": "integer"}}},
        handler=fast_tool,
    )

    # 2. Simulate 1000 concurrent tool calls
    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args

    calls = [MockCall("fast_tool", {"x": i}) for i in range(1000)]

    start_time = time.monotonic()
    results = await asyncio.gather(*(router.dispatch(c) for c in calls))
    end_time = time.monotonic()

    duration = end_time - start_time
    throughput = len(calls) / duration

    print("\n🚀 Stress Test Results:")
    print(f"   Throughput: {throughput:.2f} calls/sec")
    print(f"   Total Time: {duration:.4f}s")

    # 3. Verify correctness
    assert len(results) == 1000
    assert all(r["result"]["data"] == i * 2 for i, r in enumerate(results))

    # 4. Verify profiling
    stats = router.get_performance_report()["fast_tool"]
    assert stats["count"] == 1000
    assert stats["p99"] > 0
    print(f"   p99 Latency: {stats['p99'] * 1000:.3f}ms")


@pytest.mark.asyncio
async def test_crash_isolation():
    """Ensure a failing tool doesn't crash the router."""
    router = ToolRouter()

    def failing_tool():
        raise RuntimeError("Neural cascade failure")

    router.register(
        name="failing_tool",
        description="A tool that always fails",
        parameters={},
        handler=failing_tool,
    )

    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args

    response = await router.dispatch(MockCall("failing_tool", {}))

    assert "error" in response
    assert "Neural cascade failure" in response["error"]
    print("\n🛡️ Crash Isolation: Verified (Failing tool handled gracefully)")
