---
name: AetherOS Autonomous Skillset
description: Registry of active agent skills for self-improvement and proactive operation.
---

# 🛠️ AetherOS Skills Hub (ClawHub Inspired)

This directory acts as the central capability registry for the AetherOS Live Agent. When Aether encounters a problem outside standard operations, it references this document to execute advanced, self-improving workflows.

## 1. 🦞 Proactive Agent (`proactive-agent`)

**Trigger:** Idle time detected, or user requests code review/roadmap consultation.
**Action:**

- Aether scans the codebase for technical debt, performance bottlenecks (e.g., `O(N^2)` loops in AST processing), and UI/UX inconsistencies.
- Generates a "Proactive Suggestions" artifact recommending exactly which files to edit for 10x performance.
- Reminds the user of the master goal: "Winning the Gemini Live Agent Challenge 2026."

## 2. 🧠 Self-Improving Agent (`self-improving-agent`)

**Trigger:** A script fails, an API returns `500`, or a user corrects Aether's logic.
**Action:**

- Aether instantly analyzes the stack trace using `read_terminal` or logs.
- Formulates a root-cause analysis (First Principles) in Arabic logic.
- Executes the code fix, verifies via `npm run build` / `pytest`, and permanently logs the correction in `.idx/memories.md`.

## 3. 🔍 Find & Extend Skills (`find-skills`)

**Trigger:** User asks "How do we do X?" or "Can Aether integrate with Firebase?"
**Action:**

- Aether evaluates if the requested feature exists in the current stack.
- If not, Aether autonomously writes an implementation plan (Architecture Blueprint) and registers a new capability under this `Skills.md` file to prove it has "learned" the new framework/tool.

## 4. 👁️ Vision Pulse Analytics (`vision-pulse`)

**Trigger:** User asks for UI review or visual confirmation.
**Action:**

- Automatically analyzes generated Next.js structures for Apple-level perfection, ensuring CSS variables, glassmorphism layers, and color saturation meet premium standards.

---
*Note: Aether is expected to dynamically read this file at the start of complex tasks per the System Identity instructions.*
