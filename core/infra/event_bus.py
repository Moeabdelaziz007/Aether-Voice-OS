import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("AetherOS.EventBus")

# ==========================================
# 🌌 RULE 1 & 2: System Clock Protocol
# Every event inherits from SystemEvent and
# is subject to strict deadline budgets.
# ==========================================


class SystemEvent(BaseModel):
    """
    The acoustic nervous system base event.
    Time is the currency of AetherOS.
    """

    timestamp: float
    source: str
    latency_budget: int  # in milliseconds

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def is_expired(self) -> bool:
        """Check if the event missed its latency budget deadline."""
        deadline = self.timestamp + (self.latency_budget / 1000.0)
        return time.time() > deadline


# ==========================================
# Tiered Event Payloads (Pydantic Contracts)
# ==========================================


class AudioFrameEvent(SystemEvent):
    """Tier 1: High Priority Audio Data (PCM Stream)"""

    pcm_data: bytes
    sample_rate: int
    channels: int


class ControlEvent(SystemEvent):
    """Tier 2: State Changes and Control Commands (e.g. Listening -> Thinking)"""

    command: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class TelemetryEvent(SystemEvent):
    """Tier 3: Observability and Metrics (Droppable)"""

    metric_name: str
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AcousticTraitEvent(SystemEvent):
    """Tier 2: Real-time Paralinguistic Data (Affective Soul)"""

    trait_name: str  # e.g. "valence", "arousal", "pitch", "energy"
    trait_value: float
    confidence: float = 1.0


class VisionPulseEvent(SystemEvent):
    """Tier 3: Proactive Vision Pulse (Screenshot context)"""

    image_payload: Optional[bytes] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==========================================
# 🌌 RULE 3: Neural Event Bus Engine
# Agnostic to audio or agents.
# Pure multi-queue scheduling.
# ==========================================


class EventBus:
    @dataclass
    class _SubscriberState:
        callback: Callable[[SystemEvent], Awaitable[None]]
        queue: asyncio.Queue[SystemEvent]
        worker_task: Optional[asyncio.Task] = None
        processed: int = 0
        dropped: int = 0
        timed_out: int = 0
        failures: int = 0
        consecutive_failures: int = 0
        total_service_time_ms: float = 0.0
        degraded_until: float = 0.0
        degrade_count: int = 0
        evicted: bool = False

        @property
        def name(self) -> str:
            return getattr(self.callback, "__qualname__", repr(self.callback))

    def __init__(
        self,
        *,
        max_callback_workers: int = 16,
        subscriber_queue_size: int = 1000,
        subscriber_timeout_ms: int = 30,
        max_subscriber_failures: int = 5,
        max_subscriber_degrades: int = 3,
        degrade_cooldown_s: float = 0.5,
    ):
        # 3-Tier Separate Queues to prevent priority inversion/starvation
        self.audio_queue: asyncio.Queue[AudioFrameEvent] = asyncio.Queue()
        self.control_queue: asyncio.Queue[ControlEvent] = asyncio.Queue()
        self.telemetry_queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue()

        # Subscribers routing table: EventType -> List of Async Callbacks
        self._subscribers: Dict[Type[SystemEvent], List[EventBus._SubscriberState]] = {}
        self._subscriber_queue_size = subscriber_queue_size
        self._subscriber_timeout_s = max(subscriber_timeout_ms / 1000.0, 0.001)
        self._max_subscriber_failures = max_subscriber_failures
        self._max_subscriber_degrades = max_subscriber_degrades
        self._degrade_cooldown_s = degrade_cooldown_s
        self._callback_semaphore = asyncio.Semaphore(max_callback_workers)

        # Dispatcher state (Multi-Lane)
        self._running = False
        self._tasks: List[asyncio.Task] = []

    def subscribe(
        self,
        event_type: Type[SystemEvent],
        callback: Callable[[SystemEvent], Awaitable[None]],
    ):
        """Register an async callback for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        state = EventBus._SubscriberState(
            callback=callback,
            queue=asyncio.Queue(maxsize=self._subscriber_queue_size),
        )
        self._subscribers[event_type].append(state)

        if self._running:
            state.worker_task = asyncio.create_task(self._subscriber_worker(state))
        logger.debug(
            f"[EventBus] Subscribed {callback.__name__} to {event_type.__name__}"
        )

    async def publish(self, event: SystemEvent):
        """Publish an event to its respective tier queue."""
        if isinstance(event, AudioFrameEvent):
            await self.audio_queue.put(event)
        elif isinstance(event, (ControlEvent, AcousticTraitEvent)):
            await self.control_queue.put(event)
        elif isinstance(event, (TelemetryEvent, VisionPulseEvent)):
            await self.telemetry_queue.put(event)
        else:
            logger.warning(
                f"[EventBus] Unknown event tier for {type(event)}. Routing to Telemetry."
            )
            await self.telemetry_queue.put(event)

    async def start(self):
        """Ignite the cardiovascular system of the OS."""
        if self._running:
            return

        self._running = True
        self._tasks = [
            asyncio.create_task(
                self._tier_worker("Audio", self.audio_queue, drop_if_expired=True)
            ),
            asyncio.create_task(
                self._tier_worker("Control", self.control_queue, drop_if_expired=True)
            ),
            asyncio.create_task(
                self._tier_worker(
                    "Telemetry", self.telemetry_queue, drop_if_expired=False
                )
            ),
        ]

        for states in self._subscribers.values():
            for state in states:
                if state.worker_task is None or state.worker_task.done():
                    state.worker_task = asyncio.create_task(self._subscriber_worker(state))
        logger.info("[EventBus] 🌌 Multi-Lane Neural Event Bus initialized.")

    async def stop(self):
        """Gracefully shutdown the bus and flush queues."""
        self._running = False
        for task in self._tasks:
            task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks = []

        subscriber_tasks = [
            state.worker_task
            for states in self._subscribers.values()
            for state in states
            if state.worker_task is not None
        ]
        for task in subscriber_tasks:
            task.cancel()
        if subscriber_tasks:
            await asyncio.gather(*subscriber_tasks, return_exceptions=True)
        for states in self._subscribers.values():
            for state in states:
                state.worker_task = None
        logger.info("[EventBus] Event Bus offline.")

    async def _tier_worker(
        self, name: str, queue: asyncio.Queue, drop_if_expired: bool
    ):
        """Dedicated worker for a specific event lane."""
        logger.debug(f"[EventBus] {name} Lane Worker started.")
        while self._running:
            try:
                event = await queue.get()

                if drop_if_expired and event.is_expired():
                    logger.warning(
                        f"[EventBus] 🔴 {name} Lane: Dropped expired event from {event.source}"
                    )
                else:
                    await self._route_event(event)

                # Keep lane workers hot by ACK'ing as soon as the handoff is queued.
                queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[EventBus] {name} Lane Error: {e}")

    async def _route_event(self, event: SystemEvent):
        """Fan-out event by queueing work for per-subscriber workers."""
        event_type = type(event)
        if event_type in self._subscribers:
            for state in self._subscribers[event_type]:
                if state.evicted:
                    continue
                if state.degraded_until > time.monotonic():
                    state.dropped += 1
                    continue
                try:
                    state.queue.put_nowait(event)
                except asyncio.QueueFull:
                    state.dropped += 1
                    logger.warning(
                        "[EventBus] Subscriber queue full for %s; dropping callback.",
                        state.name,
                    )

    async def _subscriber_worker(self, state: _SubscriberState):
        while self._running:
            try:
                event = await state.queue.get()
                await self._execute_subscriber_callback(state, event)
                state.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("[EventBus] Subscriber worker error (%s): %s", state.name, e)

    async def _execute_subscriber_callback(
        self, state: _SubscriberState, event: SystemEvent
    ):
        now = time.time()
        deadline = event.timestamp + (event.latency_budget / 1000.0)
        budget_remaining_s = max(deadline - now, 0.0)
        callback_timeout_s = min(self._subscriber_timeout_s, budget_remaining_s)
        if callback_timeout_s <= 0:
            state.timed_out += 1
            state.dropped += 1
            self._register_failure(state, "expired_budget")
            return

        start = time.perf_counter()
        try:
            async with self._callback_semaphore:
                await asyncio.wait_for(state.callback(event), timeout=callback_timeout_s)
            elapsed_ms = (time.perf_counter() - start) * 1000
            state.processed += 1
            state.total_service_time_ms += elapsed_ms
            state.consecutive_failures = 0
        except asyncio.TimeoutError:
            state.timed_out += 1
            state.dropped += 1
            self._register_failure(state, "timeout")
            logger.warning("[EventBus] Subscriber timeout: %s", state.name)
        except Exception as exc:
            state.dropped += 1
            self._register_failure(state, "exception")
            logger.warning("[EventBus] Subscriber failed: %s (%s)", state.name, exc)

    def _register_failure(self, state: _SubscriberState, reason: str):
        state.consecutive_failures += 1
        state.failures += 1
        if state.consecutive_failures < self._max_subscriber_failures:
            return

        state.consecutive_failures = 0
        state.degrade_count += 1

        if state.degrade_count >= self._max_subscriber_degrades:
            state.evicted = True
            logger.error("[EventBus] Subscriber evicted: %s (%s)", state.name, reason)
            return

        state.degraded_until = time.monotonic() + self._degrade_cooldown_s
        logger.warning(
            "[EventBus] Subscriber degraded for %.2fs: %s (%s)",
            self._degrade_cooldown_s,
            state.name,
            reason,
        )

    def get_subscriber_telemetry(self) -> Dict[str, Dict[str, float | int | bool]]:
        """Expose per-subscriber service time + timeout/drop counters."""
        telemetry: Dict[str, Dict[str, float | int | bool]] = {}
        for states in self._subscribers.values():
            for state in states:
                avg_ms = (
                    state.total_service_time_ms / state.processed
                    if state.processed
                    else 0.0
                )
                telemetry[state.name] = {
                    "processed": state.processed,
                    "dropped": state.dropped,
                    "timed_out": state.timed_out,
                    "failures": state.failures,
                    "degrade_count": state.degrade_count,
                    "evicted": state.evicted,
                    "avg_service_time_ms": round(avg_ms, 3),
                }
        return telemetry
