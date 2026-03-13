import asyncio
import logging
import time
from enum import Enum

from core.infra.event_bus import EventBus

logger = logging.getLogger("AetherOS.StateManager")

# ==========================================
# 🌌 AetherOS Defined States
# ==========================================


class SystemState(Enum):
    BOOTING = "booting"
    IDLE = "idle"  # VAD engaged, waiting for wake logic
    LISTENING = "listening"  # User is talking, streaming to Gemini
    THINKING = "thinking"  # Audio stream closed, LLM processing
    SPEAKING = "speaking"  # TTS outputting audio, mic suppressed (EchoGuard active)
    PAUSED = "paused"  # System suspended via Admin
    ERROR = "error"  # Fatal breakdown, watchdog restart required
    NIGHT_TERRORS = (
        "night_terrors"  # The system is dreaming (Internal Memory Consolidation)
    )


# ==========================================
# Single Source of Truth (SSoT) Transition Matrix
# ==========================================
# Maps Current State -> Allowed Next States

ALLOWED_TRANSITIONS = {
    SystemState.BOOTING: [SystemState.IDLE, SystemState.ERROR],
    SystemState.IDLE: [
        SystemState.LISTENING,
        SystemState.PAUSED,
        SystemState.ERROR,
        SystemState.NIGHT_TERRORS,
    ],
    SystemState.LISTENING: [SystemState.THINKING, SystemState.IDLE, SystemState.ERROR],
    SystemState.THINKING: [SystemState.SPEAKING, SystemState.IDLE, SystemState.ERROR],
    SystemState.SPEAKING: [
        SystemState.IDLE,
        SystemState.ERROR,
    ],  # Requires a stop to listen again
    SystemState.PAUSED: [SystemState.IDLE, SystemState.ERROR],
    SystemState.NIGHT_TERRORS: [SystemState.IDLE],
    SystemState.ERROR: [SystemState.BOOTING],  # Watchdog recovery
}

# ==========================================
# 🌌 Engine State Manager
# Event-driven architecture preventing race conditions
# between Audio (Eyes/Ears) and LLM (Brain).
# ==========================================


class EngineStateManager:
    """
    The Single Source of Truth for AetherOS.
    No component is allowed to set the state directly. They must use `request_transition`.
    """

    def __init__(self, event_bus: EventBus):
        self._bus = event_bus
        self._current_state: SystemState = SystemState.BOOTING
        self._lock = asyncio.Lock()

    @property
    def current_state(self) -> SystemState:
        return self._current_state

    async def request_transition(
        self, new_state: SystemState, source: str, reason: str = ""
    ) -> bool:
        """
        Request a state transition. Validates against the ALLOWED_TRANSITIONS matrix.
        If valid, updates internal state and broadcasts a ControlEvent on Tier 2.
        """
        async with self._lock:
            # 1. Validation
            allowed_next = ALLOWED_TRANSITIONS.get(self._current_state, [])
            if new_state not in allowed_next:
                logger.warning(
                    f"[StateManager] 🛑 Invalid Transition requested by {source}: "
                    f"{self._current_state.value} -> {new_state.value}. Allowed: {[s.value for s in allowed_next]}"
                )
                return False

            # 2. State Mutation
            old_state = self._current_state
            self._current_state = new_state
            logger.info(
                f"[StateManager] 🔄 Transition: {old_state.value} -> {new_state.value} ({reason})"
            )

            # 3. Broadcast Event-Driven Knowledge (Control Tier 2)
            # This is how the HUD and hardware know to react
            from core.infra.event_bus import ControlEvent
            event = ControlEvent(
                timestamp=time.time(),
                source="StateManager",
                latency_budget=100,  # 100ms absolute deadline for control logic
                command="STATE_CHANGED",
                payload={
                    "old_state": old_state.value,
                    "new_state": new_state.value,
                    "reason": reason,
                    "trigger_source": source,
                },
            )
            await self._bus.publish(event)
            return True

    def is_state(self, state: SystemState) -> bool:
        """Synchronous check for fast logic gates."""
        return self._current_state == state
