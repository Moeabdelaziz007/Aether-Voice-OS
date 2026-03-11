import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from core.infra.config import get_firebase_cert, load_config

logger = logging.getLogger(__name__)


class FirebaseConnector:
    """
    The Cloud Native Persistence Layer.

    Architected for Real-Time Frontend Sync:
    1. Sessions: Stores high-level metadata.
    2. Messages (Subcollection): Stores chat logs. Frontend listens via onSnapshot().
    3. Metrics (Subcollection): Stores affective computing data points.
    """

    def __init__(self) -> None:
        self._db: Optional[firestore.client] = None
        self._session_id: Optional[str] = None
        self.is_connected: bool = False
        self._initialized: bool = False

    async def initialize(self) -> bool:
        """
        Initializes connection to Firestore using secure Base64 credentials if
        available.
        """
        try:
            config = load_config()
            cert_dict = get_firebase_cert(config)

            # Avoid re-initializing if app already exists
            if not firebase_admin._apps:
                if cert_dict:
                    cred = credentials.Certificate(cert_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info(
                        "🔥 Firebase: Initialized with Secure Base64 Credentials"
                    )
                else:
                    # Fallback to standard Google Application Credentials (local dev)
                    firebase_admin.initialize_app()
                    logger.info("🔥 Firebase: Initialized with Default Credentials")

            self._db = firestore.client()
            self.is_connected = True
            self._initialized = True
            return True
        except Exception as e:
            logger.warning(f"🔥 Firebase: Connection Failed (Offline Mode) - {e}")
            self.is_connected = False
            return False

    async def start_session(self) -> None:
        """Creates a new session document to track this interaction."""
        if not self.is_connected or not self._db:
            return

        self._session_id = str(uuid.uuid4())
        try:
            doc_ref = self._db.collection("sessions").document(self._session_id)

            def _write():
                doc_ref.set(
                    {
                        "started_at": datetime.now(timezone.utc),
                        "status": "active",
                        "agent_version": "2.0-alpha",
                        "device": "desktop-mac",
                    }
                )

            await asyncio.to_thread(_write)
            logger.info(f"Session ID: {self._session_id}")
        except Exception as e:
            logger.error(f"Failed to create session doc: {e}")

    async def log_message(self, role: str, content: str) -> None:
        """
        Logs a message to the 'messages' subcollection.

        Frontend Architecture:
        The Next.js app listens to `sessions/{id}/messages` using `onSnapshot`.
        When this function runs, the UI updates instantly.
        """
        if not self.is_connected or not self._session_id:
            return

        try:
            msg_data = {
                "role": role,  # 'user' or 'assistant'
                "content": content,
                "timestamp": datetime.now(timezone.utc),
            }

            def _write():
                (
                    self._db.collection("sessions")
                    .document(self._session_id)
                    .collection("messages")
                    .add(msg_data)
                )

            await asyncio.to_thread(_write)
        except Exception as e:
            logger.error(f"Failed to log message: {e}")

    async def log_affective_metrics(self, features: Any) -> None:
        """Logs emotional telemetry for the dashboard visualizer."""
        if not self.is_connected or not self._session_id:
            return

        try:
            data = {
                "timestamp": datetime.now(timezone.utc),
                "valence": getattr(features, "engagement_score", 0.0),
                "arousal": getattr(features, "rms_variance", 0.0) / 500.0,
                "pitch": getattr(features, "pitch_estimate", 0.0),
                "rate": getattr(features, "speech_rate", 0.0),
                "zen_mode": getattr(features, "zen_mode", False),
            }

            def _write():
                (
                    self._db.collection("sessions")
                    .document(self._session_id)
                    .collection("metrics")
                    .add(data)
                )

            await asyncio.to_thread(_write)
        except Exception as e:
            # Debug level to avoid spamming logs
            logger.debug(f"Failed to log metrics: {e}")

    async def log_knowledge(self, topic: str, content: str, source: str) -> None:
        """Stores scraped context into the permanent cloud brain."""
        if not self.is_connected:
            return

        try:
            data = {
                "topic": topic,
                "content": content,
                "source": source,
                "session_id": self._session_id,
                "timestamp": datetime.now(timezone.utc),
            }

            def _write():
                self._db.collection("knowledge").add(data)

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: Brain updated with knowledge on {topic}")
        except Exception as e:
            logger.error(f"Failed to log knowledge: {e}")

    async def log_repair_event(
        self, filepath: str, diagnosis: str, status: str = "applied"
    ) -> None:
        """Logs an autonomous healing action for the audit trail."""
        if not self.is_connected or not self._session_id:
            return

        try:
            data = {
                "filepath": filepath,
                "diagnosis": diagnosis,
                "status": status,
                "timestamp": datetime.now(timezone.utc),
            }

            def _write():
                (
                    self._db.collection("sessions")
                    .document(self._session_id)
                    .collection("repairs")
                    .add(data)
                )

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: Repair logged for {filepath}")
        except Exception as e:
            logger.error(f"Failed to log repair: {e}")

    async def end_session(self, summary: dict) -> None:
        """Closes the session."""
        if not self.is_connected or not self._session_id:
            return

        try:
            doc_ref = self._db.collection("sessions").document(self._session_id)

            def _update():
                doc_ref.update(
                    {
                        "status": "completed",
                        "ended_at": datetime.now(timezone.utc),
                        "summary": summary,
                    }
                )

            await asyncio.to_thread(_update)
        except Exception as e:
            logger.error(f"Failed to end session: {e}")

    async def get_session_affective_summary(self, session_id: str) -> dict:
        """
        Calculates fitness metrics for the genetic optimizer.
        Aggregates valence/arousal from the 'metrics' subcollection using
        Firestore AggregationQuery to avoid N+1 fetches.
        """
        if not self.is_connected or not self._db:
            return {"status": "error", "message": "Firebase disconnected"}

        try:
            metrics_ref = (
                self._db.collection("sessions")
                .document(session_id)
                .collection("metrics")
            )

            # Use Firestore Aggregation Queries to avoid N+1 and minimize memory usage
            agg_query = (
                metrics_ref.count(alias="count")
                .avg("valence", alias="avg_valence")
                .avg("arousal", alias="avg_arousal")
            )

            # Wrap the blocking aggregation call
            agg_results = await asyncio.to_thread(agg_query.get)

            if not agg_results or not agg_results[0]:
                return {"status": "empty", "message": "No telemetry data found"}

            count = 0
            avg_valence = 0.0
            avg_arousal = 0.0

            for agg in agg_results[0]:
                if agg.alias == "count":
                    count = agg.value
                elif agg.alias == "avg_valence":
                    avg_valence = agg.value or 0.0
                elif agg.alias == "avg_arousal":
                    avg_arousal = agg.value or 0.0

            if count == 0:
                return {"status": "empty", "message": "No telemetry data found"}

            # Heuristic fitness matching GeneticOptimizer expectation
            summary = {
                "avg_engagement": (avg_valence + 1.0) / 2.0,  # Map -1..1 to 0..1
                "avg_pitch": 160.0 + (avg_arousal * 40.0),  # Simulated pitch variance
                "trend": "stable" if abs(avg_valence) < 0.2 else "improving",
                "interaction_count": count,
            }

            return {"status": "success", "summary": summary}
        except Exception as e:
            logger.error(f"Failed to fetch affective summary: {e}")
            return {"status": "error", "message": str(e)}

    async def log_event(self, event_type: str, data: dict) -> None:
        """Logs a generic event for analytics and auditing."""
        if not self.is_connected or not self._db:
            return

        try:
            data["timestamp"] = datetime.now(timezone.utc)

            def _write():
                self._db.collection("events").add({"type": event_type, "payload": data})

            await asyncio.to_thread(_write)
        except Exception as e:
            logger.error(f"Failed to log event {event_type}: {e}")

    async def get_recent_knowledge(self, limit: int = 5) -> list[dict]:
        """Retrieves the most recent knowledge entries from the cloud brain."""
        if not self.is_connected or not self._db:
            return []

        try:

            def _read():
                query = (
                    self._db.collection("knowledge")
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                )
                return [doc.to_dict() for doc in query.stream()]

            return await asyncio.to_thread(_read)
        except Exception as e:
            logger.error(f"Failed to fetch recent knowledge: {e}")
            return []

    async def sync_agent_dna(self, agent_name: str, dna: dict) -> bool:
        """
        Syncs a forged agent's DNA to the global 'agents' collection.
        This enables cross-device discovery and backup.
        """
        if not self.is_connected or not self._db:
            return False

        try:
            dna["last_synced"] = datetime.now(timezone.utc)
            dna["status"] = dna.get("status", "forged")

            def _write():
                self._db.collection("agents").document(agent_name.lower()).set(
                    dna, merge=True
                )

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: Agent DNA synced for {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to sync agent DNA for {agent_name}: {e}")
            return False

    async def log_agent_memory(
        self, agent_id: str, entry: str, context: Optional[dict] = None
    ) -> None:
        """
        Logs a memory entry for a specific agent.
        Ensures persistent 'consciousness' across sessions.
        """
        if not self.is_connected or not self._db:
            return

        try:
            data = {
                "content": entry,
                "context": context or {},
                "timestamp": datetime.now(timezone.utc),
            }

            def _write():
                (
                    self._db.collection("agents")
                    .document(agent_id.lower())
                    .collection("memory")
                    .add(data)
                )

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: Persistent memory logged for {agent_id}")
        except Exception as e:
            logger.error(f"Failed to log agent memory for {agent_id}: {e}")

    # --- AetherMemoryService Extension ---

    async def get_user_dna(self, uid: str) -> dict:
        """Retrieves the persistent User DNA for a specific identity."""
        if not self.is_connected or not self._db:
            return {}

        try:
            def _read():
                doc = self._db.collection("user_dna").document(uid).get()
                return doc.to_dict() if doc.exists else {}

            return await asyncio.to_thread(_read)
        except Exception as e:
            logger.error(f"Failed to fetch user DNA for {uid}: {e}")
            return {}

    async def update_user_dna(self, uid: str, dna_updates: dict) -> bool:
        """Updates the persistent User DNA (preferences, themes)."""
        if not self.is_connected or not self._db:
            return False

        try:
            def _write():
                self._db.collection("user_dna").document(uid).set(
                    dna_updates, merge=True
                )

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: User DNA updated for {uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user DNA for {uid}: {e}")
            return False

    async def link_agent_to_synapse(self, agent_id: str, mission_id: str, uid: str) -> None:
        """Maps an agent's memory to a shared mission synapse."""
        if not self.is_connected or not self._db:
            return

        try:
            synapse_id = f"{uid}_{mission_id}"
            def _write():
                self._db.collection("synapses").document(synapse_id).set({
                    "mission_id": mission_id,
                    "last_active": datetime.now(timezone.utc),
                    "agents": firestore.ArrayUnion([agent_id])
                }, merge=True)

            await asyncio.to_thread(_write)
            logger.info(f"🔥 Firebase: Agent {agent_id} linked to synapse {synapse_id}")
        except Exception as e:
            logger.error(f"Failed to link agent to synapse: {e}")

    async def get_mission_context(self, uid: str, mission_id: str) -> dict:
        """Retrieves shared context (synapse) for a mission."""
        if not self.is_connected or not self._db:
            return {}

        try:
            synapse_id = f"{uid}_{mission_id}"
            def _read():
                doc = self._db.collection("synapses").document(synapse_id).get()
                return doc.to_dict() if doc.exists else {}

            return await asyncio.to_thread(_read)
        except Exception as e:
            logger.error(f"Failed to fetch mission context: {e}")
            return {}
