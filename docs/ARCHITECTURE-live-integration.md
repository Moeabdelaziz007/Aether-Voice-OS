# 🧬 Aether-Voice-OS: Gemini Live Architecture (V3)

This document outlines the solidified architecture for the **Gemini Live** integration in Aether-Voice-OS, focusing on deterministic multimodal grounding and low-latency interaction loops.

## 🏗️ The LiveSession Lifecycle

The `GeminiLiveSession` (managed in `core/ai/session/facade.py`) orchestrates a bidirectional WebSocket connection to the Google GenAI API.

### 1. Connection & Initialization

`core/ai/session/facade.py::GeminiLiveSession.connect()` establishes the primary stream.

- **Warm Start**: The session is pre-initialized using `core/ai/generative_init.py` which sets global safety filters, temperature (0.7), and max output tokens (2048).
- **Tool Declaration**: The `response_schema` feature is utilized to enforce typed JSON outputs from the model during function calling, reducing hallucination in OS-level operations.

### 2. Multimodal Context Injection

`core/ai/session/facade.py::inject_handover_context()` is the entry point for "Temporal Grounding".

- **Visual Stacking**: Frontend frames captured via `apps/portal/src/hooks/useAetherGateway.ts` are sent as WebP-compressed payloads.
- **Payload Mapping**: These are converted to `google.genai.types.Part.from_bytes(data=frame, mime_type="image/webp")` and injected into the active realtime stream.
- **Aesthetic Empathy**: Contextual metadata (CPU load, active window title) is injected alongside frames to allow the AI to say: *"I see you're struggling with that Rust compiler error..."*

### 3. Tool Calling & Validation

Aether uses a centralized `ToolRegistry` to ensure strict schema adherence:

- **Deterministic JSON**: Tools such as `soul_swap` and `open_claw` use Pydantic-derived JSON schemas in `response_schema`.
- **Validation**: `core/ai/session/facade.py::_handle_tool_call` validates arguments before dispatching to `ToolRouter`.

## 📡 Transport & Flow Control

The `AetherGateway` (`core/infra/transport/gateway.py`) maintains the high-performance bridge between client and AI.

- **Rate Limiting**: `AetherGateway.send_text()` implements a 500ms debounce to prevent prompt flooding.
- **Backpressure**: The gateway monitors WebSocket `bufferedAmount` (High Water Mark: 64KB). If exceeded, non-critical vision frames are dropped to prioritize audio latency.
- **Handoff Logic**: `AetherGateway.request_handoff()` triggers a state capture, gathering the last 5 seconds of visual history stored in `useGeminiLive.ts` to "warm up" the target expert.

## 🧪 Audio Pipeline Mapping

| Component | Responsibility | Mapping |
| :--- | :--- | :--- |
| **STT Stream** | User Mic (PCM 16kHz) → Gateway | `core/infra/transport/gateway.py::_route_binary` |
| **Logic Loop** | `GeminiLiveSession` Real-time Loop | `core/ai/session/facade.py::run` |
| **TTS Stream** | Gemini Audio → Frontend Speaker | `core/ai/session/facade.py::_receive_loop` |

## 🚀 Migration Steps

1. **Consolidate Tools**: Move all ad-hoc tool definitions to the `ToolRegistry` in `session/facade.py`.
2. **Schema Enforcement**: Update `ToolRouter` to return results matching the new strict `response_schema`.
3. **Frontend Sync**: Deploy `useAetherGateway.ts` updates to enable WebP compression of Vision Pulses.

---
**Risk Summary**: The primary risk is context window bloating due to high-frequency vision pulsing. We mitigate this using a rolling 10-frame buffer and a "Pulse Ack" mechanism to ensure frames are only kept if they successfully grounded the session.
