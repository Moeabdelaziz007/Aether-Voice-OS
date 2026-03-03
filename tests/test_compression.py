"""
Aether Voice OS — Neural Summarizer Unit Tests.
"""

import asyncio
import pytest
from unittest.mock import MagicMock
from core.ai.compression import NeuralSummarizer
from core.ai.handover_protocol import HandoverContext, ConversationEntry, WorkingMemory
from core.infra.config import AIConfig

@pytest.fixture
def mock_config():
    config = MagicMock(spec=AIConfig)
    config.api_key = "test_key"
    return config

@pytest.mark.asyncio
async def test_summarizer_should_compress():
    summarizer = NeuralSummarizer(MagicMock())
    
    # Small context should not trigger compression
    small_context = HandoverContext(
        handover_id="test-1",
        source_agent="A",
        target_agent="B",
        task="Test small",
        conversation_history=[]
    )
    assert summarizer.should_compress(small_context) is False
    
    # Large context should trigger compression
    large_history = [
        ConversationEntry(speaker="User", message="Hello" * 100)
    ] * 25
    large_context = HandoverContext(
        handover_id="test-2",
        source_agent="A",
        target_agent="B",
        task="Test large",
        conversation_history=large_history
    )
    assert summarizer.should_compress(large_context) is True

@pytest.mark.asyncio
async def test_summarizer_compress_fallback(mock_config):
    # Test that it handles errors gracefully
    summarizer = NeuralSummarizer(mock_config)
    
    # Mock the client to raise an exception
    summarizer._client.models.generate_content = MagicMock(side_effect=Exception("API Error"))
    
    context = HandoverContext(
        handover_id="test-3",
        source_agent="A",
        target_agent="B",
        task="Test fallback",
        conversation_history=[ConversationEntry(speaker="User", message="Test")]
    )
    
    seed = await summarizer.compress(context)
    assert "error" in seed
    assert seed["fallback_summary"] == "Test fallback"
