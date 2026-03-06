import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Set

from core.ai.session import GeminiLiveSession
from core.infra.cloud.firebase.interface import FirebaseConnector

logger = logging.getLogger(__name__)

class AetherCodex:
    """
    The Aether Codex Bridge — "The Second Brain".
    
    This component monitors the cloud-native knowledge base (Firestore)
    and injects relevant context into the active Gemini session in real-time.
    
    It bridges Phase 1 (Knowledge Bridge) and Phase 2 (Context Pulse).
    """

    def __init__(
        self, 
        firebase: FirebaseConnector, 
        session: GeminiLiveSession,
        pulse_interval: float = 5.0
    ) -> None:
        self._firebase = firebase
        self._session = session
        self._pulse_interval = pulse_interval
        self._seen_knowledge: Set[str] = set()
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts the Codex monitoring loop."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._pulse_loop())
        logger.info("Codex: Knowledge Bridge activated.")

    async def stop(self) -> None:
        """Stops the Codex monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Codex: Knowledge Bridge deactivated.")

    async def _pulse_loop(self) -> None:
        """Periodic pulse to check for new knowledge."""
        while self._running:
            try:
                if self._firebase.is_connected:
                    recent = await self._firebase.get_recent_knowledge(limit=3)
                    for item in recent:
                        # Use a combination of topic and timestamp as a unique ID proxy
                        # if real document IDs aren't available for some reason.
                        k_id = f"{item.get('topic')}_{item.get('timestamp')}"
                        
                        if k_id not in self._seen_knowledge:
                            await self._inject_knowledge(item)
                            self._seen_knowledge.add(k_id)
                
            except Exception as e:
                logger.error(f"Codex: Pulse error - {e}")
            
            await asyncio.sleep(self._pulse_interval)

    async def _inject_knowledge(self, item: dict) -> None:
        """Formats and injects knowledge into the Gemini session."""
        topic = item.get("topic", "General")
        content = item.get("content", "")
        source = item.get("source", "Cloud Brain")
        
        # Format as a high-priority system injection
        injection_text = (
            f"\n[CODEX INJECTION: {topic}]\n"
            f"Source: {source}\n"
            f"Context: {content}\n"
            f"--- Please incorporate this context into your next response if relevant. ---\n"
        )
        
        logger.info(f"Codex: Injecting knowledge on '{topic}'")
        success = await self._session.send_text(injection_text)
        
        if not success:
            logger.warning(f"Codex: Failed to inject knowledge on '{topic}'")
