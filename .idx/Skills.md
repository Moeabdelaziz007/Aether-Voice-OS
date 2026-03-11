---
name: AetherOS Autonomous Skillset (V3.0)
description: Master Capability Registry including Agent Usage Instructions and GWS Integration.
---

# 🧬 AetherOS Skills Hub (Registry V4.0)

> **"Skills are the neuro-transmitters of the AetherOS. This document is the primary instruction set for Agent Reasoning and the Aether Forge Blueprint."**

---

## 🛠️ Global Execution Protocol

When an agent needs to use a skill, it must:
1. **Identify Intent**: Map user request to a specific Skill Identifier.
2. **Validate Generation**: Check if the skill matches the current V-Tier (V1/V2/V3).
3. **Execute via Gateway**: Use the `gws_connector` or internal `core` tools.

---

## 🛰️ Sector 1: GWS Enterprise (The Core Actions)

### 📧 `gws-gmail-manager` (V1-V2)
**Agent Instructions**: Use this when the user mentions "emails", "inbox", or "summarize messages".
- **V1 (Foundational)**: `get_unread()`, `send_email(to, subject, body)`.
- **V2 (Proactive)**: Detect priorities. If a user receives a high-value email, proactively draft a response and present it via the 3D Avatar.
- **Input Schema**: `{ action: "query" | "send" | "summarize", params: { ... } }`

### 📂 `gws-drive-intel` (V1-V3)
**Agent Instructions**: Use for "finding files", "uploading", or "analyzing documents".
- **V1**: `list_files(query)`, `upload_file(path)`.
- **V2 (Contextual)**: Autonomously find relevant docs for the current task.
- **V3 (Recursive)**: Connect to **GWS Intel Nexus** to perform RAG (Retrieval Augmented Generation) across all Drive PDFs and Docs.
- **Execution**: Internal bridge to `gws drive` CLI logic.

### 🗓️ `gws-calendar-synapse` (V1-V2)
**Agent Instructions**: Trigger for "meetings", "schedule", or "what is my day like?".
- **V2 Feature**: **Calendar Briefing**. The agent should synthesize the day's agenda and trigger a `Gesture: Briefing` on the 3D Avatar.

---

## 🛰️ Sector 2: Neural & Sensory (The Perception)

### 🧠 `aether-neural-os` (V2-V3)
**Agent Instructions**: Use `WAL` (Write-Ahead Log) for any task lasting > 5 minutes or involving critical state changes.
- **Protocol**: Write to `SESSION-STATE.md` before finalizing response.
- **Goal**: Prevent context amnesia across chat sessions.

### 🎙️ `voice-pipeline-thalamic` (V2)
**Agent Instructions**: Do not call manually. This skill is a **Global Filter**.
- **Action**: Monitors `audio_stream` for emotion. If "Anger" or "Frustration" > 0.8, shift Avatar to `State: Comforting`.

---

## 🪐 Sector 3: Galaxy Orchestration (The Network)

### 🌌 `galaxy-orchestrator` (V3)
**Agent Instructions**: Use when a task is too complex for a single message.
- **Logic**: Delegate sub-tasks to specialized Planet Agents (e.g., `Coding-Planet`, `SRE-Planet`).
- **Safety**: Monitor the **Circuit Breaker**. If a Planet Agent returns `500` twice, route back to the **Architect**.

---

## 🤖 Sector 4: Embodiment (The Presence)

### 🕺 `workspace-avatar` (V2)
**Agent Instructions**: Every high-impact response should be accompanied by an avatar gesture.
- **Gestures**: `POINT_TO_TERMINAL`, `THUMBS_UP`, `CONCENTRATING`, `GREETING`.
- **Execution**: `push_state(avatar_id, gesture_name)`.

---

## 🛰️ Sector 5: External Library (ClawHub)

**Agent Instructions**: Use for specialized capabilities not found in Sectors 1-4. Triggers for "install", "fetch from cloud", or "advanced talent acquisition".

### ☁️ `clawhub-acquire` (V1-V2)
- **V1 (Acquisition)**: `install_skill(slug)`. Dynamically pulls logic from ClawHub.ai using `npx clawhub`.
- **V2 (Validation)**: `inspect_skill(slug)`. Audits external skills for security compliance before injection.
- **Protocol**: When a user asks for a skill like "Rust Optimization" or "3D Shaders", query Sector 5 first.

### 🧩 Featured ClawHub Slugs (Ready for Forge)
- `sql-architect`: Advanced schema modeling & optimization.
- `rust-optimizer`: Systems-level performance hot-paths.
- `threejs-master`: WebGL & Spatial computing pipelines.
- `pentest-auditor`: Autonomous security vulnerability scans.

---

## 📜 Error Handling & Fallbacks

- **V1 Failure**: Inform the user clearly and provide the raw CLI error if available.
- **V2 Failure**: Attempt an alternative proactive path (e.g., if draft fails, summarize instead).
- **V3 Failure**: Roll back to V1 execution and log a "Feedback Loop Error" in `.idx/memories.md`.

---
*Note: Aether is expected to dynamically read this file at the start of complex tasks per the System Identity instructions.*
