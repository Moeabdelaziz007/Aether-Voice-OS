import asyncio
import logging

from core.tools.firebase_tool import FirebaseConnector

logging.basicConfig(level=logging.INFO)


class DummyFeatures:
    valence = 0.5
    arousal = 0.8
    emotion = "excited"


async def test_firebase():
    connector = FirebaseConnector()
    print("Initializing...")
    success = await connector.initialize()
    print(f"Connected: {success}")

    if success:
        print("Starting session...")
        await connector.start_session()
        print(f"Session ID: {connector._session_id}")

        print("Logging message...")
        await connector.log_message(
            role="assistant", content="Testing Firebase connectivity."
        )

        print("Logging affective metrics...")
        await connector.log_affective_metrics(DummyFeatures())

        print("Ending session...")
        await connector.end_session(
            {"test_status": "success", "notes": "Automated verification"}
        )
        print("Test complete.")
    else:
        print("Failed to initialize Firebase.")


if __name__ == "__main__":
    asyncio.run(test_firebase())
