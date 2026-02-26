import asyncio

from core.tools.firebase_tool import FirebaseConnector


async def test_fb():
    fb = FirebaseConnector()
    print("Initializing...")
    ok = await fb.initialize()
    print(f"Connected: {ok}")
    if ok:
        print("Starting session...")
        sid = await fb.start_session()
        print(f"Session ID: {sid}")
        await fb.end_session({"status": "test_complete"})
        print("Done")


if __name__ == "__main__":
    asyncio.run(test_fb())
