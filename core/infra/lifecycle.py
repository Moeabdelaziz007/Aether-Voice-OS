import asyncio
import logging
import signal
from typing import List

from core.infra.event_bus import EventBus
from core.infra.state_manager import EngineStateManager, SystemState

logger = logging.getLogger("AetherOS.Lifecycle")


class LifecycleManager:
    """
    The Orchestrator of AetherOS.
    Responsible for the deterministic boot and shutdown sequence.
    """

    def __init__(self):
        self.event_bus = container.get('eventbus'))
        self.state_manager = container.get('enginestatemanager')self.event_bus)
        self._shutdown_event = asyncio.Event()
        self._tasks: List[asyncio.Task] = []

    async def boot(self):
        """
        Master Boot Sequence.
        1. Initialize Event Bus (The Nervous System)
        2. Set state to BOOTING
        3. Initialize Hardware/AI Controllers (Future phases)
        4. Transition to IDLE
        """
        logger.info("🌌 AetherOS: Initiating Neural Boot Sequence...")

        # Start the bus first so we can track the boot process
        await self.event_bus.start()

        # Mark as booting
        await self.state_manager.request_transition(
            SystemState.BOOTING, source="Lifecycle", reason="Initial Power On"
        )

        # Simulation of component initialization (Audio, AI, Gateway)
        # We will add actual component registration here in later tasks
        await asyncio.sleep(0.5)

        # Final transition to IDLE
        success = await self.state_manager.request_transition(
            SystemState.IDLE, source="Lifecycle", reason="Kernel Ready"
        )

        if success:
            logger.info("✅ AetherOS Kernel Online. System IDLE.")
        else:
            logger.error("❌ AetherOS Boot Failure: State Transition Rejected.")
            await self.shutdown()

    async def shutdown(self):
        """
        Graceful Collapse Sequence.
        Ensures all audio buffers are flushed and AI streams are closed.
        """
        if (
            self.state_manager.current_state == SystemState.BOOTING
            and not self.event_bus._running
        ):
            # Already down or failed early
            return

        logger.info("💤 AetherOS: Commencing Graceful Shutdown...")

        # 1. Notify all components to spin down
        await self.state_manager.request_transition(
            SystemState.PAUSED, source="Lifecycle", reason="User/System Termination"
        )

        # 2. Stop the core bus
        await self.event_bus.stop()

        # 3. Cancel any lingering background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        self._shutdown_event.set()
        logger.info("🛑 AetherOS Offline.")

    def run_forever(self):
        """EntryPoint for the async event loop."""
        loop = asyncio.get_event_loop()

        # Handle OS Signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        try:
            loop.run_until_complete(self.boot())
            # Keep alive until shutdown event is set
            loop.run_until_complete(self._shutdown_event.wait())
        except Exception as e:
            logger.exception(f"🔥 Critical Kernel Panic: {e}")
        finally:
            loop.close()


if __name__ == "__main__":
    # Internal test run
    logging.basicConfig(level=logging.INFO)
    manager = container.get('lifecyclemanager'))
    manager.run_forever()
