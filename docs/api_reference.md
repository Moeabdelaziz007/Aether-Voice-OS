# 📚 Aether OS API Reference

## 🛠️ Core Modules

### `core.engine.AetherEngine`

The central orchestrator of the OS.

- `__init__(config: Optional[AetherConfig])`: Initializes all sub-components.
- `run()`: Starts the TaskGroup containing audio capture, playback, Gemini session, and gateway.
- `register_tool(name: str, tool: Any)`: Registers a legacy ADK tool.

### `core.ai.session.GeminiLiveSession`

Manages the bidirectional WebSocket to Gemini.

- `connect()`: Establishes the connection.
- `run()`: Starts the `_send_loop` and `_receive_loop`.
- `_handle_tool_call(session, tool_call)`: Dispatches function calls to the `ToolRouter`.

### `core.transport.gateway.AetherGateway`

The secure entry point for external UI clients.

- `run()`: Binds the WebSocket server (Port 18789).
- `broadcast(event: str, data: dict)`: Sends a message to all connected clients.
- `verify_handshake(token: str)`: Ed25519 signature verification.

### `core.audio.processing`

High-performance audio utilities (Rust-accelerated).

- `RingBuffer(capacity_samples: int)`: O(1) circular buffer.
- `find_zero_crossing(pcm_data, ...)`: Finds clean cut points.
- `energy_vad(pcm_chunk, threshold)`: Local energy-based VAD.

### `core.identity.registry.AetherRegistry`

Package manager for `.ath` files.

- `scan()`: Scans `brain/packages/` for valid manifests.
- `get_package(name: str)`: Returns a `SoulManifest` object.

## 🔧 Tools (ADK)

### `core.tools.system_tool`

- `get_current_time()`: Returns the current ISO timestamp.
- `get_system_info()`: Detailed hardware/OS metadata.

### `core.tools.tasks_tool`

- `create_task(title: str)`: Writes a new task to Firestore.
- `list_tasks()`: Retrieves pending tasks from Firestore.

### `core.tools.memory_tool`

- `save_memory(key, value)`: Stores semantic context in long-term memory.
- `recall_memory(key)`: Retrieves stored context.
