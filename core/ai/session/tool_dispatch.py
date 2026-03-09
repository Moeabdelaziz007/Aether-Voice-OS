from __future__ import annotations

import asyncio
import logging
import os
from time import perf_counter

from google.genai import types

from core.infra.telemetry import (
    get_tool_timeout_dashboard,
    record_tool_dispatch_telemetry,
)

logger = logging.getLogger(__name__)


async def handle_tool_call(session_facade, session, tool_call) -> None:
    if not session_facade._tool_router:
        return

    calls = tool_call.function_calls or []

    async def _dispatch_with_timeout(fc):
        # O(1) Tool Latency Config
        latency_config = {
            "discovery_tool": (8.0, "fast"),
            "search_tool": (8.0, "fast"),
            "vision_tool": (18.0, "slow"),
            "camera_tool": (18.0, "slow"),
            "hive_tool": (18.0, "slow"),
        }
        
        timeout_s, latency_tier = latency_config.get(fc.name, (25.0, "medium"))

        if session_facade._scheduler:
            session_facade._scheduler.on_tool_start(fc.name, fc.args)

        started = perf_counter()
        try:
            return await asyncio.wait_for(
                session_facade._tool_router.dispatch(fc),
                timeout=timeout_s,
            )
        except asyncio.TimeoutError:
            elapsed_ms = int((perf_counter() - started) * 1000)
            record_tool_dispatch_telemetry(fc.name, elapsed_ms, "timeout")
            return {
                "status": "timeout",
                "error": f"Tool '{fc.name}' exceeded latency budget for {latency_tier}.",
                "partial_context": {
                    "tool_name": fc.name,
                    "args": fc.args or {},
                    "latency_tier": latency_tier,
                    "timeout_s": timeout_s,
                },
                "retry_hint": "retry_with_narrower_scope_or_fewer_results",
                "x-a2a-status": 504,
                "x-a2a-latency": latency_tier,
            }
        finally:
            if session_facade._scheduler:
                session_facade._scheduler.on_tool_end(fc.name)

    results = await asyncio.gather(
        *[_dispatch_with_timeout(fc) for fc in calls], return_exceptions=True
    )

    function_responses = []
    for fc, result in zip(calls, results):
        if isinstance(result, Exception):
            logger.error("Tool %s failed: %s", fc.name, result)
            result = {"error": str(result), "status": "failed"}

        function_responses.append(types.FunctionResponse(name=fc.name, response=result))

        asyncio.create_task(
            session_facade._gateway.broadcast(
                "tool_result",
                {
                    "tool_name": fc.name,
                    "result": str(result.get("result", result))
                    if isinstance(result, dict)
                    else str(result),
                    "status": "failed"
                    if isinstance(result, dict) and "error" in result
                    else "success",
                    "code": result.get("x-a2a-status")
                    if isinstance(result, dict)
                    else None,
                },
            )
        )

        if isinstance(result, dict) and "screenshot_path" in result:
            path = result["screenshot_path"]
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        image_bytes = f.read()
                    await session.send_realtime_input(
                        parts=[
                            types.Part.from_bytes(
                                data=image_bytes, mime_type="image/jpeg"
                            )
                        ]
                    )
                    os.remove(path)
                except Exception as e:
                    logger.error("Vision injection failed: %s", e)

        if session_facade._on_tool_call:
            asyncio.create_task(session_facade._on_tool_call(fc.name, fc.args, result))

        if (
            fc.name == "delegate_to_agent"
            and isinstance(result, dict)
            and result.get("status") == "handoff_initiated"
        ):
            handoff_id = result.get("handoff_id")
            session_facade._active_handoffs[handoff_id] = {
                "target": fc.args.get("target_agent_id"),
                "task": fc.args.get("task_description"),
                "timestamp": result.get("handoff_time"),
            }
            logger.info("A2A [STATE] Tracking handoff: %s", handoff_id)

    try:
        dashboard = get_tool_timeout_dashboard()
        if hasattr(session_facade._gateway, "metrics") and isinstance(
            session_facade._gateway.metrics, dict
        ):
            session_facade._gateway.metrics["tool_dispatch_dashboard"] = dashboard
    except Exception as exc:
        logger.debug("Failed to update tool timeout dashboard: %s", exc)

    try:
        await session.send_tool_response(function_responses)
        logger.info(
            "✓ Parallel Brain Cycle Complete: %d results sent", len(function_responses)
        )
    except Exception as exc:
        logger.error("Failed to send parallel tool responses: %s", exc)
