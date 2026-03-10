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
        self._prompts_cache: List[Dict[str, Any]] = []
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
        params = StdioServerParameters(command=self._command, args=self._args, env=self._env)

        try:
            logger.info("Connecting to GWS MCP Daemon...")
            self._client = stdio_client(params)
            self._exit_stack = await self._client.__aenter__()
            read, write = self._exit_stack

            self.session = ClientSession(read, write)
            await self.session.__aenter__()

            await self.session.initialize()

            # Cache tools and prompts (Elite Skills) for immediate access
            result_tools = await self.session.list_tools()
            self._tools_cache = [t.model_dump() for t in result_tools.tools]

            try:
                result_prompts = await self.session.list_prompts()
                self._prompts_cache = [p.model_dump() for p in result_prompts.prompts]
                logger.debug("Discovered %d MCP Prompts (GWS Skills).", len(self._prompts_cache))
            except Exception:
                logger.debug("MCP Prompts discovery not supported or failed.")

            self._is_running = True
            self._reconnect_attempts = 0
            logger.info(
                "GWS MCP Connection established. Discovered %d tools and %d skills/prompts.",
                len(self._tools_cache),
                len(self._prompts_cache),
            )

        except Exception as e:
            self._is_running = False
            logger.error("MCP Connection Failure: %s", str(e))
            asyncio.create_task(self._reconnect())

    async def _reconnect(self):
        """Implements exponential backoff for reconnection."""
        if self._is_running:
            return

        wait_time = min(2**self._reconnect_attempts, self._max_backoff)
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

    def get_prompts(self) -> List[Dict[str, Any]]:
        """Returns the cached list of discovered prompts (Skills)."""
        return self._prompts_cache

    async def execute_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves a prompt (Skill recipe) from the MCP server.
        """
        if not self.session or not self._is_running:
            return {"status": "error", "message": "GWS MCP Session not active"}

        try:
            logger.debug("Fetching GWS Prompt: %s", name)
            result = await self.session.get_prompt(name, arguments)
            return {
                "status": "success",
                "description": result.description,
                "messages": [m.model_dump() for m in result.messages],
            }
        except Exception as e:
            logger.error("MCP Prompt Execution Error [%s]: %s", name, str(e))
            return {"status": "error", "message": str(e)}

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forwards tool calls to the MCP server with zero cold-start latency.
        """
        if not self.session or not self._is_running:
            return {"status": "error", "message": "GWS MCP Session not active", "x-a2a-status": 503}

        try:
            logger.debug("Dispatching GWS Tool: %s", name)
            result = await self.session.call_tool(name, arguments)

            if result.isError:
                return {"status": "error", "content": result.content, "x-a2a-status": 400}

            return {"status": "success", "data": result.content, "x-a2a-status": 200}
        except Exception as e:
            logger.exception("MCP Tool Execution Error [%s]: %s", name, str(e))
            return {"status": "error", "message": str(e), "x-a2a-status": 500}


# Singleton instance for engine-wide use
gws_bridge = GWSMCPClient()


def get_discovered_tools() -> List[Dict[str, Any]]:
    """Helper for ToolRouter registration."""
    # Maps MCP tool definition to Aether Tool format
    tools = []

    # 1. Essential Tools (Direct Mapping for high performance)
    essential_keywords = ["gmail", "calendar", "drive", "docs", "sheets"]
    discovered_mcp_tools = gws_bridge.get_tools()

    for tool in discovered_mcp_tools:
        # We categorize certain tools as "Essential" for direct registration
        is_essential = any(k in tool["name"].lower() for k in essential_keywords)

        # Limit direct registration to ~20 essential tools to maintain latency
        if is_essential and len(tools) < 25:
            tools.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"],
                    "handler": lambda name=tool["name"], **kwargs: gws_bridge.execute_tool(name, kwargs),
                    "latency_tier": "p95_sub_100ms",
                }
            )

    # 2. Meta-Tools for the "100+ Skills" and non-essential tools
    tools.append(
        {
            "name": "list_gws_skills",
            "description": "Lists the 100+ specialized Google Workspace agent skills and recipes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'research', 'automation')",
                    }
                },
            },
            "handler": lambda **kwargs: {
                "skills": [
                    {"name": p["name"], "description": p["description"]}
                    for p in gws_bridge.get_prompts()
                    if not kwargs.get("category") or kwargs["category"] in p["name"].lower()
                ],
                "note": "Use use_gws_skill(name) to execute one of these recipes.",
            },
        }
    )

    tools.append(
        {
            "name": "use_gws_skill",
            "description": "Executes a specialized GWS agent skill/recipe found via list_gws_skills.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "The exact name of the skill to execute."},
                    "arguments": {"type": "object", "description": "Arguments required by the skill recipe."},
                },
                "required": ["skill_name"],
            },
            "handler": lambda skill_name, arguments=None, **kwargs: gws_bridge.execute_prompt(
                skill_name, arguments or {}
            ),
        }
    )

    return tools
