# 💎 GEMIGRAM V2: Technical Specifications & Immersive UX

This document serves as the definitive technical reference for the **GEMIGRAM** Voice-First platform, consolidating all architectural, UI, and troubleshooting specifications.

---

## 🎙️ Voice-First Philosophy (The Neural Spine)

GEMIGRAM is a **pure voice-native** ecosystem. We have eliminated all traditional chatbox elements to provide a cinematic, immersive Experience.

### Core Interface Principles
- **Zero Chatbox**: No text inputs, persistent logs, or message bubbles.
- **Cinematic Pacing**: Every interaction is visualized through dynamic neural pulses.
- **Micro-Transcripts**: Transient text pulses (4s duration) provide visual confirmation without clutter.
- **State-Reactive HUD**: The environment (Aura, Lightning field) adapts to the agent's emotional and cognitive state.

---

## 🏗️ System Architecture

### Frontend: Client-Side Intelligence
- **Framework**: Next.js 15 (React 19)
- **State Management**: Zustand with `useAetherGateway` hook.
- **Neural Sync**: Direct WebSocket connection to Gemini Multimodal Live.
- **Memory**: Bidirectional sync with **Firestore** for real-time state persistence.

### Key Components
1. **NeuralOrb**: The central interaction node. Responsive to audio frequency and intent detection.
2. **Aether Forge**: The multi-step agent creation flow (Identity → Brain → Voice → Deploy).
3. **Communication Sanctum**: The immersive primary workspace where user and agent collaborate.
4. **AgentHive**: Relational card system for managing multiple specialized agents.

---

## 🛠️ Infrastructure & Troubleshooting

### Firebase Integration
To prevent **Hydration Mismatches** and **SSR Errors**, all Firebase initializations are gated by `isClient` checks to ensure they only run in the browser environment.

#### Mandatory Environment Variables
```env
NEXT_PUBLIC_FIREBASE_API_KEY="..."
NEXT_PUBLIC_FIREBASE_PROJECT_ID="..."
NEXT_PUBLIC_AETHER_GATEWAY_URL="ws://localhost:18789"
```

### Common Fixes
| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `invalid-api-key` | SSR attempt to load Firebase | Use `AuthGuard` with `isMounted` state. |
| `Hydration mismatch` | Server/Client HTML divergence | Wrap voice components in `dynamic(() => ..., { ssr: false })`. |
| `Microphone blocked` | Permission or WebSocket URL | Verify SSL for production URLs and browser permissions. |

---

## 🧪 Deployment & Verification
- **Hosting**: Firebase Hosting (Static Optimized).
- **Domain**: `aetheros.web.app` or custom associated domains.
- **CI/CD**: Unified pipeline (`aether_pipeline.yml`) ensures linting, Rust signal checks, and Python test coverage (>40%).

> [!NOTE]
> For local development without Firebase, the system automatically falls back to a **Mock User** session to ensure zero downtime for UI testing.
