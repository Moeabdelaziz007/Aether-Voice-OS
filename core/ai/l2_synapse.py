"""
Aether Voice OS — L2 Synapse Daemon.

This performs "Autonomous Self-Healing and Memory Consolidation".
It routinely reads recent conversations/events from Firebase,
creates a summarized memory package, and writes it to a local `.ath` file.
This gives the agent a "long-term memory" of user behavior decoupled
from instantaneous session context.

Usage:
    python -m core.ai.l2_synapse
"""

import asyncio
import json
import logging
import os
from datetime import datetime

from core.tools.firebase_tool import FirebaseConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("L2_Synapse")

SYNAPSE_DIR = os.path.expanduser("~/.aetheros/synapse")


async def consolidate_memory():
    """Reads recent session data and writes a consolidated memory package."""
    logger.info("Initializing L2 Synapse Memory Consolidation...")

    # Connect to Firebase
    connector = FirebaseConnector()
    connected = await connector.initialize()

    if not connected or not connector._db:
        logger.error("Firebase not connected. Cannot consolidate memory.")
        return

    db = connector._db

    try:
        # Fetch the 10 most recent sessions
        sessions_ref = (
            db.collection("sessions")
            .order_by("started_at", direction="DESCENDING")
            .limit(10)
        )

        sessions_stream = sessions_ref.stream()

        # Simple local consolidation loop
        # (In a production environment, this would feed into a summarization LLM chain)
        consolidated_data = {
            "timestamp": datetime.now().isoformat(),
            "sessions_analyzed": 0,
            "key_events": [],
        }

        async for doc in sessions_stream:
            data = doc.to_dict()
            consolidated_data["sessions_analyzed"] += 1

            # Extract basic metrics or context to save
            end_time = data.get("ended_at")
            if end_time:
                consolidated_data["key_events"].append(
                    {
                        "session_id": doc.id,
                        "date": data.get("started_at"),
                        "status": "completed",
                    }
                )

        # Ensure directory exists
        os.makedirs(SYNAPSE_DIR, exist_ok=True)

        # Write to the .ath memory package
        package_path = os.path.join(SYNAPSE_DIR, "heartbeat.ath")
        with open(package_path, "w") as f:
            json.dump(consolidated_data, f, indent=4)

        logger.info(
            "✅ L2 Synapse: Memory successfully consolidated at %s", package_path
        )

    except Exception as e:
        logger.error("L2 Synapse encountered an error during consolidation: %s", e)


def main():
    asyncio.run(consolidate_memory())


if __name__ == "__main__":
    main()
