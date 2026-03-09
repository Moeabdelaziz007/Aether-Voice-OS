"""
Aether Voice OS — GWS MCP Bridge.
Elite Model Context Protocol (MCP) client for real-time Google Workspace orchestration.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Log to OpenTelemetry-compatible logger via standard library
logger = logging.getLogger("AetherOS.GWSBridge")

class GWSMCPClient:
    """
    Elite MCP Client for Google Workspace.
    Maintains a persistent lifecycle with gws mcp to achieve <50ms dispatch latency.
    """

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._exit_stack = None
        self._client = None
        self._tools_cache: List[Dict[str, Any]] = []
        self._reconnect_attempts = 0
        self._max_backoff = 32  # seconds
        self._is_running = False
        self._lock = asyncio.Lock()

        # Command configuration
        self._command = "gws"
        self._args = ["mcp"]
        
        # Silent Auth via Service Account JSON
        self._env = os.environ.copy()
        sa_json = os.getenv("GWS_SERVICE_ACCOUNT_JSON")
        if sa_json:
            try:
                # Validate JSON structure silently
                json.loads(sa_json)
                logger.info("Service Account JSON detected. Silent authentication enabled.")
            except json.JSONDecodeError:
                logger.error("GWS_SERVICE_ACCOUNT_JSON is not a valid JSON string.")

    async def start(self):
        """Starts the MCP daemon with exponential backoff on failure."""
        async with self._lock:
            if self._is_running:
                return
            await self._connect()

    async def _connect(self):
        """Internal connection logic."""
        params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env
        )

        try:
            logger.info("Connecting to GWS MCP Daemon...")
            self._client = stdio_client(params)
            self._exit_stack = await self._client.__aenter__()
            read, write = self._exit_stack
            
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            
            await self.session.initialize()
            
            # Cache tools for immediate access
            result = await self.session.list_tools()
            self._tools_cache = [t.model_dump() for t in result.tools]
            
            self._is_running = True
            self._reconnect_attempts = 0
            logger.info("GWS MCP Connection established. Discovered %d tools.", len(self._tools_cache))
            
        except Exception as e:
            self._is_running = False
            logger.error("MCP Connection Failure: %s", str(e))
            asyncio.create_task(self._reconnect())

    async def _reconnect(self):
        """Implements exponential backoff for reconnection."""
        if self._is_running:
            return

        wait_time = min(2 ** self._reconnect_attempts, self._max_backoff)
        self._reconnect_attempts += 1
        
        logger.warning("Reconnecting to GWS MCP in %ds (Attempt %d)...", wait_time, self._reconnect_attempts)
        await asyncio.sleep(wait_time)
        await self._connect()

    async def stop(self):
        """Gracefully terminates the MCP session and daemon."""
        async with self._lock:
            self._is_running = False
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._client:
                await self._client.__aexit__(None, None, None)
            logger.info("GWS MCP Shutdown complete.")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Returns the cached list of discovered tools."""
        return self._tools_cache

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forwards tool calls to the MCP server with zero cold-start latency.
        """
        if not self.session or not self._is_running:
            return {
                "status": "error",
                "message": "GWS MCP Session not active",
                "x-a2a-status": 503
            }

        try:
            logger.debug("Dispatching GWS Tool: %s", name)
            result = await self.session.call_tool(name, arguments)
            
            if result.isError:
                return {
                    "status": "error",
                    "content": result.content,
                    "x-a2a-status": 400
                }
                
            return {
                "status": "success",
                "data": result.content,
                "x-a2a-status": 200
            }
        except Exception as e:
            logger.exception("MCP Tool Execution Error [%s]: %s", name, str(e))
            return {
                "status": "error",
                "message": str(e),
                "x-a2a-status": 500
            }

# Singleton instance for engine-wide use
gws_bridge = GWSMCPClient()

def get_discovered_tools() -> List[Dict[str, Any]]:
    """Helper for ToolRouter registration."""
    # Maps MCP tool definition to Aether Tool format
    tools = []
    for tool in gws_bridge.get_tools():
        tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["inputSchema"],
            "handler": lambda name=tool["name"], **kwargs: gws_bridge.execute_tool(name, kwargs),
            "latency_tier": "p95_sub_100ms",
        })
    return tools
