import sys
import types
from unittest.mock import MagicMock

compression_stub = types.ModuleType("core.ai.compression")


class NeuralSummarizer:
    def __init__(self, _config):
        pass

    def should_compress(self, _context):
        return False

    async def compress(self, _context):
        return None


compression_stub.NeuralSummarizer = NeuralSummarizer
sys.modules.setdefault("core.ai.compression", compression_stub)

genetic_stub = types.ModuleType("core.ai.genetic")


class AgentDNA:
    pass


class GeneticOptimizer:
    def __init__(self, *_args, **_kwargs):
        pass


genetic_stub.AgentDNA = AgentDNA
genetic_stub.GeneticOptimizer = GeneticOptimizer
sys.modules.setdefault("core.ai.genetic", genetic_stub)

from core.ai.hive import HiveCoordinator
from core.ai.handover_protocol import HandoverStatus


def test_prepare_handoff_without_negotiation_handles_prewarm_and_compression(monkeypatch):
    """Regression test for NameError when asyncio wasn't imported in hive.py."""
    registry = MagicMock()
    router = MagicMock()
    hive = HiveCoordinator(registry=registry, router=router, ai_config=object())

    summarizer = MagicMock()
    summarizer.should_compress.return_value = True
    hive._summarizer = summarizer

    scheduled_tasks = []

    def fake_create_task(coro):
        scheduled_tasks.append(coro)
        return MagicMock()

    monkeypatch.setattr("core.ai.hive.asyncio.create_task", fake_create_task)

    async def async_prewarm_callback(_target_name: str):
        return None

    hive.set_pre_warm_callback(async_prewarm_callback)

    success, context, message = hive.prepare_handoff(
        target_name="CodingExpert",
        task="Refactor the parser",
        enable_negotiation=False,
    )

    assert success is True
    assert context is not None
    assert message == "Handover prepared successfully"
    assert context.status == HandoverStatus.PRE_WARMING
    assert len(scheduled_tasks) == 2

    for task in scheduled_tasks:
        task.close()
