import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from core.utils.config import get_firebase_cert, load_config

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

    async def initialize(self) -> bool:
        """
        Initializes connection to Firestore using secure Base64 credentials if available.
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
            doc_ref.set(
                {
                    "started_at": datetime.now(timezone.utc),
                    "status": "active",
                    "agent_version": "2.0-alpha",
                    "device": "desktop-mac",
                }
            )
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

            # Add to subcollection
            (
                self._db.collection("sessions")
                .document(self._session_id)
                .collection("messages")
                .add(msg_data)
            )

        except Exception as e:
            logger.error(f"Failed to log message: {e}")

    async def log_affective_metrics(self, features: Any) -> None:
        """Logs emotional telemetry for the dashboard visualizer."""
        if not self.is_connected or not self._session_id:
            return

        try:
            data = {
                "timestamp": datetime.now(timezone.utc),
                "valence": getattr(features, "valence", 0.0),
                "arousal": getattr(features, "arousal", 0.0),
                "emotion": getattr(features, "emotion", "neutral"),
            }

            (
                self._db.collection("sessions")
                .document(self._session_id)
                .collection("metrics")
                .add(data)
            )
        except Exception as e:
            # Debug level to avoid spamming logs
            logger.debug(f"Failed to log metrics: {e}")

    async def end_session(self, summary: dict) -> None:
        """Closes the session."""
        if not self.is_connected or not self._session_id:
            return

        try:
            doc_ref = self._db.collection("sessions").document(self._session_id)
            doc_ref.update(
                {
                    "status": "completed",
                    "ended_at": datetime.now(timezone.utc),
                    "summary": summary,
                }
            )
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
