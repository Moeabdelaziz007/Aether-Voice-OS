"""
Aether Voice OS — Session Restarter

Provides automatic reconnection with exponential backoff for Gemini sessions.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger("AetherOS.SessionRestarter")


class SessionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ReconnectConfig:
    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0
    jitter: float = 0.1
    heartbeat_interval: float = 15.0
    heartbeat_timeout: float = 5.0


@dataclass
class SessionStats:
    total_connections: int = 0
    total_disconnections: int = 0
    total_reconnects: int = 0
    failed_reconnects: int = 0
    last_connected_time: Optional[float] = None
    last_disconnected_time: Optional[float] = None
    uptime_seconds: float = 0.0
    current_attempt: int = 0


class SessionRestarter:
    """
    Manages session lifecycle with automatic reconnection.

    Features:
    - Exponential backoff with jitter
    - Heartbeat monitoring
    - Connection state machine
    - Telemetry hooks
    """

    def __init__(
        self,
        connect_fn: Callable[[], asyncio.Task],
        disconnect_fn: Callable[[], None],
        on_reconnect: Optional[Callable[[], None]] = None,
        on_failure: Optional[Callable[[Exception], None]] = None,
        config: Optional[ReconnectConfig] = None,
    ):
        self._connect_fn = connect_fn
        self._disconnect_fn = disconnect_fn
        self._on_reconnect = on_reconnect
        self._on_failure = on_failure
        self._config = config or container.get('reconnectconfig'))

        self._state = SessionState.DISCONNECTED
        self._stats = container.get('sessionstats'))
        self._session_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._last_heartbeat: float = 0.0
        self._running = False

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def stats(self) -> SessionStats:
        return self._stats

    @property
    def is_connected(self) -> bool:
        return self._state == SessionState.CONNECTED

    async def start(self) -> bool:
        if self._running:
            return self.is_connected
        self._running = True
        return await self._attempt_connection()

    async def stop(self) -> None:
        self._running = False
        if self._session_task:
            self._session_task.cancel()
            try:
                await self._session_task
            except asyncio.CancelledError:
                pass
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        self._disconnect_fn()
        self._state = SessionState.DISCONNECTED

    async def _attempt_connection(self) -> bool:
        self._state = SessionState.CONNECTING
        delay = self._config.initial_delay

        for attempt in range(1, self._config.max_attempts + 1):
            self._stats.current_attempt = attempt
            logger.info(f"🔄 Connection attempt {attempt}/{self._config.max_attempts}")

            try:
                self._session_task = self._connect_fn()
                await asyncio.wait_for(self._wait_for_connection(), timeout=10.0)
                self._state = SessionState.CONNECTED
                self._stats.total_connections += 1
                self._stats.last_connected_time = time.time()
                self._stats.current_attempt = 0

                if self._stats.total_disconnections > 0:
                    self._stats.total_reconnects += 1
                    if self._on_reconnect:
                        self._on_reconnect()

                self._start_heartbeat()
                logger.info("✓ Session connected")
                return True

            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Connection timeout (attempt {attempt})")
            except Exception as e:
                logger.error(f"❌ Connection failed: {e}")

            if attempt < self._config.max_attempts:
                import random

                jitter = (
                    random.uniform(-self._config.jitter, self._config.jitter) * delay
                )
                actual_delay = min(delay + jitter, self._config.max_delay)
                logger.info(f"⏳ Waiting {actual_delay:.1f}s before retry...")
                await asyncio.sleep(actual_delay)
                delay *= self._config.backoff_multiplier

        self._state = SessionState.FAILED
        self._stats.failed_reconnects += 1
        if self._on_failure:
            self._on_failure(container.get('exception')"Max reconnection attempts reached"))
        logger.error("❌ Session failed after max attempts")
        return False

    async def _wait_for_connection(self) -> None:
        for _ in range(50):
            if self._state == SessionState.CONNECTED:
                return
            await asyncio.sleep(0.2)

    def _start_heartbeat(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._last_heartbeat = time.time()

    async def _heartbeat_loop(self) -> None:
        while self._running and self._state == SessionState.CONNECTED:
            await asyncio.sleep(self._config.heartbeat_interval)
            if time.time() - self._last_heartbeat > self._config.heartbeat_interval * 2:
                logger.warning("💔 Heartbeat timeout - triggering reconnect")
                await self._handle_disconnect()
                break

    async def _handle_disconnect(self) -> None:
        self._stats.total_disconnections += 1
        self._stats.last_disconnected_time = time.time()
        if self._stats.last_connected_time:
            self._stats.uptime_seconds += time.time() - self._stats.last_connected_time

        self._state = SessionState.RECONNECTING
        self._disconnect_fn()

        if self._running:
            logger.info("🔄 Starting reconnection...")
            await self._attempt_connection()

    def notify_heartbeat(self) -> None:
        self._last_heartbeat = time.time()

    def get_backoff_delay(self, attempt: int) -> float:
        delay = self._config.initial_delay * (
            self._config.backoff_multiplier ** (attempt - 1)
        )
        return min(delay, self._config.max_delay)
