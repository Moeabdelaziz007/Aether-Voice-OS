---
name: aether-voice
version: 0.7.0
description: Full-duplex voice agent powered by Gemini Live native audio. Always-listening, barge-in support, sub-300ms latency.
author: AetherOS
license: Apache-2.0
tags:
  - voice
  - gemini-live
  - audio
  - agent
  - real-time
requires:
  - pyaudio>=0.2.14
  - google-genai>=1.0.0
  - pydantic-settings>=2.0.0
  - python-dotenv>=1.0.0
entry: run_aether.py
---

# Aether Voice — Live Agent Skill

A standalone voice interaction skill that connects your agent to **Gemini Live API** for full-duplex, native audio conversations.

## Features

- **Always Listening** — No push-to-talk button. The agent listens the moment it starts.
- **Barge-in** — Interrupt the AI mid-sentence and it stops immediately.
- **Native Audio** — Gemini handles STT + reasoning + TTS in a single model call. No Whisper, no external TTS.
- **ADK Compatible** — Follows `setup → execute → teardown` lifecycle.
- **State Machine** — Tracks `idle → initializing → listening → speaking → stopped`.

## Quick Start

```bash
# Set your API key
export GOOGLE_API_KEY='your-key-here'

# Install dependencies
pip install pyaudio google-genai pydantic-settings python-dotenv

# Run
python run_aether.py
```

## As a Tool

```python
from core.tools.voice_tool import VoiceTool

tool = VoiceTool()
await tool.setup()
await tool.execute()  # blocks until Ctrl+C or shutdown
```

## Architecture

```
Mic (PyAudio) → asyncio.Queue → Gemini Live (WebSocket) → asyncio.Queue → Speaker (PyAudio)
                                        ↕
                              Barge-in Detection
                              State Management
```

## Configuration

All settings are loaded from environment variables or `.env`:

| Variable | Default | Description |
|:---------|:--------|:------------|
| `GOOGLE_API_KEY` | — | Gemini API key (required) |
| `AETHER_AUDIO_SEND_SAMPLE_RATE` | 16000 | Mic sample rate (Hz) |
| `AETHER_AUDIO_RECEIVE_SAMPLE_RATE` | 24000 | Speaker sample rate (Hz) |
| `AETHER_AI_MODEL` | gemini-2.5-flash-native-audio | Model ID |
| `AETHER_AI_ENABLE_AFFECTIVE_DIALOG` | true | Emotion-aware responses |
| `AETHER_AI_PROACTIVE_AUDIO` | true | Model decides when to speak |
