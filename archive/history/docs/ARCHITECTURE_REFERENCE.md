# Aether Voice OS — Architecture Reference

## 1. System Overview

Aether Voice OS is a layered voice-first runtime that combines low-latency audio processing, Gemini Live session orchestration, secure gateway transport, and tool execution.

Core execution starts in `core/server.py`, boots `AetherEngine`, and orchestrates audio, AI session, gateway, tool routing, and telemetry.

## 2. Layer Decomposition

- Audio Layer: `core/audio/*` handles capture, playback, VAD, muting, paralinguistics, and AEC-related utilities.
- AI Layer: `core/ai/*` handles live session lifecycle, proactive behavior, handover logic, and expert coordination.
- Infrastructure Layer: `core/infra/*` provides config, telemetry, service wiring, and transport state.
- Transport Layer: `core/infra/transport/*` implements WebSocket protocol, handshake, state transitions, and bus bridging.
- Tool Layer: `core/tools/*` provides callable runtime tools and central dispatch with security controls.
- Identity Layer: `core/identity/*` provides `.ath` package and registry model for expert manifests.

## 3. Runtime Data Flow

1. Mic PCM enters capture loop (`core/audio/capture.py`).
2. Processed chunks are queued to AI session input.
3. Gemini Live session (`core/ai/session.py`) streams request/response audio and tool calls.
4. Output PCM is queued to playback and gateway.
5. Gateway (`core/infra/transport/gateway.py`) serves authenticated clients and forwards events.

## 4. Session and Gateway Lifecycle

Handshake protocol:

- `connect.challenge` from server
- `connect.response` from client with Ed25519 signature
- `connect.ack` from server on success

Session state is controlled by `SessionStateManager` to keep transitions explicit and observable.

## 5. Security Controls

- Ed25519 challenge-response verification in gateway transport.
- JWT path available for service communication.
- Biometric voice check gate in tool router for sensitive tool execution.
- Restricted command execution policy in `system_tool`.

## 6. Performance and Reliability Priorities

- Keep audio callbacks non-blocking and queue-driven.
- Favor deterministic state transitions for reconnect/recovery behavior.
- Preserve graceful degradation for optional cloud dependencies.
- Keep portal and backend protocol contracts version-aligned.

## 7. Operational Validation Baseline

- Syntax compile: `python3 -m compileall core tests`
- Focused core lint: `ruff check core/engine.py core/audio/capture.py core/server.py core/tools/router.py core/tools/system_tool.py`
- Gateway/system regressions: `pytest tests/test_system_tool.py tests/integration/test_gateway_e2e.py -q`
- Portal tests: `cd apps/portal && npm run test`
