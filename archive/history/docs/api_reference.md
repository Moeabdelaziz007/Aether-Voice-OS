# 📚 AetherOS: Neural API Codex (V2.0)

> **"Code is the implementation; the Codex is the intent."**
> A functional reference for the core Python classes of the AetherOS engine.

---

## 🧠 Core Orchestration

### `core.engine.AetherEngine`

The central nervous system of AetherOS.

- **`__init__(config: Optional[AetherConfig] = None)`**
  - Initializes all managers (Audio, Agent, Infra) and the ToolRouter.
  - Loads local vector indices for semantic search.
- **`run()`** (Async)
  - **Latency Tier**: `cold_start` (~44s) / `warm_start` (<5s)
  - Orchestrates the `asyncio.TaskGroup` for all sub-services.
- **`_on_affective_data(features: Any)`**
  - Handles real-time paralinguistic data (frustration, valence).
  - Broadcasts `affective_score` events to the gateway.

---

## 📡 Communication & Streaming

### `core.infra.transport.gateway.AetherGateway`

The secure single source of truth for all AI sessions.

- **`broadcast(msg_type: str, payload: dict)`** (Async)
  - **Performance**: Thread-safe with `asyncio.timeout(2.0)` guard.
  - Dispatches JSON events to all authenticated WebSocket clients.
- **`broadcast_binary(data: bytes)`** (Async)
  - Routes raw PCM audio data directly to the playback buffers.
- **`request_handoff(target_soul: str)`** (Async)
  - **Pattern**: Deep Handover (ADK 2.0).
  - Initiates state serialization and speculate-warms the target agent session.

### `core.ai.session.GeminiLiveSession`

Manages the raw multimodal stream to Google's Gemini API.

- **`connect()`** (Async)
  - Establishes the `LiveConnect` WebSocket.
- **`inject_handover_context(context: HandoverContext)`**
  - Merges external history and memory into the current system instruction.
- **`_receive_loop(session)`** (Async internal)
  - The "Neural Switchboard" that handles audio, tool calls, and barge-in interruptions.

---

## 🛠️ Tool Dispatching (ADK 2.0)

### `core.tools.router.ToolRouter`

The high-performance kernel for tool execution.

- **`register_module(module: Any)`**
  - Introspects modules for `get_tools()` and adds them to the registry.
- **`dispatch(function_call: types.FunctionCall)`** (Async)
  - **Middleware**: Executes `BiometricMiddleware` (Soul-Lock) for sensitive tools.
  - **Parallelism**: Runs independent tools concurrently via `TaskGroup`.
- **`profiler`**
  - Exposes `get_stats()` for fetching p50, p95, and p99 metrics for registered tools.

---

## ☁️ Infrastructure & Persistence

### `core.logic.managers.infra.InfraManager`

Manages cloud lifecycle and system health.

- **`initialize()`** (Async)
  - Sets up the `FirebaseConnector` and begins the session audit trail.
- **`start_watchdog()`**
  - Spawns the SRE Watchdog to monitor node health and handle autonomous recovery.
