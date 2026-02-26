"""
Aether Voice OS — Tool Router (Neural Dispatcher V2).

Routes Gemini Live `tool_call` messages to registered handler functions.
This is the central nervous dispatcher: when Gemini decides it needs
to execute a function (e.g., "create_task"), the router finds the
correct handler and executes it.

Architecture:
  Gemini → tool_call → ToolRouter.dispatch() → handler_fn → tool_response → Gemini

The router maintains a registry of:
  - Function declarations (sent to Gemini at session start)
  - Handler callables (invoked when Gemini emits a tool_call)
"""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from google.genai import types

logger = logging.getLogger(__name__)


@dataclass
class ToolRegistration:
    """A registered tool with its schema and handler."""
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]


class ToolExecutionProfiler:
    """Tracks performance metrics for tool executions."""
    
    def __init__(self) -> None:
        self._execution_times: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def record(self, tool_name: str, duration: float) -> None:
        """Record an execution duration for a tool."""
        async with self._lock:
            if tool_name not in self._execution_times:
                self._execution_times[tool_name] = []
            # Keep only the last 1000 samples per tool to prevent memory leak
            self._execution_times[tool_name].append(duration)
            if len(self._execution_times[tool_name]) > 1000:
                self._execution_times[tool_name].pop(0)

    def get_stats(self, tool_name: str) -> dict[str, float]:
        """Calculate p50, p95, and p99 latencies for a tool."""
        times = sorted(self._execution_times.get(tool_name, []))
        if not times:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "count": 0}
        
        count = len(times)
        return {
            "p50": times[int(count * 0.5)],
            "p95": times[int(count * 0.95)] if count >= 20 else times[-1],
            "p99": times[int(count * 0.99)] if count >= 100 else times[-1],
            "avg": sum(times) / count,
            "count": count,
        }


class ToolRouter:
    """
    Central dispatcher for Gemini Live function calling.

    Usage:
        router = ToolRouter()
        router.register(
            name="get_current_time",
            description="Returns the current date and time",
            parameters={},
            handler=my_time_handler,
        )

        # Get declarations for LiveConnectConfig
        declarations = router.get_declarations()

        # When Gemini emits a tool_call:
        response = await router.dispatch(function_call)
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolRegistration] = {}
        self._profiler = ToolExecutionProfiler()

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """Register a tool with its handler function."""
        self._tools[name] = ToolRegistration(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        logger.info("Tool registered: %s", name)

    def un_register(self, name: str) -> None:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            logger.info("Tool un-registered: %s", name)

    def register_module(self, module: Any) -> None:
        """
        Register all tools from a module that exposes `get_tools()`.

        Modules should implement:
            def get_tools() -> list[dict]
        where each dict has: name, description, parameters, handler
        """
        if not hasattr(module, "get_tools"):
            logger.warning(
                "Module %s has no get_tools() method — skipping",
                module.__name__ if hasattr(module, "__name__") else module,
            )
            return

        for tool_def in module.get_tools():
            self.register(**tool_def)

    @property
    def count(self) -> int:
        """Number of registered tools."""
        return len(self._tools)

    @property
    def names(self) -> list[str]:
        """Names of all registered tools."""
        return list(self._tools.keys())

    def get_declarations(self) -> list[types.FunctionDeclaration]:
        """
        Generate Gemini-compatible function declarations.

        Returns a list of FunctionDeclaration objects to pass
        into LiveConnectConfig.tools.
        """
        declarations = []
        for tool in self._tools.values():
            decl = types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters if tool.parameters else None,
            )
            declarations.append(decl)

        logger.debug(
            "Generated %d function declarations: %s",
            len(declarations),
            [d.name for d in declarations],
        )
        return declarations

    async def dispatch(
        self,
        function_call: Any,
    ) -> dict[str, Any]:
        """
        Dispatch a Gemini function_call to its registered handler.

        Args:
            function_call: The function call object from Gemini,
                           with .name and .args attributes.

        Returns:
            A dict with the tool response to send back to Gemini.
        """
        name = function_call.name
        args = function_call.args or {}

        if name not in self._tools:
            logger.error("Unknown tool called: %s", name)
            return {
                "error": f"Unknown tool: {name}",
                "available_tools": self.names,
            }

        tool = self._tools[name]
        logger.info(
            "⚡ Dispatching tool call: %s(%s)",
            name,
            json.dumps(args, default=str)[:200],
        )

        start_time = asyncio.get_event_loop().time()
        try:
            # Support both sync and async handlers
            if inspect.iscoroutinefunction(tool.handler):
                result = await tool.handler(**args)
            else:
                result = await asyncio.to_thread(tool.handler, **args)

            duration = asyncio.get_event_loop().time() - start_time
            await self._profiler.record(name, duration)

            logger.info("✓ Tool %s completed successfully (%.3fs)", name, duration)
            return result if isinstance(result, dict) else {"result": result}

        except TypeError as exc:
            logger.error("Tool %s argument error: %s", name, exc)
            return {"error": f"Invalid arguments for {name}: {exc}"}
        except Exception as exc:
            logger.error("Tool %s execution failed: %s", name, exc, exc_info=True)
            return {"error": f"Tool {name} failed: {exc}"}

    def get_performance_report(self) -> dict[str, dict[str, float]]:
        """Return performance stats for all tools."""
        return {name: self._profiler.get_stats(name) for name in self.names}
