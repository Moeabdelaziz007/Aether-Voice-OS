# Gemini Live API Integration

<cite>
**Referenced Files in This Document**
- [session.py](file://core/ai/session.py)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts)
- [AetherBrain.tsx](file://apps/portal/src/components/AetherBrain.tsx)
- [useVisionPulse.ts](file://apps/portal/src/hooks/useVisionPulse.ts)
- [thalamic.py](file://core/ai/thalamic.py)
- [router.py](file://core/tools/router.py)
- [compression.py](file://core/ai/compression.py)
- [processing.py](file://core/audio/processing.py)
- [echo_guard.py](file://core/audio/echo_guard.py)
- [telemetry.py](file://core/infra/telemetry.py)
- [GEMINI.md](file://docs/GEMINI.md)
- [test_gemini_live_session.py](file://tests/unit/test_gemini_live_session.py)
- [geminiLive.integration.test.ts](file://apps/portal/src/__tests__/geminiLive.integration.test.ts)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py)
- [voice_quality_benchmark.py](file://tests/benchmarks/voice_quality_benchmark.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document explains the Gemini Live API integration in Aether Voice OS, focusing on bidirectional audio sessions, session configuration, real-time streaming, structured concurrency, multimodal processing, tool call handling, proactive vision pulses, backchannel loops, interrupt handling, output queue management, compression strategies, and telemetry. It synthesizes the Python backend (core/ai/session.py, core/ai/thalamic.py, core/tools/router.py, core/ai/compression.py, core/audio/processing.py, core/infra/telemetry.py) with the Next.js frontend hooks (apps/portal/src/hooks/useGeminiLive.ts, apps/portal/src/components/AetherBrain.tsx, apps/portal/src/hooks/useVisionPulse.ts) and supporting documentation (docs/GEMINI.md).

## Project Structure
The integration spans:
- Backend AI session and audio processing (core/ai/*, core/audio/*, core/tools/*, core/infra/*)
- Frontend React hooks and UI orchestration (apps/portal/src/hooks/*, apps/portal/src/components/*)
- Documentation and tests (docs/*, tests/*)

```mermaid
graph TB
subgraph "Frontend"
H1["useGeminiLive.ts"]
H2["AetherBrain.tsx"]
H3["useVisionPulse.ts"]
end
subgraph "Backend"
B1["session.py"]
B2["thalamic.py"]
B3["router.py"]
B4["compression.py"]
B5["processing.py"]
B6["echo_guard.py"]
B7["telemetry.py"]
end
H1 --> B1
H2 --> H1
H3 --> B1
B1 --> B2
B1 --> B3
B1 --> B4
B1 --> B5
B1 --> B6
B1 --> B7
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L1-L922)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L1-L485)
- [AetherBrain.tsx](file://apps/portal/src/components/AetherBrain.tsx#L1-L132)
- [useVisionPulse.ts](file://apps/portal/src/hooks/useVisionPulse.ts#L1-L225)
- [thalamic.py](file://core/ai/thalamic.py#L1-L122)
- [router.py](file://core/tools/router.py#L1-L360)
- [compression.py](file://core/ai/compression.py#L1-L115)
- [processing.py](file://core/audio/processing.py#L1-L508)
- [echo_guard.py](file://core/audio/echo_guard.py#L1-L67)
- [telemetry.py](file://core/infra/telemetry.py#L1-L130)

**Section sources**
- [session.py](file://core/ai/session.py#L1-L922)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L1-L485)
- [AetherBrain.tsx](file://apps/portal/src/components/AetherBrain.tsx#L1-L132)
- [useVisionPulse.ts](file://apps/portal/src/hooks/useVisionPulse.ts#L1-L225)
- [GEMINI.md](file://docs/GEMINI.md#L1-L75)

## Core Components
- GeminiLiveSession: Manages the bidirectional Live session, structured concurrency, send/receive loops, tool calls, interrupts, proactive vision pulses, and backchannel loop.
- ThalamicGate: Proactive intervention engine that monitors acoustic states and triggers interventions.
- ToolRouter: Registers tools, validates biometrics, dispatches function calls, and returns standardized results.
- NeuralSummarizer: Compresses long-handover contexts into compact “Semantic Seeds.”
- Audio processing utilities: RingBuffer, VAD engines, and zero-crossing detection for barge-in.
- Telemetry: Usage tracking and OTLP export for cost and performance.
- Frontend hooks: WebSocket management, audio streaming, vision pulses, tool response, and latency measurement.

**Section sources**
- [session.py](file://core/ai/session.py#L43-L235)
- [thalamic.py](file://core/ai/thalamic.py#L11-L122)
- [router.py](file://core/tools/router.py#L120-L360)
- [compression.py](file://core/ai/compression.py#L24-L115)
- [processing.py](file://core/audio/processing.py#L107-L508)
- [telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L65-L485)

## Architecture Overview
The system uses structured concurrency to run send/receive loops, vision pulses, and backchannel loops concurrently. The backend wires a Thalamic Gate for AEC-like echo gating and proactive interventions. The frontend streams PCM audio and vision frames, handles tool calls, and measures latency.

```mermaid
sequenceDiagram
participant FE as "useGeminiLive.ts"
participant WS as "Gemini WebSocket"
participant BE as "GeminiLiveSession"
participant TG as "ThalamicGate"
participant TR as "ToolRouter"
FE->>WS : "connect() + setup()"
WS-->>FE : "setupComplete"
FE->>WS : "sendAudio(pcm)"
WS-->>BE : "realtimeInput"
BE->>TG : "monitor acoustic state"
WS-->>BE : "serverContent (audio/text/toolCall)"
BE->>TR : "dispatch tool_call (parallel)"
TR-->>BE : "results"
BE->>WS : "send_tool_response"
BE-->>FE : "audio bytes"
FE-->>FE : "playback + latency measurement"
```

**Diagram sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L90-L361)
- [session.py](file://core/ai/session.py#L174-L235)
- [thalamic.py](file://core/ai/thalamic.py#L25-L122)
- [router.py](file://core/tools/router.py#L234-L355)

## Detailed Component Analysis

### Session Lifecycle and Structured Concurrency
- Establishes the Live session with a LiveConnectConfig built from tools, system instructions, and voice preferences.
- Runs send_loop, receive_loop, vision_pulse_loop, and backchannel_loop concurrently using TaskGroup.
- Handles exceptions via structured concurrency and cleans up ThalamicGate on exit.

```mermaid
flowchart TD
Start(["run()"]) --> BuildCfg["Build LiveConnectConfig"]
BuildCfg --> Open["Open Live session"]
Open --> StartLoops["TaskGroup: send/receive/vision/backchannel"]
StartLoops --> Receive["receive_loop: usage/tool_call/audio/interrupt"]
Receive --> Send["send_loop: enqueue PCM"]
Receive --> Vision["vision_pulse_loop: capture/inject frames"]
Receive --> Back["backchannel_loop: inject cues"]
Receive --> Exceptions{"Exception?"}
Exceptions --> |Yes| Raise["Raise AISessionExpiredError"]
Exceptions --> |No| Cleanup["Stop ThalamicGate + close"]
Cleanup --> End(["Exit"])
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L174-L235)
- [session.py](file://core/ai/session.py#L237-L265)
- [session.py](file://core/ai/session.py#L383-L477)
- [session.py](file://core/ai/session.py#L266-L341)
- [session.py](file://core/ai/session.py#L343-L382)

**Section sources**
- [session.py](file://core/ai/session.py#L96-L154)
- [session.py](file://core/ai/session.py#L174-L235)
- [session.py](file://core/ai/session.py#L237-L265)
- [session.py](file://core/ai/session.py#L383-L477)
- [session.py](file://core/ai/session.py#L266-L341)
- [session.py](file://core/ai/session.py#L343-L382)

### Session Configuration with LiveConnectConfig
- Tools: Declared via ToolRouter.get_declarations() and optionally Google Search grounding.
- SpeechConfig: Maps a voice_id from the soul manifest to a prebuilt voice.
- Advanced features: affective dialog, proactive audio, thinking budget.

```mermaid
classDiagram
class GeminiLiveSession {
+_build_session_config() LiveConnectConfig
+connect() void
+run() void
}
class ToolRouter {
+get_declarations() list
}
class LiveConnectConfig {
+response_modalities
+system_instruction
+tools
+speech_config
+enable_affective_dialog
+proactivity
+thinking_config
}
GeminiLiveSession --> LiveConnectConfig : "build"
GeminiLiveSession --> ToolRouter : "uses"
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L96-L154)
- [router.py](file://core/tools/router.py#L211-L232)

**Section sources**
- [session.py](file://core/ai/session.py#L96-L154)
- [router.py](file://core/tools/router.py#L211-L232)

### Real-Time Audio Streaming (Frontend and Backend)
- Frontend: Encodes PCM chunks to base64 and sends realtimeInput; decodes audio responses; measures RTT.
- Backend: Reads from audio_in_queue and sends via session.send_realtime_input; writes audio responses to audio_out_queue.

```mermaid
sequenceDiagram
participant FE as "useGeminiLive.ts"
participant WS as "WebSocket"
participant BE as "GeminiLiveSession"
FE->>FE : "encode PCM to base64"
FE->>WS : "realtimeInput {mimeType : 'audio/pcm;rate=16000', data : base64}"
WS-->>BE : "receive() stream"
BE-->>BE : "enqueue audio to out_queue"
BE-->>WS : "send_realtime_input(audio)"
WS-->>FE : "binary audio bytes"
FE-->>FE : "decode + play + measure latency"
```

**Diagram sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L327-L361)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L193-L204)
- [session.py](file://core/ai/session.py#L237-L265)
- [session.py](file://core/ai/session.py#L422-L461)

**Section sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L327-L361)
- [session.py](file://core/ai/session.py#L237-L265)
- [session.py](file://core/ai/session.py#L422-L461)

### Audio Processing Pipeline Integration (Thalamic Gate V2)
- ThalamicGate monitors audio_state, computes frustration, and proactively injects prompts to Gemini when needed.
- EchoGuard implements acoustic identity gating (MFCC-like fingerprint cache) to distinguish self vs user audio.

```mermaid
flowchart TD
A["Monitor audio_state"] --> B["Compute frustration score"]
B --> C{"Should intervene?"}
C --> |Yes| D["send_realtime_input(prompt)"]
C --> |No| E["Continue monitoring"]
D --> F["Record metrics"]
```

**Diagram sources**
- [thalamic.py](file://core/ai/thalamic.py#L41-L122)
- [echo_guard.py](file://core/audio/echo_guard.py#L14-L67)

**Section sources**
- [thalamic.py](file://core/ai/thalamic.py#L11-L122)
- [echo_guard.py](file://core/audio/echo_guard.py#L14-L67)

### Multimodal Capabilities (Audio, Text, Visual)
- Audio: PCM streaming, VAD, barge-in handling, backchannel cues.
- Text: Transcript extraction from model text parts; UI broadcast.
- Visual: Proactive vision pulses every 10s with temporal grounding; hard-interrupt camera capture; optional tool-triggered screenshots injected into the next turn.

```mermaid
graph LR
A["Vision Pulse Loop"] --> B["Take screenshot"]
B --> C["Send PNG + Temporal Grounding"]
A --> D["Hard Interrupt Camera"]
D --> E["Send JPEG on demand"]
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L266-L341)

**Section sources**
- [session.py](file://core/ai/session.py#L266-L341)
- [useVisionPulse.ts](file://apps/portal/src/hooks/useVisionPulse.ts#L45-L225)

### Tool Call Handling System (Parallel Execution)
- Gemini emits functionCalls; session dispatches via ToolRouter.
- Parallel execution with asyncio.gather; biometric middleware for sensitive tools; standardized result wrapping; optional vision injection from tool results.

```mermaid
sequenceDiagram
participant BE as "GeminiLiveSession"
participant TR as "ToolRouter"
BE->>TR : "dispatch(fc) for each function_call"
TR-->>TR : "biometric verification (optional)"
TR-->>BE : "results (wrapped)"
BE->>BE : "send_tool_response(functionResponses)"
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L493-L602)
- [router.py](file://core/tools/router.py#L234-L355)

**Section sources**
- [session.py](file://core/ai/session.py#L493-L602)
- [router.py](file://core/tools/router.py#L120-L360)

### Proactive Vision Pulse and Temporal Grounding
- Maintains a rolling buffer of frames; pulses every 10s with a text grounding marker; broadcasts UI events; captures camera on hard interrupts.

**Section sources**
- [session.py](file://core/ai/session.py#L266-L341)
- [useVisionPulse.ts](file://apps/portal/src/hooks/useVisionPulse.ts#L45-L225)

### Backchannel Loop (Empathetic Responses)
- Monitors silence types; when user is “thinking” or “breathing,” injects a soft text cue to trigger a subtle vocal backchannel without full takeover.

**Section sources**
- [session.py](file://core/ai/session.py#L343-L382)

### Interrupt Handling and Output Queue Management
- On interrupted flag, drains audio output queue instantly; measures drain latency; maintains telemetry counters for queue drops.

**Section sources**
- [session.py](file://core/ai/session.py#L463-L477)
- [session.py](file://core/ai/session.py#L604-L614)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py#L40-L78)

### Compression Strategies
- NeuralSummarizer compresses long conversations into compact “Semantic Seeds” using a lightweight model to reduce token usage during handovers.

**Section sources**
- [compression.py](file://core/ai/compression.py#L24-L115)

### Telemetry Collection
- Usage metadata recorded per response; cost estimation; OTLP export via TelemetryManager; spans enriched with usage attributes.

**Section sources**
- [session.py](file://core/ai/session.py#L479-L492)
- [telemetry.py](file://core/infra/telemetry.py#L77-L130)

## Dependency Analysis
- Frontend depends on Gemini WebSocket protocol and React hooks for streaming and UI orchestration.
- Backend depends on google-genai aio SDK, asyncio queues, and internal tooling.
- ThalamicGate integrates with audio_state and emotion calibration; EchoGuard provides acoustic identity cache.

```mermaid
graph TB
FE["useGeminiLive.ts"] --> WS["Gemini WebSocket"]
FE --> UI["UI Orchestration"]
WS --> BE["GeminiLiveSession"]
BE --> TG["ThalamicGate"]
BE --> TR["ToolRouter"]
BE --> SUM["NeuralSummarizer"]
BE --> AUD["Audio Processing"]
BE --> TLM["Telemetry"]
```

**Diagram sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L65-L485)
- [session.py](file://core/ai/session.py#L1-L922)
- [thalamic.py](file://core/ai/thalamic.py#L1-L122)
- [router.py](file://core/tools/router.py#L1-L360)
- [compression.py](file://core/ai/compression.py#L1-L115)
- [processing.py](file://core/audio/processing.py#L1-L508)
- [telemetry.py](file://core/infra/telemetry.py#L1-L130)

**Section sources**
- [session.py](file://core/ai/session.py#L1-L922)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L1-L485)

## Performance Considerations
- Latency targets: ~300–500ms glass-to-ear; RTT measured via rolling average.
- Barge-in: Instant queue drain to minimize interruption latency.
- DSP backends: Prefer Rust-accelerated aether-cortex when available; otherwise NumPy fallbacks.
- Thalamic Gate: Target < 2ms per frame for latency-sensitive gating.
- Queue sizing: Output queue overflow drops tracked for downstream pressure.

**Section sources**
- [GEMINI.md](file://docs/GEMINI.md#L13-L17)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py#L40-L78)
- [voice_quality_benchmark.py](file://tests/benchmarks/voice_quality_benchmark.py#L717-L766)
- [processing.py](file://core/audio/processing.py#L85-L95)

## Troubleshooting Guide
- Connection failures: Frontend attempts exponential backoff reconnects; logs error and sets status to error.
- Session termination: Structured concurrency raises AISessionExpiredError; backend cleans up ThalamicGate.
- Tool call mismatches: Semantic recovery via vector store; returns available tools and status codes.
- Vision pulse errors: Logged and retried; continues loop on exceptions.

**Section sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L426-L448)
- [session.py](file://core/ai/session.py#L220-L235)
- [router.py](file://core/tools/router.py#L249-L283)
- [session.py](file://core/ai/session.py#L338-L341)

## Conclusion
Aether Voice OS integrates Gemini’s Live API as a native multimodal engine, orchestrating bidirectional audio, vision, and tool-based actions with structured concurrency, proactive perception, empathetic backchannels, and robust telemetry. The backend’s Thalamic Gate and EchoGuard enable near-real-time acoustic decisions, while the frontend’s hooks manage seamless streaming and UI responsiveness.

## Appendices

### Example: Session Configuration
- Build LiveConnectConfig with tools, system instruction, speech_config, and advanced flags.
- Configure voice mapping from soul manifest; enable proactive audio and affective dialog as needed.

**Section sources**
- [session.py](file://core/ai/session.py#L96-L154)

### Example: Error Handling Patterns
- Frontend: exponential backoff reconnects; status transitions; latency measurement resets.
- Backend: structured concurrency exception handling; cleanup on shutdown; usage recording on errors.

**Section sources**
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L426-L448)
- [session.py](file://core/ai/session.py#L220-L235)

### Example: Performance Optimization Techniques
- Use Rust DSP backend when available for zero-crossing and VAD.
- Apply NeuralSummarizer for long sessions to reduce token usage.
- Monitor output queue drops and adjust playback scheduling.

**Section sources**
- [processing.py](file://core/audio/processing.py#L85-L95)
- [compression.py](file://core/ai/compression.py#L108-L115)
- [session.py](file://core/ai/session.py#L426-L455)

### Integration Tests and Benchmarks
- Frontend integration tests validate setup and audio/vision acceptance.
- Backend unit tests verify session config composition and send loop behavior.
- Interrupt latency benchmark ensures queue drain performance.

**Section sources**
- [geminiLive.integration.test.ts](file://apps/portal/src/__tests__/geminiLive.integration.test.ts#L79-L109)
- [geminiLive.integration.test.ts](file://apps/portal/src/__tests__/geminiLive.integration.test.ts#L135-L168)
- [test_gemini_live_session.py](file://tests/unit/test_gemini_live_session.py#L61-L110)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py#L40-L78)