# 🖥️ AetherOS: Frontend Architecture (Neural UI)

> **"The UI is the window into the AI's mind."**
> AetherOS uses a **Hybrid Tauri/Next.js 15** architecture to deliver a hardware-accelerated, transparent desktop overlay.

---

## 🏛️ The Structural Conductor: `AetherBrain`

The frontend is orchestrated by an invisible component called `AetherBrain.tsx`. It acts as the "Central Nervous System" by:

1. **Starting the Audio Pipeline**: Initializing microphone capture and speaker playback.
2. **Opening the Gateway**: Connecting to the Python backend via WebSocket (Port 18789).
3. **Internal Routing**: Piping raw PCM chunks from the mic to the gateway, and back from the gateway to the speaker.

---

## 🔐 The OpenClaw Gateway Bridge

The `useAetherGateway` hook implements a **Zero-Trust Handshake**:

- **Ed25519 Auth**: Uses `tweetnacl` to sign a challenge from the server, proving client identity.
- **Binary PCM Stream**: High-frequency audio data is sent as raw `ArrayBuffer` to minimize serialization overhead.
- **Tick Sync**: Maintains a 15-second heartbeat to ensure connection integrity.

---

## 🧠 State Management: Zustand `useAetherStore`

We use a single-store pattern with **Zustand** for global reactivity.

- **`status`**: Current connection state (`connecting`, `connected`, `error`).
- **`engineState`**: Reflects the AI's internal state (`LISTENING`, `THINKING`, `SPEAKING`).
- **`affectiveStats`**: Real-time telemetry including `frustrationScore`, `valence`, and `arousal`.
- **`neuralEvents`**: Tracks tool hanovers and active ADK agent tasks.

---

## 🎨 Visualizing the Mind: `NeuralWeb`

The "Neural Synchronizer" is a hardware-accelerated **Three.js** component:

- **`NeuralMesh`**: Renders a dynamic point-cloud network.
- **Reactivity**: The points pulse and change color based on `arousal` and active `neuralEvents`.
- **Performance**: Runs inside a `@react-three/fiber` canvas for 60fps fluidity even during high CPU load.

---

## 🚀 Desktop Overlay Logic (Tauri)

AetherOS resides in a native Tauri shell to achieve:

1. **Transparency**: The background is fully transparent (`alpha: true`), allowing only the Glassmorphism widgets to be visible.
2. **Always-On-Top**: Stays visible across all desktops and full-screen apps.
3. **Click-Through**: Leverages Mac-specific APIs to become "intangible" when the user is interacting with their code behind the overlay.

---

## 🧪 Development Workflow

To extend the UI:

1. Add new state to `store/useAetherStore.ts`.
2. Create a component in `components/` utilizing `framer-motion` for animations.
3. Pulse data from the backend via `core/infra/transport/gateway.py`'s `broadcast` method.
