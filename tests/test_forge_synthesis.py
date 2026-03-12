"""
Tests for ForgeOrchestrator in core.ai.session.
"""

import pytest
import shutil
from unittest.mock import AsyncMock, MagicMock, patch

from core.ai.session.forge_orchestrator import ForgeOrchestrator

@pytest.mark.asyncio
async def test_forge_synthesis_flow(tmp_path):
    session_facade = MagicMock()
    session_facade._client = MagicMock()
    session_facade._client.aio.models.generate_content = AsyncMock()
    session_facade._firebase = MagicMock()
    session_facade._firebase.search_neural_synapses = AsyncMock(return_value=[])
    session_facade._firebase.log_vector_memory = AsyncMock()
    session_facade.send_transcription = AsyncMock()
    
    mock_response = MagicMock()
    mock_response.text = '{"name": "SecurityExpert", "description": "Security Agent", "instructions": "test", "expertise": {"sec": 1.0}}'
    session_facade._client.aio.models.generate_content.return_value = mock_response
    
    session_facade._agent_registry = MagicMock()
    session_facade._gateway = MagicMock()
    session_facade._gateway.broadcast = AsyncMock()
    
    orchestrator = ForgeOrchestrator(session_facade)
    
    with patch("core.ai.session.forge_orchestrator.create_agent") as mock_create:
        mock_create.return_value = {"status": "success"}
        
        result = await orchestrator.forge_and_activate("I want a security expert")
        
        assert result["status"] == "success"
        session_facade._agent_registry.register_agent.assert_called_once()
        mock_create.assert_called_once()
