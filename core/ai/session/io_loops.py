from __future__ import annotations

import asyncio
import logging

from google.genai import types

from core.infra.telemetry import record_usage

logger = logging.getLogger(__name__)


async def send_loop(session_facade, session) -> None:
    logger.debug("Send loop started")
    frame_count = 0
    while session_facade._running:
        try:
            msg = await asyncio.wait_for(session_facade._in_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break

        try:
            await session.send_realtime_input(audio=msg)
            frame_count += 1
            if frame_count % 500 == 0:
                logger.debug(
                    "Send loop: %d frames sent, in_queue=%d",
                    frame_count,
                    session_facade._in_queue.qsize(),
                )
        except Exception as exc:
            logger.error("Send error: %s", exc)
            if "closed" in str(exc).lower():
                break


async def receive_loop(session_facade, session) -> None:
    logger.debug("Receive loop started")

    async def handle_server_content(sc):
        if sc.model_turn:
            for part in sc.model_turn.parts:
                if part.text:
                    try:
                        asyncio.create_task(
                            session_facade._gateway.broadcast(
                                "transcript", {"text": part.text}
                            )
                        )
                    except Exception as e:
                        logger.debug("Failed to broadcast transcript: %s", e)

                if part.inline_data and isinstance(part.inline_data.data, bytes):
                    # Elite Audio Queue Policy
                    if session_facade._out_queue.full():
                        try:
                            session_facade._out_queue.get_nowait()
                            session_facade._output_queue_drops += 1
                            if session_facade._gateway:
                                asyncio.create_task(
                                    session_facade._gateway.broadcast(
                                        "system_telemetry",
                                        {"type": "pressure_marker", "severity": "critical"},
                                    )
                                )
                        except asyncio.QueueEmpty:
                            pass

                    session_facade._out_queue.put_nowait(part.inline_data.data)
                    if session_facade._gateway:
                        asyncio.create_task(
                            session_facade._gateway.broadcast(
                                "engine_state", {"state": "SPEAKING"}
                            )
                        )
        
        if sc.interrupted:
            logger.info("⚡ Barge-in detected — draining output")
            drain_output(session_facade)
            if session_facade._on_interrupt:
                session_facade._on_interrupt()

    while session_facade._running:
        try:
            turn = session.receive()
            async for response in turn:
                handle_usage(session_facade, response)

                # O(1) Response Dispatch
                handlers = {
                    "tool_call": lambda r: session_facade._handle_tool_call(session, r.tool_call),
                    "server_content": lambda r: handle_server_content(r.server_content),
                }

                for attr, handler in handlers.items():
                    if getattr(response, attr, None):
                        await handler(response)

        except asyncio.CancelledError:
            break
        except Exception as exc:
            if "closed" in str(exc).lower():
                logger.info("Receive stream closed")
                break
            logger.error("Receive error: %s", exc, exc_info=True)
            await asyncio.sleep(0.5)


def handle_usage(session_facade, response: types.LiveConnectResponse) -> None:
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        try:
            usage = response.usage_metadata
            record_usage(
                input_tokens=usage.prompt_token_count or 0,
                output_tokens=usage.candidates_token_count or 0,
                model_name=session_facade._config.model.value,
            )
        except Exception as exc:
            logger.debug("Failed to record usage metadata: %s", exc)


def drain_output(session_facade) -> None:
    count = 0
    while not session_facade._out_queue.empty():
        try:
            session_facade._out_queue.get_nowait()
            count += 1
        except asyncio.QueueEmpty:
            break
    if count:
        logger.debug("Drained %d audio chunks from output queue", count)
