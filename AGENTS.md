# AGENTS.md — Aether Voice OS

> The unified context file for AI agents operating within the Aether OS codebase.
> This document follows the [AGENTS.md standard](https://agentsmd.io) for AI-native development.

## 🌌 Project Overview

**Aether Voice OS** is a real-time, multimodal AI operating system built for the
**Google Gemini Live Agents Challenge 2026**. It combines Gemini 2.0 Multimodal
Live API, Google ADK, and Firebase to deliver zero-latency voice-first AI interactions.

### Architecture at a Glance

```
┌─────────────────────────────────────────────────────┐
│                   Aether Voice OS                   │
├──────────┬──────────┬──────────┬────────────────────┤
│  Voice   │ Gateway  │  Runner  │     Registry       │
│ Stream   │ OpenClaw │   ADK    │    .ath Packages   │
│ (Gemini) │ (WS/TLS) │ (Orch.) │  (Soul/Skills)     │
├──────────┴──────────┴──────────┴────────────────────┤
│              Firebase (Firestore + Functions)        │
└─────────────────────────────────────────────────────┘
```

### Directory Structure

```
core/               # Python backend engine
  windowing.py      # Audio tumbling windows + zero-crossing detection
  voice_stream.py   # Gemini 2.0 Multimodal Live client
  gateway.py        # OpenClaw WebSocket gateway (Ed25519 auth)
  runner.py         # Central ADK orchestrator
  registry.py       # .ath package loader & hot-swap
docs/               # Technical specifications
  agent.md          # Persona & DNA specification
  gateway_protocol.md  # OpenClaw handshake reference
brain/              # Agent identity packages
  aether-persona/   # Core persona files (Soul.md, Skills.md)
  packages/         # Loadable .ath agent packages
skills/             # Skill modules for tool execution
apps/web/           # Next.js frontend (Phase 3)
```

---

## 🛠️ Setup & Build

```bash
# 1. Create and activate virtual environment
python3 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install google-generativeai fastapi uvicorn websockets \
  python-dotenv numpy cryptography pydantic watchdog

# 3. Set environment variables
export GOOGLE_API_KEY="your-key-here"

# 4. Run the gateway
python -m core.gateway

# 5. Run the orchestrator
python -m core.runner
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov-report=term-missing

# Lint check
flake8 core/ --max-line-length=120
```

---

## 📐 Coding Standards

| Rule | Convention |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Type Hints** | Required on all public functions |
| **Docstrings** | Google-style, required on classes and public methods |
| **Line Length** | 120 characters max |
| **Imports** | `isort` ordering: stdlib → third-party → local |
| **Async** | Prefer `asyncio` over threads for I/O-bound work |
| **Secrets** | Never hardcode. Use `.env` + `python-dotenv` |
| **Error Handling** | Explicit exceptions with context messages |

---

## 🔐 Security Boundaries

- **API Keys:** Injected via environment variables only. Never committed.
- **Gateway Auth:** Ed25519 challenge-response (see `docs/gateway_protocol.md`).
- **Workspace Access:** All tool execution is sandboxed with `workspace: "ro"` by default.
- **Package Integrity:** `.ath` packages are verified with SHA256 checksums before loading.

---

## 🧠 Domain Context

### Audio Processing

- **Chunk Size:** 150ms PCM windows (16kHz, 16-bit mono).
- **Barge-in:** Zero-crossing detection prevents audio clicks during interruption.
- **VAD:** Energy-based voice activity detection triggers processing.

### Agent Identity (.ath Packages)

- `Soul.md` — Core persona instructions and bias parameters.
- `Skills.md` — Available tools and MCP integrations.
- `heartbeat.md` — Autonomous background routines.

### Multi-Agent Orchestration

- Supervisor pattern: `runner.py` delegates to specialized sub-agents.
- State shared via Firebase Firestore (L1: session, L2: long-term memory).
- Capability-based access control prevents privilege escalation.

---

## 🤖 Agent Instructions

When modifying this codebase:

1. **Always run `flake8`** before committing. Zero warnings policy.
2. **Never modify `.env`** or credential files.
3. **Test audio changes** with synthetic PCM data, not live microphone.
4. **Respect the gateway protocol** — changes to handshake require updating `docs/gateway_protocol.md`.
5. **Update `AGENTS.md`** if you add new directories, commands, or conventions.
