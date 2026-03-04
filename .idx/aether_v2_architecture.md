# 🧬 AetherOS V2 – Architectural Blueprint (End-to-End Connections)

This document maps how the core modules communicate across the Python Backend and the React Frontend, particularly focusing on the newly integrated Phase 4 features (Real-Time Audio Telemetry & Autonomous Healing).

## 1. The Sensor & Intelligence Layer (Python Domain)

### `core/audio/capture.py` (The Senses)

- **Role**: Continuously samples local audio devices. Now features the `AdaptiveJitterBuffer` to stabilize network latency logic.
- **Outbound Flow**: Every 15Hz (managed by `time.monotonic()`), it calculates Volume (RMS), Gain, and Voice Activity (VAD). It dispatches an `audio_telemetry` event to the `GlobalBus`.
- **Inbound Flow**: Feeds clean, AEC-filtered PCM chunks into the Gemini Multimodal AI.

### `core/services/watchdog.py` (The Nervous System)

- **Role**: Constantly audits system health (Network Latency, AI API Availability, Audio Device Locks).
- **Triggers**: If an error (e.g., `TimeoutException`, `ConnectionError`) occurs, it calls `_heal_system_failure()`.
- **Outbound Flow**: Executes its 3-step healing machine (`diagnosing` → `applied` → `failed`). With each state change, it logs to Firebase (`log_repair_event()`) AND pushes a `frontend_events` PubSub message to the `GlobalBus` (Payload: `{ event: "system_failure", state: ... }`).

---

## 2. The Bridge (Python Domain)

### `core/gateway.py` (The Synapse)

- **Role**: Runs the Secure WebSocket Server (`ws://localhost:18789`). Provides the *only* connection point between the AI Engine and the User Interface.
- **The Telemetry Bridge**: Subscribes to the `GlobalBus` listening for both `audio_telemetry` and `frontend_events`.
- **Outbound Flow**: When an event fires on the bus, `gateway.py` translates it to a structured JSON WebSocket frame (`{ type: "audio_telemetry", payload: ... }` / `{ type: "frontend_event", payload: ... }`) and `self.broadcast()`s it to all active Web GUI clients.
- **Inbound Flow**: Receives React's raw microphone arrays (if running in web-mode) or user vision buffers and routes them to `engine.py`.

---

## 3. The Reception & State Layer (TypeScript Domain)

### `apps/portal/src/hooks/useAetherGateway.ts` (The Receiver)

- **Role**: React Hook that opens and holds the WebSocket connection to the Python Gateway.
- **Inbound Flow**: Implements `onmessage` parsers.
  - If `msg.type === "audio_telemetry"`, it invokes `useAetherStore.getState().setOrbState(msg.payload)`. (Transient update—zero unnecessary re-renders).
  - If `msg.type === "frontend_event" && msg.payload.event === "system_failure"`, it invokes `useAetherStore.getState().triggerSystemFailure(msg.payload.state)`.

### `apps/portal/src/store/useAetherStore.ts` (The Mind)

- **Role**: Zustand Global State Container. Holds all transient states (`micLevel`, `speakerLevel`, `latencyMs`, `systemFailureState`). Designed for ultra-high-performance updates (mutations over re-creation where possible).

---

## 4. The UI / UX Presentation Layer (React Domain)

### `apps/portal/src/components/AetherOrb.tsx` (The Face)

- **Role**: The pulsating visual sphere representing Aether.
- **Connection**: Directly subscribes to `useAetherStore`. Reads `micLevel` and `speakerLevel` to dynamically adjust `energyPulse`, drop-shadows, and scale. Translates the 15Hz Python telemetry into smooth 60FPS CSS/SVG animations.

### `apps/portal/src/components/HUD/SystemFailure.tsx` (The Immune System UI)

- **Role**: The Cyberpunk / Glitch UI overlay that triggers during autonomous healing events.
- **Connection**: Directly subscribes to `systemFailureState` in `useAetherStore`.
- **Behavior**:
  - **`diagnosing`**: Renders a yellow/orange glitch overlay with "Analyzing Critical Fault...".
  - **`applied`**: Turns green, drops the glitch severity, "Deploying Automated Fix...".
  - **`failed`**: Full red lockdown screen, "Manual Intervention Required."

## Next Immediate Steps to Complete the Circuit

1. **Build the `SystemFailure.tsx` UI**: The file is currently completely empty. We need to implement the actual React components (Framer Motion / Tailwind) that consume `systemFailureState` and present the glitch UI.
2. **Wire in the Store**: Verify `systemFailureState` actually exists in `useAetherStore.ts`.
3. **Trigger Testing**: Once built, we manually trigger a Timeout exception in `watchdog.py` and verify that the UI reacts exactly as designed (Firebase log → GlobalBus → Gateway → WebSocket → Store → React Component).
