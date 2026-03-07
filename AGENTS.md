# 🤖 AetherOS Autonomous Agents (The Hive Mind)

This document maps the **actual** operational agents and cognitive managers currently powering AetherOS V2.0.

---

## 🔬 Core Runtime Agents (The Pre-Frontal Cortex)

| Agent | Module | Functional Responsibility |
| :--- | :--- | :--- |
| **Aether Cortex** | `core/ai/scheduler.py` | Speculative tool execution, temporal grounding from vision pulses, and conversational overlap memory. |
| **Thalamic Gate** | `core/services/thalamic_gate.py` | Paralinguistic analysis, emotion calibration, and proactive barge-in logic based on acoustic frustration scores. |
| **Hive Coordinator** | `core/ai/handover/` | Orchestrates the 4-stage Deep Handover Protocol (Prepare -> Commit -> Switch -> Inject) between specialists. |

---

## 🛠️ Specialized Experts (Operational Handovers)

These experts are dynamically spawned and handed context via the **Hive Gateway**.

1. **Architect Expert**: Handles system-wide blueprints and architectural integrity (powered by Gemini 2.0 Pro).
2. **Debugger Expert**: Specialized in syntax security and autonomous incident recovery (SRE Watchdog integration).
3. **Vision Pulse Agent**: Proactive spatial awareness via 1s rolling screenshot buffers.

---

## 🧬 Identity & Skills (The DNA)

Behavior and capabilities are defined by a unified triple-artifact system:

- **Registry**: `AetherRegistry` (Cosine similarity routing < 50ms).
- **Soul**: Behavioural profiles (Industrial Sci-Fi alignment).
- **Skills Hub**: [Skills.md](file:///Users/cryptojoker710/Desktop/Aether%20Live%20Agent/.idx/Skills.md) (The autonomous capability registry).

---

## 🩺 Self-Healing Infrastructure

- **SRE Watchdog**: Monitors `gateway.py` and `capture.py` for connection drifts/deadlocks.
- **Healing Tool**: Autonomously executes 3-step repair cycles (`diagnosing` -> `applied` -> `failed`) with real-time UI telemetry.

---

*Note: Legacy agent scripts have been moved to `archive/history/legacy_agents/` to ensure architectural purity.*
