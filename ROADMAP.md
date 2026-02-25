# 🗺️ Aether Voice OS - The Master Roadmap

*The blueprint to the Gemini Live Agent Challenge 2026*

This roadmap breaks down the final realization of the Aether vision into precise, execution-ready substeps, combining the **Whisper Flow UX**, **Gemini Native Audio**, **Firebase**, **Google ADK**, and **OpenClaw** into a single, cohesive architecture.

---

## 🏗️ Phase 1: Core Voice Infrastructure (✅ COMPLETED)

We have successfully built the highly complicated backend. Aether now "listens and thinks".

- [x] **1.1 Gemini Live Audio Integration:** Bidirectional PCM audio streaming using `google-genai` and Gemini 2.5 Flash Native Audio.
- [x] **1.2 Tumbling Window Buffer:** Advanced digital signal processing (VAD, Zero-Crossing detection) for ultra-low latency & click-free interruptions.
- [x] **1.3 The `.ath` Package System:** Agent DNA encapsulated into portable packages (`Soul.md`, `Skills.md`, `manifest.json`, `heartbeat.md`).
- [x] **1.4 OpenClaw Gateway Base:** A secure WebSocket gateway orchestrating connections between the UI and the ADK logic layer.

---

## 🎨 Phase 2: The "Wispr Flow" Visual UX (🚧 NEXT UP)

The goal is an interface that feels "alive and always with you" — a sleek, floating widget design that visualizes thought and speech.

- **2.1 Global Floating Widget (Tauri/Next.js)**
  - [ ] Initialize Next.js 15 Monorepo/Workspace for the frontend UI.
  - [ ] Set up Tauri V2 to wrap the Next.js app natively.
  - [ ] Configure `tauri.conf.json` for a borderless, transparent, floating window constraint (always on top).
  - [ ] Implement MacOS-like global hotkey listener (`Cmd+Option+Space`) in Tauri Rust backend.
  - [ ] Build the base "pill" React container with TailwindCSS (dark mode, glassmorphism `backdrop-blur-md`, carbon fiber aesthetics).

- **2.2 The "Moving Line" Audio Visualizer**
  - [ ] Set up WebGL canvas or Framer Motion wrapper for high-FPS rendering.
  - [ ] Write `LiveWaveLine.tsx` React Component accepting dynamic PCM buffers.
  - [ ] Connect `LiveWaveLine` to real-time `AnalyzerNode` from the browser's audio context (or via WebSocket telemetry from the Python engine).
  - [ ] Implement visual state machine triggers:
    - [ ] **Idle:** thin grey pulse.
    - [ ] **Listening:** cyan glowing expanding string (`box-shadow: 0 0 15px cyan`).
    - [ ] **Thinking:** fast pulsating geometric shifts.
    - [ ] **Speaking:** aggressive dynamic waveform matching Gemini's output decibel array.

- **2.3 The Conversation Log UX**
  - [ ] Create an expandable, hidden transcription drawer in the DOM (`framer-motion` height animation).
  - [ ] Connect UI to OpenClaw WebSocket to receive `ModelTurn` text chunks in real-time.
  - [ ] Implement `MarkdownRenderer` for token streaming with smooth simulated typing.
  - [ ] Add auto-scroll-to-bottom logic for continuous conversation logs.

---

## 🔥 Phase 3: Firebase Cloud Native Backend

Shift from local/GCP defaults strictly to **Firebase Cloud**, minimizing dev-ops and maximizing real-time capabilities.

- **3.1 Firebase CLI & Project Init**
  - [x] Authenticate MCP & `firebase init` to link the local repo to `notional-armor-456623-e8`.
  - [x] Generate SDK Configuration and initialize Firestore rules locally.
  - [ ] Write `core/config.py` parser to load Firebase Admin SDK JSON keys programmatically.
  - [ ] Enable Firebase Authentication natively (Anonymous Login) and fetch Custom Tokens for Python.

- **3.2 Firestore Cloud Memory (L2 Cortex)**
  - [ ] Define precise Firestore schemas for `users/{userId}/sessions/{sessionId}`.
  - [ ] Map Aether's `memory_tool.py` explicitly to Firestore Collections (`setDoc()`, `getDoc()`).
  - [ ] Refactor Python Engine to pipe session history logs directly to Firestore `messages` subcollection.
  - [ ] Implement live frontend reactivity: Use Firebase Client SDK `onSnapshot` to render memory updates instantaneously in the widget UI.

- **3.3 Firebase Serverless Engine (Optional/Scalability)**
  - [ ] Initialize `firebase init functions` container.
  - [ ] Migrate heavy ADK processing nodes into HTTP-triggered Cloud Functions.
  - [ ] Connect Firebase Storage to act as the globally distributed `.ath` Package Repository.

---

## 🤖 Phase 4: Google ADK & OpenClaw Skills Hub

Give Aether "hands" and "superpowers" to control the desktop or fetch cloud data autonomously.

- **4.1 OpenClaw Channel Architecture Enrichment**
  - [ ] Finalize `core/transport/gateway.py` with strict structured typing (Pydantic models).
  - [ ] Implement deterministic routing logic: Audio chunks ↔ Transcriber, JSON Payloads ↔ Web UI.
  - [ ] Enforce Ed25519 payload signing validation for security.

- **4.2 Google ADK Node Execution Pipeline**
  - [ ] Adapt the `core/engine.py` tool router to natively consume Google ADK's `FunctionDeclaration` schema.
  - [ ] **Build `system_tool.py`:** Add Python `subprocess` triggers to open OS apps, view active task managers, or read local context files.
  - [ ] **Build `vision_tool.py`:** Allow Aether to take screenshots of the user's screen natively to analyze via Gemini Multimodal.
  - [ ] Standardize the JSON response schema for all tools to prevent hallucination errors back to the model.

- **4.3 Autonomous Agent Evolution (Self-Healing)**
  - [ ] Build the `L2_Synapse` daemon: A background Python thread running every 5 minutes.
  - [ ] Configure daemon to scan recent conversation transcripts, extract facts, and overwrite `Heartbeat.md` with refined personality/context.
  - [ ] Upload the mutated `.ath` package state back to Firebase Storage autonomously.

---

## 🏆 Phase 5: Polish & Gemini Live Challenge Submission

- **5.1 Artistic Integration**
  - [ ] Connect the Aether Avatar (Cyberpunk Neural Core) into the UI standby state.
  - [ ] Add subtle breathing/parallax animations to the avatar based on cursor movement.

- **5.2 Quality Assurance & Telemetry**
  - [ ] Conduct extreme E2E stress testing: Voice ↔ Gateway ↔ ADK ↔ Firebase ↔ UI.
  - [ ] Analyze WebRTC vs WebSocket latency; enforce strict <300ms roundtrip audio rules.

- **5.3 Master Demonstration**
  - [ ] Record a 3-minute flawless demonstration video showcasing the Whisper Flow UI, Gemini Speed, and local/cloud tool execution.
  - [ ] Write the DevPost Submission highlighting the Zero-Friction approach, ADK use, Firebase architecture, and `.ath` package modularity.
