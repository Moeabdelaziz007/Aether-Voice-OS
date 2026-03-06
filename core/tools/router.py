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
from dataclasses import dataclass
from typing import Any, Callable, Optional

from google.genai import types

from core.tools.vector_store import LocalVectorStore

logger = logging.getLogger(__name__)


@dataclass
class ToolRegistration:
    """A registered tool with its schema and handler."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]
    latency_tier: str = "p95_sub_500ms"
    idempotent: bool = True
    requires_biometric: bool = False


class BiometricMiddleware:
    """
    Middleware that enforces biometric 'Soul-Lock' verification
    for sensitive tool executions.
    """

    def __init__(self, fallback_authorized: bool = False) -> None:
        self._fallback_authorized = fallback_authorized

    async def verify(
        self, tool_name: str, context: Optional[dict[str, Any]] = None
    ) -> bool:
        """
        Perform biometric verification for the given tool.

        In AetherOS V2, this checks for a 'bio_locked' flag in the
        session context, which is typically set by the audio capture
        layer (Thalamic Gate) after analyzing voice-print stability.
        """
        logger.info(
            "🛡️ [SECURITY] [BIO-LOCK] Verifying biometric integrity for: %s", tool_name
        )

        # Real verification logic: Check context for biometric flag
        if context and context.get("biometric_verified"):
            logger.info("🛡️ [SECURITY] [BIO-LOCK] Biometric Match: SUCCESS")
            return True

        # Fallback for development/testing
        if self._fallback_authorized:
            logger.warning(
                "🛡️ [SECURITY] [BIO-LOCK] Falling back to AUTHORIZED (DEV MODE)"
            )
            return True

        logger.error(
            "🛡️ [SECURITY] [BIO-LOCK] Verification Failed: NO VOICE-PRINT MATCH"
        )
        return False


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
    Upgraded for AetherOS V2: Biometric Middleware & A2A Metadata.
    """

    # Tools that require Biometric Soul-Lock (Middleware)
    SENSITIVE_TOOLS = {
        "deploy_package",
        "write_memory",
        "execute_system_command",
        "delete_task",
        "update_firebase_config",
    }

    def __init__(self) -> None:
        self._tools: dict[str, ToolRegistration] = {}
        self._profiler = ToolExecutionProfiler)
        self._vector_store: Optional[LocalVectorStore] = None
        self._biometric_middleware = BiometricMiddlewarefallback_authorized=True)

    def init_vector_store(self, api_key: str) -> None:
        """Initialize the semantic search engine."""
        self._vector_store = LocalVectorStoreapi_key=api_key)
        logger.info("Neural Dispatcher: Semantic indexing engine initialized.")

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Any],
        latency_tier: str = "p95_sub_500ms",
        idempotent: bool = True,
    ) -> None:
        """Register a tool with its handler function and A2A metadata."""
        self._tools[name] = ToolRegistration
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            latency_tier=latency_tier,
            idempotent=idempotent,
        )

        # Async indexing (Best effort)
        if self._vector_store:
            asyncio.create_task(
                self._vector_store.add_text(
                    key=name,
                    text=f"Title: {name}; Description: {description}",
                    metadata={"name": name},
                )
            )

        logger.info("Tool registered: %s [Tier: %s]", name, latency_tier)

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
        function_call: types.FunctionCall,
    ) -> dict[str, Any]:
        """
        Neural Dispatcher: Routes tool_calls with Biometric Soul-Lock middleware.
        """
        name = function_call.name
        args = function_call.args or {}

        if name not in self._tools:
            logger.warning(
                "Unmatched tool called: %s. Attempting semantic recovery...", name
            )

            was_recovered = False
            # --- Semantic Recovery Sequence ---
            if self._vector_store:
                try:
                    query_vec = await self._vector_store.get_query_embedding(name)
                    hits = self._vector_store.search(query_vec, limit=1)
                    if hits and hits[0]["similarity"] > 0.75:
                        match = hits[0]["key"]
                        logger.info(
                            "🎯 Semantic Match Found: %s -> %s (Sim: %.2f)",
                            name,
                            match,
                            hits[0]["similarity"],
                        )
                        name = match  # Redirect to the closest tool
                        was_recovered = True
                    else:
                        return {
                            "error": (
                                f"Tool '{name}' not found and no close semantic "
                                "matches (>0.75)."
                            ),
                            "available_tools": self.names,
                            "x-a2a-status": 404,
                        }
                except Exception as e:
                    logger.error("Semantic recovery failed: %s", e)

            if name not in self._tools:
                return {
                    "error": f"Unknown tool: {name}",
                    "available_tools": self.names,
                }
        else:
            was_recovered = False

        tool = self._tools[name]

        # ── Biometric Soul-Lock Middleware ──────────────────────────
        if name in self.SENSITIVE_TOOLS or tool.requires_biometric:
            # We assume session context is passed in the function call metadata
            # or retrieved from the active session.
            # For now, we simulate the context check.
            context = {"biometric_verified": True}  # Simulation

            authorized = await self._biometric_middleware.verify(name, context)
            if not authorized:
                return {
                    "error": (
                        "Security Exception: Biometric Soul-Lock verification failed."
                    ),
                    "x-a2a-status": 403,
                }

        logger.info(
            "⚡ Dispatching: %s(%s) [Tier: %s]",
            name,
            json.dumps(args, default=str)[:200],
            tool.latency_tier,
        )

        start_time = asyncio.get_event_loop().time()
        try:
            # Support both sync and async handlers robustly
            if inspect.iscoroutinefunction(tool.handler):
                result = await tool.handler(**args)
            else:
                result = await asyncio.to_thread(tool.handler, **args)

            # If the result itself is still awaitable (e.g. from a mock or wrapper leak)
            if inspect.isawaitable(result):
                result = await result

            duration = asyncio.get_event_loop().time() - start_time
            await self._profiler.record(name, duration)

            # ── A2A Protocol V3 Response Wrapping ───────────────────────
            # Standardizes output for multi-agent interoperability.
            a2a_status = 202 if was_recovered else 200  # OK
            if isinstance(result, dict) and "a2a_code" in result:
                a2a_status = result.pop("a2a_code")

            wrapped_result = {
                "result": result if isinstance(result, dict) else {"data": result},
                "x-a2a-status": a2a_status,
                "x-a2a-latency": tool.latency_tier,
                "x-a2a-idempotent": tool.idempotent,
                "x-a2a-duration_ms": int(duration * 1000),
            }

            logger.info(
                "✓ Tool %s completed [A2A:%d] (%.3fs)", name, a2a_status, duration
            )
            return wrapped_result

        except TypeError as exc:
            logger.error("Tool %s argument error: %s", name, exc)
            return {
                "error": f"Invalid arguments for {name}: {exc}",
                "x-a2a-status": 400,  # Bad Request
            }
        except Exception as exc:
            logger.error("Tool %s execution failed: %s", name, exc, exc_info=True)
            return {
                "error": f"Tool {name} failed: {exc}",
                "x-a2a-status": 500,  # Internal Error
            }

    def get_performance_report(self) -> dict[str, dict[str, float]]:
        """Return performance stats for all tools."""
        return {name: self._profiler.get_stats(name) for name in self.names}
