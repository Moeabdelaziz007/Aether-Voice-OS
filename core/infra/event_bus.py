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
        
        # Dispatcher state (Multi-Lane)
        self._running = False
        self._tasks: List[asyncio.Task] = []

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
        elif isinstance(event, (ControlEvent, AcousticTraitEvent)):
            await self.control_queue.put(event)
        elif isinstance(event, (TelemetryEvent, VisionPulseEvent)):
            await self.telemetry_queue.put(event)
        else:
            logger.warning(f"[EventBus] Unknown event tier for {type(event)}. Routing to Telemetry.")
            await self.telemetry_queue.put(event)

    async def start(self):
        """Ignite the cardiovascular system of the OS."""
        if self._running:
            return
        
        self._running = True
        self._tasks = [
            asyncio.create_task(self._tier_worker("Audio", self.audio_queue, drop_if_expired=True)),
            asyncio.create_task(self._tier_worker("Control", self.control_queue, drop_if_expired=True)),
            asyncio.create_task(self._tier_worker("Telemetry", self.telemetry_queue, drop_if_expired=False))
        ]
        logger.info("[EventBus] 🌌 Multi-Lane Neural Event Bus initialized.")

    async def stop(self):
        """Gracefully shutdown the bus and flush queues."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks = []
        logger.info("[EventBus] Event Bus offline.")

    async def _tier_worker(self, name: str, queue: asyncio.Queue, drop_if_expired: bool):
        """Dedicated worker for a specific event lane."""
        logger.debug(f"[EventBus] {name} Lane Worker started.")
        while self._running:
            try:
                event = await queue.get()
                
                if drop_if_expired and event.is_expired():
                    logger.warning(f"[EventBus] 🔴 {name} Lane: Dropped expired event from {event.source}")
                else:
                    await self._route_event(event)

                queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[EventBus] {name} Lane Error: {e}")

    async def _route_event(self, event: SystemEvent):
        """Broadcast the event to all matched subscribers concurrently."""
        event_type = type(event)
        if event_type in self._subscribers:
            tasks = [subscriber(event) for subscriber in self._subscribers[event_type]]
            if tasks:
                # Fire and forget concurrently; errors won't crash the bus
                await asyncio.gather(*tasks, return_exceptions=True)
