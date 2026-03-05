import asyncio
import time
import logging
from typing import Any, Dict, Optional, Callable, Awaitable, Type, List
from pydantic import BaseModel, ConfigDict

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
    payload: Dict[str, Any] = {}

class TelemetryEvent(SystemEvent):
    """Tier 3: Observability and Metrics (Droppable)"""
    metric_name: str
    value: float
    metadata: Dict[str, Any] = {}

class AcousticTraitEvent(SystemEvent):
    """Tier 2: Real-time Paralinguistic Data (Affective Soul)"""
    trait_name: str  # e.g. "valence", "arousal", "pitch", "energy"
    trait_value: float
    confidence: float = 1.0

# ==========================================
# 🌌 RULE 3: Neural Event Bus Engine
# Agnostic to audio or agents. 
# Pure multi-queue scheduling.
# ==========================================

class EventBus:
    def __init__(self):
        # 3-Tier Separate Queues to prevent priority inversion/starvation
        self.audio_queue: asyncio.Queue[AudioFrameEvent] = asyncio.Queue()
        self.control_queue: asyncio.Queue[ControlEvent] = asyncio.Queue()
        self.telemetry_queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue()

        # Subscribers routing table: EventType -> List of Async Callbacks
        self._subscribers: Dict[Type[SystemEvent], List[Callable[[SystemEvent], Awaitable[None]]]] = {}
        
        # Dispatcher state
        self._running = False
        self._dispatcher_task: Optional[asyncio.Task] = None

    def subscribe(self, event_type: Type[SystemEvent], callback: Callable[[SystemEvent], Awaitable[None]]):
        """Register an async callback for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"[EventBus] Subscribed {callback.__name__} to {event_type.__name__}")

    async def publish(self, event: SystemEvent):
        """Publish an event to its respective tier queue."""
        if isinstance(event, AudioFrameEvent):
            await self.audio_queue.put(event)
        elif isinstance(event, ControlEvent):
            await self.control_queue.put(event)
        elif isinstance(event, AcousticTraitEvent):
            await self.control_queue.put(event)  # Route to Tier 2 (Control)
        elif isinstance(event, TelemetryEvent):
            await self.telemetry_queue.put(event)
        else:
            logger.warning(f"[EventBus] Unknown event tier for {type(event)}. Routing to Telemetry.")
            await self.telemetry_queue.put(event)

    async def start(self):
        """Ignite the cardiovascular system of the OS."""
        if self._running:
            return
        
        self._running = True
        self._dispatcher_task = asyncio.create_task(self._dispatch_loop())
        logger.info("[EventBus] 🌌 Neural Event Bus initialized.")

    async def stop(self):
        """Gracefully shutdown the bus and flush queues."""
        self._running = False
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass
        logger.info("[EventBus] Event Bus offline.")

    async def _dispatch_loop(self):
        """
        The Core Scheduler Loop.
        Implements proportional fair scheduling to prevent starvation,
        while strictly dropping expired events based on latency_budget.
        """
        while self._running:
            processed = False

            # 1. Process up to 10 Audio Frames (Tier 1)
            for _ in range(10):
                if not self.audio_queue.empty():
                    event = self.audio_queue.get_nowait()
                    if not event.is_expired():
                        await self._route_event(event)
                    else:
                        logger.warning(f"[EventBus] 🔴 Dropped expired AudioFrame from {event.source}")
                    self.audio_queue.task_done()
                    processed = True
                else:
                    break

            # 2. Process up to 5 Control Events (Tier 2)
            for _ in range(5):
                if not self.control_queue.empty():
                    event = self.control_queue.get_nowait()
                    if not event.is_expired():
                        await self._route_event(event)
                    else:
                        logger.warning(f"[EventBus] 🟡 Dropped expired ControlEvent: {event.command}")
                    self.control_queue.task_done()
                    processed = True
                else:
                    break
            
            # 3. Process up to 20 Telemetry Events (Tier 3)
            for _ in range(20):
                if not self.telemetry_queue.empty():
                    event = self.telemetry_queue.get_nowait()
                    if not event.is_expired():
                        await self._route_event(event)
                    # Note: Expired telemetry is silently dropped to reduce log noise
                    self.telemetry_queue.task_done()
                    processed = True
                else:
                    break

            # Yield control to the ASGI/uvloop event loop
            if not processed:
                await asyncio.sleep(0.001) # Rest if idle
            else:
                await asyncio.sleep(0)     # Breathe between bursts

    async def _route_event(self, event: SystemEvent):
        """Broadcast the event to all matched subscribers concurrently."""
        event_type = type(event)
        if event_type in self._subscribers:
            tasks = [subscriber(event) for subscriber in self._subscribers[event_type]]
            if tasks:
                # Fire and forget concurrently; errors won't crash the bus
                await asyncio.gather(*tasks, return_exceptions=True)
