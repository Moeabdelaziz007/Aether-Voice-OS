import logging
from datetime import datetime
from typing import List

try:
    from firebase_admin import firestore
except ImportError:
    firestore = None

from core.cloud.firebase.schemas import SessionMetadata

logger = logging.getLogger(__name__)

# Simple in-memory cache for recent queries to reduce Firestore reads
_recent_sessions_cache = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


class Queries:
    def __init__(self):
        self.db = firestore.client() if firestore else None

    async def get_recent_sessions(
        self, user_id: str, limit: int = 10
    ) -> List[SessionMetadata]:
        """
        Retrieves the most recent sessions for a user.
        Utilizes a compound index on {"user_id": ASC, "start_time": DESC}
        Results are cached in memory for 5 minutes to optimize reads.
        """
        if not self.db:
            logger.warning(
                "Firestore client not initialized. Cannot fetch recent sessions."
            )
            return []

        now = datetime.utcnow().timestamp()
        cache_key = f"{user_id}_{limit}"

        if cache_key in _recent_sessions_cache:
            cache_data, cache_time = _recent_sessions_cache[cache_key]
            if now - cache_time < _CACHE_TTL_SECONDS:
                logger.debug("Cache hit for get_recent_sessions")
                return cache_data

        logger.debug("Fetching from Firestore for get_recent_sessions")
        try:
            sessions_ref = self.db.collection("sessions")
            # This query requires a compound index: user_id (ASC) + start_time (DESC)
            query = (
                sessions_ref.where("user_id", "==", user_id)
                .order_by("start_time", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            # Note: The firestore python SDK async support might need aio module, we use standard sync to simulate here or if using firebase-admin async
            # Since standard firebase-admin is synchronous, we wrap or mock.
            docs = query.stream()

            results = []
            for doc in docs:
                data = doc.to_dict()
                # Parse to Pydantic
                results.append(SessionMetadata(**data))

            _recent_sessions_cache[cache_key] = (results, now)
            return results
        except Exception as e:
            logger.error("Failed to fetch recent sessions: %s", e)
            return []
