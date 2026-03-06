import logging
import os
from typing import Any

from core.infra.cloud.firebase import FirebaseConnector
from core.services.watchdog import SREWatchdog

logger = logging.getLogger(__name__)


class InfraManager:
    """Manages infrastructure services: Firebase and Watchdog."""

    def __init__(self, gateway: Any):
        self._firebase = FirebaseConnector
        self._watchdog = SREWatchdog(node_id=f"aether-node-{os.getpid()}",
            bus=gateway._bus,
            gateway=gateway,
        )

    async def initialize(self):
        firebase_ok = await self._firebase.initialize()
        if firebase_ok:
            await self._firebase.start_session()
            logger.info(
                "  Firebase: ✦ Connected — session %s", self._firebase._session_id
            )
        else:
            logger.warning("  Firebase: ✗ Offline — tasks will not persist")
        return firebase_ok

    def start_watchdog(self):
        self._watchdog.start()

    def stop(self):
        self._watchdog.stop()

    async def end_session(self, router: Any):
        if self._firebase.is_connected:
            await self._firebase.end_session(
                {
                    "tools_used": router.names,
                    "tool_count": router.count,
                }
            )
