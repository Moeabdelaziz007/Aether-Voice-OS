# 🤖 Gemini Multimodal Integration: The Aether Core

## 1. Overview: The Real-time Brain

Aether OS is built on a "Native Multimodal" architecture. Unlike typical voice assistants that stack separate STT, LLM, and TTS models, Aether uses **Gemini 2.0 Flash** as a single unified engine for audio understanding, visual perception, and vocal synthesis.

---

## 2. Low-Latency Audio Pipeline

The `GeminiLiveSession` manages a bidirectional WebSocket connection to the Gemini Google GenAI API.

### Performance Profile

- **Latency**: ~300ms - 500ms (Glass-to-Ear).
- **Sampling**: 16kHz PCM Audio.
- **Barge-in (Interrupt)**: Gemini natively supports client-side interruptions. When a "barge-in" signal is received, Aether instantly drains the playback queue for a seamless "Listen-When-I-Speak" experience.

### Acoustic Empathy (Backchanneling)

Aether employs a "Silence Architecture" to handle cognitive pauses:

- **Thinking Detection**: If the user pauses during a complex explanation, Aether detects the "Thinking" acoustic profile.
- **Soft-Affirmatives**: Instead of a full response, Aether injects a text cue (`[user thinking, soft 'Mhm']`) to Gemini, triggering a subtle vocal backchannel that signals active listening without interrupting the user's flow.

---

## 3. Vision Processor (Proactive Perception)

> [!TIP]
> Aether doesn't wait to be asked "What's on my screen?". It perceives the context proactively.

### Proactive Vision Pulse

The `_vision_pulse_loop` runs continuously:

- **Rolling Buffer**: Captures a screenshot every 1 second to maintain a "Temporal Grounding" window.
- **Pulse Every 10s**: Automatically sends a flattened visual state to Gemini to update its spatial awareness of the IDE/Terminal.
- **Hard-Interrupt Camera**: If the user gives a "Hard Interrupt" (emotional/sudden), Aether captures a camera frame to understand the user's facial reaction or physical gestures.

---

## 4. Prompt Engineering & System Instructions

Aether uses **Dynamic Instruction Injection** to switch between Expert Souls:

```markdown
# Base Instructions (The Aether Kernel)
- Be proactive and concise.
- Embody a calm, analytical technical philosophy.
- Use tools (Skills) to interact with the OS.

---
# Handover Context (The Expert Soul)
- You are now the "Elite Coder" expert.
- Context: You are currently debugging `core/ai/session.py`.
- Task: Optimizing the tool calling parallel loop.
```

---

## 5. Function Calling (Tool Matrix)

Gemini manages the tool execution via `ToolRouter`.

- **Parallel Dispatch**: Multiple tool calls are executed concurrently using `asyncio.gather`.
- **Media Injection**: If a tool (like `take_screenshot`) returns binary data, it is injected into the **Next Turn** as an inline multimodal part.

---

## 6. Telemetry & Cost Optimization

- **Usage Metadata**: Every response tracks `prompt_tokens` and `candidates_token_count`.
- **Context Compression**: Long sessions transition to using the `Semantic Seed` to keep the context window (and cost) under control while maintaining high-fidelity recall.
