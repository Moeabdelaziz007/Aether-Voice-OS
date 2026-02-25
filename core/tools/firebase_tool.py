"""
Aether Voice OS — Firebase Integration.

Connects Aether to Firebase for:
  - Agent state persistence (Firestore)
  - Session logging and analytics
  - Remote configuration
  - User authentication (future)

Uses the Firebase Admin SDK for server-side operations.
All Firebase config is loaded from environment variables.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Firebase SDK config (from firebase_get_sdk_config)
FIREBASE_CONFIG = {
    "projectId": "asiom-id",
    "appId": "1:854639150351:web:9250068a53a83efb542a7a",
    "storageBucket": "asiom-id.firebasestorage.app",
    "apiKey": os.getenv("FIREBASE_API_KEY", ""),
    "authDomain": "asiom-id.firebaseapp.com",
    "messagingSenderId": "854639150351",
}


class FirebaseConnector:
    """
    Firebase integration layer for Aether Voice OS.

    Manages Firestore connections for agent state persistence,
    session logging, and remote configuration.
    """

    def __init__(self, project_id: str = "asiom-id") -> None:
        self._project_id = project_id
        self._db = None
        self._initialized = False
        self._session_id: Optional[str] = None

    async def initialize(self) -> bool:
        """
        Initialize Firebase Admin SDK.

        Returns True if successfully connected, False otherwise.
        """
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Check if already initialized
            try:
                app = firebase_admin.get_app()
                logger.info("Firebase already initialized: %s", app.project_id)
            except ValueError:
                # Initialize with default credentials or service account
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with service account")
                else:
                    # Try application default credentials
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")

            self._db = firestore.AsyncClient(project=self._project_id)
            self._initialized = True
            logger.info("Firestore connected: project=%s", self._project_id)
            return True

        except ImportError:
            logger.warning(
                "firebase-admin not installed. "
                "Run: pip install firebase-admin"
            )
            return False
        except Exception as exc:
            logger.error("Firebase initialization failed: %s", exc)
            return False

    @property
    def is_connected(self) -> bool:
        """Check if Firebase is initialized and ready."""
        return self._initialized and self._db is not None

    # ── Session Management ──────────────────────────────────

    async def start_session(self, agent_id: str = "aether-voice") -> str:
        """
        Create a new session document in Firestore.

        Returns the session ID.
        """
        if not self.is_connected:
            logger.warning("Firebase not connected — session not tracked")
            return "local-session"

        from datetime import datetime, timezone
        import uuid

        self._session_id = str(uuid.uuid4())[:8]
        session_data = {
            "agent_id": agent_id,
            "session_id": self._session_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "model": os.getenv("AETHER_AI_MODEL", "gemini-2.5-flash-native-audio"),
            "platform": "standalone-cli",
        }

        try:
            doc_ref = self._db.collection("sessions").document(self._session_id)
            await doc_ref.set(session_data)
            logger.info("Session started: %s", self._session_id)
        except Exception as exc:
            logger.error("Failed to write session: %s", exc)

        return self._session_id

    async def end_session(self, summary: Optional[dict] = None) -> None:
        """Update session document as ended."""
        if not self.is_connected or not self._session_id:
            return

        update_data = {
            "status": "ended",
            "ended_at": datetime.now(timezone.utc).isoformat(),
        }
        if summary:
            update_data["summary"] = summary

        try:
            doc_ref = self._db.collection("sessions").document(self._session_id)
            await doc_ref.update(update_data)
            logger.info("Session ended: %s", self._session_id)
        except Exception as exc:
            logger.error("Failed to update session: %s", exc)

    # ── State Persistence ───────────────────────────────────

    async def save_agent_state(self, state: dict[str, Any]) -> None:
        """Persist agent state to Firestore for recovery."""
        if not self.is_connected:
            return

        state["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            doc_ref = self._db.collection("agent_state").document("current")
            await doc_ref.set(state, merge=True)
        except Exception as exc:
            logger.error("Failed to save agent state: %s", exc)

    async def load_agent_state(self) -> Optional[dict[str, Any]]:
        """Load agent state from Firestore."""
        if not self.is_connected:
            return None

        try:
            doc_ref = self._db.collection("agent_state").document("current")
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as exc:
            logger.error("Failed to load agent state: %s", exc)
        return None

    # ── Event Logging ───────────────────────────────────────

    async def log_event(
        self,
        event_type: str,
        data: Optional[dict] = None,
    ) -> None:
        """Log an agent event to Firestore for analytics."""
        if not self.is_connected:
            return

        event = {
            "type": event_type,
            "session_id": self._session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        }

        try:
            self._db.collection("events").add(event)
        except Exception as exc:
            logger.debug("Event logging failed: %s", exc)

    # ── Tool Declaration ────────────────────────────────────

    def to_adk_declaration(self) -> dict:
        """ADK-compatible tool declaration for Firebase operations."""
        return {
            "name": "aether_firebase",
            "description": (
                "Manages Firebase integration: session tracking, "
                "state persistence, and event logging."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start_session", "end_session", "save_state", "status"],
                        "description": "Firebase action to perform",
                    }
                },
                "required": ["action"],
            },
        }
