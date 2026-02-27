from types import SimpleNamespace

import pytest

from core.engine import AetherEngine


class FakeEvent:
    def __init__(self, text: str, is_final: bool):
        self.text = text
        self._is_final = is_final

    def is_final_response(self) -> bool:
        return self._is_final


def make_async_gen(events):
    async def _gen():
        for event in events:
            yield event

    return _gen()


@pytest.mark.asyncio
async def test_delegate_complex_task_success():
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOOGLE_API_KEY", "test-key")
        engine = AetherEngine()

    events = [FakeEvent("partial", False), FakeEvent("final response", True)]
    engine._adk_runner = SimpleNamespace(run_async=lambda task: make_async_gen(events))

    response = await engine._delegate_complex_task("build a plan")

    assert response["status"] == "success"
    assert "final response" in response["response"]


@pytest.mark.asyncio
async def test_delegate_complex_task_no_final_response():
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOOGLE_API_KEY", "test-key")
        engine = AetherEngine()

    events = [FakeEvent("partial", False)]
    engine._adk_runner = SimpleNamespace(run_async=lambda task: make_async_gen(events))

    response = await engine._delegate_complex_task("do work")

    assert response["status"] == "error"
    assert "No response" in response["message"]


@pytest.mark.asyncio
async def test_handle_complex_task_returns_text_without_session():
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOOGLE_API_KEY", "test-key")
        engine = AetherEngine()

    events = [FakeEvent("final response", True)]
    engine._adk_runner = SimpleNamespace(run_async=lambda task: make_async_gen(events))

    text = await engine._handle_complex_task("design database")

    assert text == "final response"
