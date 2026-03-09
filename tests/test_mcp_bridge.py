import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.ai.gws_bridge import GWSMCPClient


class AsyncContextManagerMock:
    async def __aenter__(self):
        return self.enter_return
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    def __init__(self, enter_return):
        self.enter_return = enter_return

@pytest.mark.asyncio
async def test_mcp_client_connection_flow():
    """
    Verifies the MCP client initialization and tool discovery flow.
    """
    # Create client
    client = GWSMCPClient()
    
    # Mock return values for read/write
    mock_read = AsyncMock()
    mock_write = AsyncMock()
    
    # Mock the stdio_client to return our async context manager
    with patch("core.ai.gws_bridge.stdio_client") as mock_stdio:
        mock_stdio.return_value = AsyncContextManagerMock((mock_read, mock_write))
        
        # Mock Session to be an async context manager
        with patch("core.ai.gws_bridge.ClientSession") as mock_session_class:
            mock_session = mock_session_class.return_value
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session.initialize = AsyncMock()
            
            # Mock tools
            mock_tool = MagicMock()
            mock_tool.model_dump.return_value = {"name": "list_files"}
            mock_result = MagicMock()
            mock_result.tools = [mock_tool]
            mock_session.list_tools = AsyncMock(return_value=mock_result)
            
            # Start client
            await client.start()
            
            assert client._is_running is True
            assert len(client.get_tools()) == 1
            assert client.get_tools()[0]["name"] == "list_files"
            
            # Stop client
            await client.stop()
            assert client._is_running is False

@pytest.mark.asyncio
async def test_mcp_tool_execution():
    """
    Verifies that tool calls are correctly forwarded to the MCP session.
    """
    client = GWSMCPClient()
    
    # Fake session and connection state
    client.session = AsyncMock()
    client._is_running = True
    
    # Mock successful call
    mock_result = MagicMock()
    mock_result.isError = False
    mock_result.content = "Success result from GWS"
    client.session.call_tool = AsyncMock(return_value=mock_result)
    
    response = await client.execute_tool("search_emails", {"query": "Aether"})
    
    assert response["status"] == "success"
    assert response["data"] == "Success result from GWS"
    client.session.call_tool.assert_called_once_with("search_emails", {})

@pytest.mark.asyncio
async def test_mcp_reconnection_logic():
    """
    Verifies that the client attempts reconnection on failure.
    """
    client = GWSMCPClient()
    client._max_backoff = 0.01 # Speed up test
    
    # Mock _connect directly to avoid dealing with the full stdio stack
    with patch.object(client, "_connect", wraps=client._connect) as mock_connect:
        # We need to mock the internals of _connect so it fails the first time
        with patch("core.ai.gws_bridge.stdio_client") as mc:
             # Patch ClientSession to avoid further errors on the second (successful) call

                # Trigger first connection attempt (which will raise)
                # start() calls _connect(), raising to trigger _reconnect()
                await client.start()
                
                # Reconnection is a separate task, wait a bit
                # The backoff is 1s, 2s, etc. but we can force wait
                await asyncio.sleep(1.2)
                
                # Should have tried reaching _connect at least twice
                assert mock_connect.call_count >= 2
