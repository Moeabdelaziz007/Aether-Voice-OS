from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.ai.session.io_loops import drain_output, send_loop


@pytest.mark.asyncio
async def test_send_loop_consumes_queue():
    in_q = asyncio.Queue()
    await in_q.put({"data": b"1", "mime_type": "audio/pcm;rate=16000"})
    facade = SimpleNamespace(_running=True, _in_queue=in_q)
    session = SimpleNamespace(send_realtime_input=AsyncMock())

    task = asyncio.create_task(send_loop(facade, session))
    await asyncio.sleep(0.05)
    facade._running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    session.send_realtime_input.assert_awaited()


def test_drain_output_empties_queue():
    out_q = asyncio.Queue()
    out_q.put_nowait(b"a")
    out_q.put_nowait(b"b")
    facade = SimpleNamespace(_out_queue=out_q)
    drain_output(facade)
    assert out_q.empty()
