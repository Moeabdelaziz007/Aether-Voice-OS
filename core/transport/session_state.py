"""
Aether Voice OS — Session State Manager.

Manages the lifecycle state of the Gemini Live session with atomic transitions
and validation. Ensures Single Source of Truth for session state across
the Gateway, Engine, and connected clients.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from core.ai.session import GeminiLiveSession

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """
    Lifecycle states for the Gemini Live session.

    State Machine:
        INITIALIZING → CONNECTED → HANDING_OFF → RESTARTING → INITIALIZING
                            ↓
                         ERROR → RECOVERING → INITIALIZING
    """

    INITIALIZING = auto()  # Session being created
    CONNECTED = auto()  # Active bidirectional audio flow
    HANDING_OFF = auto()  # Context transfer between souls
    RESTARTING = auto()  # Session restart for soul switch
    ERROR = auto()  # Session failure
    RECOVERING = auto()  # Attempting reconnection
    SHUTDOWN = auto()  # Graceful termination


@dataclass
class SessionMetadata:
    """Immutable session metadata for tracking and persistence."""

    session_id: str
    soul_name: str
    started_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    handoff_count: int = 0
    error_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for WebSocket broadcast."""
        return {
            "session_id": self.session_id,
            "soul_name": self.soul_name,
            "started_at": self.started_at.isoformat(),
            "message_count": self.message_count,
            "last_activity": self.last_activity.isoformat(),
            "handoff_count": self.handoff_count,
            "error_count": self.error_count,
        }


class SessionStateManager:
    """
    Centralized state manager for Gemini Live session.

    Ensures atomic state transitions with validation and broadcasts
    state changes to all connected clients.
    """

    # Valid state transitions (from_state → [allowed_to_states])
    _VALID_TRANSITIONS: dict[SessionState, list[SessionState]] = {
        SessionState.INITIALIZING: [
            SessionState.CONNECTED,
            SessionState.ERROR,
            SessionState.SHUTDOWN,
        ],
        SessionState.CONNECTED: [
            SessionState.HANDING_OFF,
            SessionState.ERROR,
            SessionState.SHUTDOWN,
        ],
        SessionState.HANDING_OFF: [SessionState.RESTARTING, SessionState.ERROR],
        SessionState.RESTARTING: [SessionState.INITIALIZING, SessionState.ERROR],
        SessionState.ERROR: [SessionState.RECOVERING, SessionState.SHUTDOWN],
        SessionState.RECOVERING: [
            SessionState.INITIALIZING,
            SessionState.ERROR,
            SessionState.SHUTDOWN,
        ],
        SessionState.SHUTDOWN: [],  # Terminal state
    }

    def __init__(self, broadcast_callback: Optional[callable] = None) -> None:
        self._state = SessionState.INITIALIZING
        self._metadata: Optional[SessionMetadata] = None
        self._session: Optional["GeminiLiveSession"] = None
        self._lock = asyncio.Lock()
        self._broadcast = broadcast_callback
        self._state_change_event = asyncio.Event()
        self._health_check_task: Optional[asyncio.Task] = None
        self._last_health_check: datetime = datetime.now()
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 3

    @property
    def state(self) -> SessionState:
        """Current session state (thread-safe read)."""
        return self._state

    @property
    def metadata(self) -> Optional[SessionMetadata]:
        """Current session metadata."""
        return self._metadata

    @property
    def session(self) -> Optional["GeminiLiveSession"]:
        """Current Gemini Live session instance."""
        return self._session

    @property
    def is_active(self) -> bool:
        """True if session is in a functional state."""
        return self._state in (SessionState.CONNECTED, SessionState.HANDING_OFF)

    @property
    def is_transitioning(self) -> bool:
        """True if session is in a transitional state."""
        return self._state in (
            SessionState.HANDING_OFF,
            SessionState.RESTARTING,
            SessionState.RECOVERING,
        )

    async def transition_to(
        self,
        new_state: SessionState,
        reason: str = "",
        metadata: Optional[SessionMetadata] = None,
    ) -> bool:
        """
        Atomically transition to a new state with validation.

        Args:
            new_state: Target state
            reason: Human-readable reason for transition
            metadata: Optional metadata update

        Returns:
            True if transition succeeded, False otherwise
        """
        async with self._lock:
            if not self._is_valid_transition(self._state, new_state):
                logger.error(
                    "Invalid state transition: %s → %s (reason: %s)",
                    self._state.name,
                    new_state.name,
                    reason,
                )
                return False

            old_state = self._state
            self._state = new_state

            if metadata:
                self._metadata = metadata

            # Update metadata timestamp on any transition
            if self._metadata:
                self._metadata.last_activity = datetime.now()

            # Track errors
            if new_state == SessionState.ERROR:
                self._consecutive_errors += 1
                if self._metadata:
                    self._metadata.error_count += 1
            elif new_state == SessionState.CONNECTED:
                self._consecutive_errors = 0

            logger.info(
                "Session state: %s → %s (reason: %s)",
                old_state.name,
                new_state.name,
                reason,
            )

            # Broadcast state change
            await self._broadcast_state_change(old_state, new_state, reason)

            # Set event for waiters
            self._state_change_event.set()
            self._state_change_event.clear()

            return True

    def _is_valid_transition(
        self, from_state: SessionState, to_state: SessionState
    ) -> bool:
        """Check if state transition is valid."""
        allowed = self._VALID_TRANSITIONS.get(from_state, [])
        return to_state in allowed

    async def _broadcast_state_change(
        self, old_state: SessionState, new_state: SessionState, reason: str
    ) -> None:
        """Broadcast state change to all connected clients."""
        if not self._broadcast:
            return

        payload = {
            "type": "session_state_change",
            "old_state": old_state.name,
            "new_state": new_state.name,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "metadata": self._metadata.to_dict() if self._metadata else None,
        }

        try:
            await self._broadcast("session_state", payload)
        except Exception as e:
            logger.error("Failed to broadcast state change: %s", e)

    async def wait_for_state(
        self, target_states: list[SessionState], timeout: Optional[float] = None
    ) -> bool:
        """
        Wait for session to reach one of the target states.

        Args:
            target_states: List of states to wait for
            timeout: Maximum wait time in seconds

        Returns:
            True if target state reached, False on timeout
        """
        if self._state in target_states:
            return True

        try:
            async with asyncio.timeout(timeout) if timeout else asyncio.nullcontext():
                while self._state not in target_states:
                    await self._state_change_event.wait()
                    if self._state in target_states:
                        return True
            return False
        except asyncio.TimeoutError:
            return False

    def set_session(self, session: Optional["GeminiLiveSession"]) -> None:
        """Set the current Gemini Live session instance."""
        self._session = session

    def increment_message_count(self) -> None:
        """Increment the message counter in metadata."""
        if self._metadata:
            self._metadata.message_count += 1
            self._metadata.last_activity = datetime.now()

    def increment_handoff_count(self) -> None:
        """Increment the handoff counter in metadata."""
        if self._metadata:
            self._metadata.handoff_count += 1

    async def start_health_monitoring(self, check_interval: float = 5.0) -> None:
        """Start background health monitoring task."""
        if self._health_check_task and not self._health_check_task.done():
            return

        self._health_check_task = asyncio.create_task(
            self._health_check_loop(check_interval)
        )

    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

    async def _health_check_loop(self, interval: float) -> None:
        """Background task for periodic health checks."""
        while True:
            try:
                await asyncio.sleep(interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check error: %s", e)

    async def _perform_health_check(self) -> None:
        """Check session health and trigger recovery if needed."""
        if self._state == SessionState.SHUTDOWN:
            return

        # Check for stuck states
        time_in_state = (datetime.now() - self._last_health_check).total_seconds()

        if self._state == SessionState.ERROR:
            if self._consecutive_errors >= self._max_consecutive_errors:
                logger.error("Max consecutive errors reached, shutting down")
                await self.transition_to(SessionState.SHUTDOWN, "Max errors reached")
            else:
                logger.info("Attempting recovery from error state")
                await self.transition_to(
                    SessionState.RECOVERING, "Auto-recovery triggered"
                )

        self._last_health_check = datetime.now()

    def should_trigger_reconnection(self) -> bool:
        """Determine if session needs reconnection based on error count."""
        return (
            self._consecutive_errors > 0
            and self._consecutive_errors < self._max_consecutive_errors
        )

    async def create_snapshot(self) -> dict[str, Any]:
        """Create a snapshot of current session for crash recovery."""
        return {
            "state": self._state.name,
            "metadata": self._metadata.to_dict() if self._metadata else None,
            "consecutive_errors": self._consecutive_errors,
            "timestamp": datetime.now().isoformat(),
        }

    async def restore_from_snapshot(self, snapshot: dict[str, Any]) -> bool:
        """Restore session state from snapshot."""
        try:
            # Only restore metadata, not state (start fresh)
            if snapshot.get("metadata"):
                meta = snapshot["metadata"]
                self._metadata = SessionMetadata(
                    session_id=meta.get("session_id", "restored"),
                    soul_name=meta.get("soul_name", "unknown"),
                    started_at=datetime.fromisoformat(meta.get("started_at")),
                    message_count=meta.get("message_count", 0),
                    handoff_count=meta.get("handoff_count", 0),
                    error_count=meta.get("error_count", 0),
                )
            logger.info("Session restored from snapshot")
            return True
        except Exception as e:
            logger.error("Failed to restore session from snapshot: %s", e)
            return False
