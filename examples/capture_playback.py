"""
Demo for Audio Capture & Playback Pipeline

This script demonstrates initializing the AudioCapture and AudioPlayback classes,
hooking them up to asyncio queues, and running them for a brief duration.
"""

import asyncio

from core.audio.capture import AudioCapture
from core.audio.playback import AudioPlayback
from core.infra.config import AudioConfig


async def main():
    print("Setting up Audio Pipeline...")
    config = AudioConfig()

    # Queues for data flow
    capture_queue = asyncio.Queue()
    playback_queue = asyncio.Queue()

    # Initialize components
    capture = AudioCapture(config=config, output_queue=capture_queue)
    playback = AudioPlayback(config=config, input_queue=playback_queue)

    try:
        print("Starting audio devices...")
        await capture.start()
        await playback.start()

        # Run in background
        capture_task = asyncio.create_task(capture.run())
        playback_task = asyncio.create_task(playback.run())

        print("Pipeline running. Listening for 5 seconds...")

        # Optional: Loopback demo (echo capture to playback)
        # async def loopback():
        #     while True:
        #         msg = await capture_queue.get()
        #         await playback_queue.put(msg["data"])
        # asyncio.create_task(loopback())

        await asyncio.sleep(5.0)

        print("Shutting down pipeline...")

    finally:
        await capture.stop()
        await playback.stop()
        if "capture_task" in locals():
            capture_task.cancel()
        if "playback_task" in locals():
            playback_task.cancel()

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
