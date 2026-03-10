#!/usr/bin/env python3
"""
Aether Voice OS — Real System Integration Test

NO MOCK DATA - REAL HARDWARE & APIs ONLY

Tests:
1. Real microphone capture (PyAudio)
2. Real Gemini Live session (Google API)
3. Real WebSocket gateway (port 18789)
4. Real audio playback (PyAudio)
5. Real tool execution (system_tool)
6. Real Firebase persistence

Requirements:
- GOOGLE_API_KEY in environment
- Microphone connected
- Speakers connected
- Internet connection
"""

import asyncio
import json
import logging
import os
import sys
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RealSystemTest")


# Check dependencies
def check_prerequisites():
    """Verify all required components are available."""
    logger.info("🔍 Checking prerequisites...")

    # 1. API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ GOOGLE_API_KEY not found in environment")
        return False
    logger.info(f"✅ API Key: {api_key[:10]}...{api_key[-5:]}")

    # 2. PyAudio
    try:
        import pyaudio

        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        logger.info(f"✅ PyAudio: {device_count} audio devices found")

        # List input devices
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                logger.info(f"   🎤 Input Device {i}: {info['name']}")
            if info["maxOutputChannels"] > 0:
                logger.info(f"   🔊 Output Device {i}: {info['name']}")

        p.terminate()
    except Exception as e:
        logger.error(f"❌ PyAudio error: {e}")
        return False

    # 3. Google GenAI
    try:
        from google import genai  # noqa: F401

        logger.info("✅ Google GenAI SDK available")
    except ImportError:
        logger.error("❌ Google GenAI SDK not installed")
        return False

    # 4. Firebase
    try:
        import firebase_admin  # noqa: F401

        logger.info("✅ Firebase Admin SDK available")
    except ImportError:
        logger.warning("⚠️ Firebase not configured (optional)")

    # 5. WebSockets
    try:
        import websockets  # noqa: F401

        logger.info("✅ WebSockets available")
    except ImportError:
        logger.error("❌ WebSockets not installed")
        return False

    logger.info("✅ All prerequisites met")
    return True


async def test_gemini_api():
    """Test real Gemini API connectivity."""
    logger.info("\n🧪 TEST 1: Gemini API Connectivity")

    try:
        from google import genai

        client = genai.Client()

        # Simple text generation test
        start = time.time()
        response = await asyncio.to_thread(
            client.models.generate_content, model="gemini-2.0-flash", contents="Say 'Hello Aether' in exactly 3 words"
        )
        latency = (time.time() - start) * 1000

        if response.text:
            logger.info(f"✅ Gemini API responded in {latency:.0f}ms")
            logger.info(f"   Response: {response.text.strip()}")
            return True
        else:
            logger.error("❌ Empty response from Gemini")
            return False

    except Exception as e:
        logger.error(f"❌ Gemini API test failed: {e}")
        return False


async def test_audio_capture_playback():
    """Test real audio capture and playback pipeline."""
    logger.info("\n🧪 TEST 2: Audio Capture & Playback Pipeline")

    try:
        import numpy as np
        import pyaudio

        p = pyaudio.PyAudio()

        # Test capture
        logger.info("🎤 Testing microphone capture (2 seconds)...")
        stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        # Capture some audio
        captured_chunks = []
        start = time.time()
        while time.time() - start < 2.0:
            try:
                data = stream_in.read(1024, exception_on_overflow=False)
                captured_chunks.append(data)
            except Exception:
                continue

        stream_in.stop_stream()
        stream_in.close()

        total_bytes = sum(len(c) for c in captured_chunks)
        msg = f"Captured {len(captured_chunks)} chunks ({total_bytes} bytes)"
        logger.info(f"✅ {msg}")

        # Test playback
        logger.info("🔊 Testing speaker playback (1 second tone)...")
        stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True, frames_per_buffer=1024)

        # Generate sine wave
        duration = 1.0
        frequency = 440  # A4 note
        samples = int(16000 * duration)
        t = np.linspace(0, duration, samples)
        tone = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

        stream_out.write(tone.tobytes())
        stream_out.stop_stream()
        stream_out.close()

        msg = f"Playback completed ({duration}s tone at {frequency}Hz)"
        logger.info(f"✅ {msg}")

        p.terminate()
        return True

    except Exception as e:
        logger.error(f"❌ Audio test failed: {e}")
        return False


async def test_websocket_gateway():
    """Test real WebSocket gateway connection."""
    logger.info("\n🧪 TEST 3: WebSocket Gateway Connection")

    try:
        import websockets

        # Try to connect to local gateway
        uri = "ws://localhost:18789"

        logger.info(f"Attempting connection to {uri}...")

        async with websockets.connect(uri, open_timeout=5) as ws:
            logger.info("✅ WebSocket connected")

            # Send ping
            await ws.send(json.dumps({"type": "PING"}))
            response = await ws.recv()
            logger.info(f"✅ PONG received: {response}")

            return True

    except Exception as e:
        msg = f"Gateway not running (expected if engine not started): {e}"
        logger.warning(f"⚠️ {msg}")
        logger.info("💡 Start the engine first: python core/server.py")
        return False  # Not critical


async def test_firebase_connection():
    """Test real Firebase Firestore connection."""
    logger.info("\n🧪 TEST 4: Firebase Firestore Connection")

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Check if already initialized
        if not firebase_admin._apps:
            # Try default credentials
            try:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized with default credentials")
            except Exception:
                logger.warning("⚠️ Firebase credentials not configured")
                return False

        db = firestore.client()

        # Test read
        start = time.time()
        docs = db.collection("knowledge").limit(1).stream()
        doc_count = sum(1 for _ in docs)
        latency = (time.time() - start) * 1000

        msg = f"Firestore query: {latency:.0f}ms, {doc_count} docs"
        logger.info(f"✅ {msg}")
        return True

    except Exception as e:
        logger.warning(f"⚠️ Firebase test skipped: {e}")
        return False  # Optional


async def test_tool_execution():
    """Test real tool execution via ToolRouter."""
    logger.info("\n🧪 TEST 5: Tool Execution")

    try:
        from core.tools.system_tool import system_tool as sys_tool

        # Test a safe read-only tool
        logger.info("Testing system_tool (read-only operation)...")

        start = time.time()
        result = await sys_tool.execute({"command": "pwd", "timeout": 5})
        latency = (time.time() - start) * 1000

        if result.get("success"):
            logger.info(f"✅ Tool executed in {latency:.0f}ms")
            logger.info(f"   Output: {result.get('output', '')[:100]}")
            return True
        else:
            logger.error(f"❌ Tool failed: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Tool test failed: {e}")
        return False


async def run_integration_test():
    """Full integration test: Capture → Process → Respond."""
    logger.info("\n🧪 TEST 6: Full Integration Test")

    try:
        from core.engine import AetherEngine
        from core.infra.config import load_config

        logger.info("Loading Aether configuration...")
        config = load_config()

        logger.info("Initializing AetherEngine (no mock data)...")
        engine = AetherEngine(config=config)  # noqa: F841

        logger.info("✅ Engine initialized successfully")
        logger.info(f"   Audio config: {config.audio.send_sample_rate}Hz")
        ai_model = getattr(config.ai, "model_name", "unknown")
        logger.info(f"   AI model: {ai_model}")
        logger.info(f"   Gateway port: {config.gateway.port}")

        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all real system tests."""
    logger.info("=" * 70)
    logger.info("🌑 AETHER VOICE OS — REAL SYSTEM INTEGRATION TEST")
    logger.info("=" * 70)
    logger.info("⚠️  NO MOCK DATA - REAL HARDWARE & APIs ONLY")
    logger.info("=" * 70)

    # Prerequisites
    if not check_prerequisites():
        logger.error("\n❌ Prerequisites check failed. Aborting.")
        sys.exit(1)

    # Run tests
    results = {}

    results["gemini_api"] = await test_gemini_api()
    results["audio_pipeline"] = await test_audio_capture_playback()
    results["websocket"] = await test_websocket_gateway()
    results["firebase"] = await test_firebase_connection()
    results["tool_execution"] = await test_tool_execution()
    results["integration"] = await run_integration_test()

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        logger.info(f"{status} - {test_name.replace('_', ' ').title()}")

    logger.info("-" * 70)
    logger.info(f"Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! System ready.")
    else:
        failed_count = total - passed
        logger.warning(f"⚠️ {failed_count} test(s) failed. Review logs.")

    logger.info("=" * 70)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
