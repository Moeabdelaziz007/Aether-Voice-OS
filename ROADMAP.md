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
  - [ ] Initialize a minimal, borderless overlay app (Tauri + Next.js 15).
  - [ ] Implement MacOS-like global hotkey (e.g., `Cmd+Option+Space`) to instantly wake Aether.
  - [ ] Build the "pill" container (dark mode, glassmorphism, carbon fiber accents).

- **2.2 The "Moving Line" Audio Visualizer**
  - [ ] Write a custom React Component (`LiveWaveLine.tsx`) driven by WebGL or Framer Motion.
  - [ ] Connect the visualizer to the microphone's real-time raw audio volume/frequency array.
  - [ ] Add states: **Listening** (cyan glowing line), **Thinking** (pulsing glow), **Speaking** (dynamic wave reacting to Aether's output voice).

- **2.3 The Conversation Log UI**
  - [ ] Build an expanding transcript view that drops down from the widget.
  - [ ] Display real-time token streaming / transcription with smooth scroll animations.

---

## 🔥 Phase 3: Firebase Cloud Native Backend

Shift from local/GCP defaults strictly to **Firebase Cloud**, minimizing dev-ops and maximizing real-time capabilities.

- **3.1 Firebase CLI & Project Init**
  - [ ] `firebase init` to link the local repo to the existing Firebase project (`asiom-id` or `notional-armor`).
  - [ ] Set up Firebase Authentication (Anonymous Login for local testing).

- **3.2 Firestore Cloud Memory (L2 Cortex)**
  - [ ] Map Aether's `memory_tool` directly to Firestore Collections (`users/{userId}/sessions`).
  - [ ] Implement live real-time sync (Firestore `onSnapshot`) so the UI updates instantly when Aether executes a task.

- **3.3 Firebase Functions & AI Logic**
  - [ ] Deploy heavy ADK logic processing to Firebase Serverless Functions.
  - [ ] Store `.ath` packages in Firebase Storage for cloud-based Agent Updates.

---

## 🤖 Phase 4: Google ADK & OpenClaw Skills Hub

Give Aether "hands" and "superpowers" to control the desktop or fetch cloud data.

- **4.1 OpenClaw Channel Architecture**
  - [ ] Finalize `core/transport/gateway.py` to act as an OpenClaw Hub.
  - [ ] Structure the WebSocket payloads to strictly adhere to OpenClaw Message Types (Handshake, Tick, Tool execution).

- **4.2 Google ADK Integration**
  - [ ] Refine the `core/engine.py` router using Google ADK Python paradigms.
  - [ ] Build `system_tool.py`: Give Aether local powers (open applications, check system stats, create files).
  - [ ] Build `firebase_tool.py`: Give Aether cloud powers (read/write databases autonomously).

- **4.3 Agent Evolution (Self-Healing)**
  - [ ] Integrate background `Heartbeat.md` routines where Aether periodically summarizes interactions into long-term Firestore memory.

---

## 🏆 Phase 5: Polish & Gemini Live Challenge Submission

- [ ] Connect the Aether Avatar (Cyberpunk Neural Core) into the UI.
- [ ] Record a 3-minute flawless demonstration video (Whisper Flow UI + Gemini Speed + Local Tool Execution).
- [ ] Finalize DevPost submission text and repository documentation.
