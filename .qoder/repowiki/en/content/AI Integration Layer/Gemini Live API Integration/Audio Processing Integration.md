# Audio Processing Integration

<cite>
**Referenced Files in This Document**
- [session.py](file://core/ai/session.py)
- [capture.py](file://core/audio/capture.py)
- [playback.py](file://core/audio/playback.py)
- [processing.py](file://core/audio/processing.py)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py)
- [vad.py](file://core/audio/vad.py)
- [state.py](file://core/audio/state.py)
- [state_manager.py](file://core/audio/state_manager.py)
- [thalamic.py](file://core/ai/thalamic.py)
- [telemetry.py](file://core/audio/telemetry.py)
- [audio.py](file://core/logic/managers/audio.py)
- [pcm-processor.js](file://apps/portal/public/pcm-processor.js)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts)
- [test_gemini_live_session.py](file://tests/unit/test_gemini_live_session.py)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py)
- [gemini_live_interactive_benchmark.py](file://tests/gemini_live_interactive_benchmark.py)
- [README.md](file://README.md)
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
This document explains the audio processing integration with the Gemini Live API in Aether Voice OS. It covers the bidirectional audio streaming architecture, the integration with Thalamic Gate V2 for AEC, VAD, and MFCC fingerprinting, audio queue management, real-time PCM handling, latency optimization, interrupt handling for barge-in, audio state monitoring, and telemetry collection for audio quality metrics. The goal is to provide a comprehensive understanding for both technical and non-technical readers.

## Project Structure
The audio pipeline spans several modules:
- AI session orchestration and Gemini Live integration
- Audio capture and preprocessing (AEC, VAD, gating)
- Playback and interruption handling
- State management and telemetry
- Frontend hooks for audio pipeline control and PCM processing

```mermaid
graph TB
subgraph "AI Layer"
S["GeminiLiveSession<br/>Bidirectional Streaming"]
TG["ThalamicGate V2<br/>Affect + Proactive Interventions"]
end
subgraph "Audio Core"
CAP["AudioCapture<br/>C Callback + AEC + VAD"]
AEC["DynamicAEC<br/>GCC-PHAT + NLMS"]
VAD["AdaptiveVAD / VAD Engine"]
PM["Paralinguistic Analyzer"]
SM["SmoothMuter<br/>Graceful Gain Ramps"]
JB["AdaptiveJitterBuffer<br/>Stable AEC Ref"]
end
subgraph "Queues"
INQ["audio_in_queue<br/>PCM Chunks"]
OUTQ["audio_out_queue<br/>Model Audio"]
end
subgraph "Playback"
PB["AudioPlayback<br/>PyAudio + Interruption"]
end
subgraph "State & Telemetry"
AS["AudioState<br/>Global State"]
TL["AudioTelemetryLogger<br/>Per-Frame Metrics"]
end
subgraph "Frontend"
UAP["useAudioPipeline.ts<br/>Interrupt + Stop"]
PCE["pcm-processor.js<br/>Web Worker PCM"]
UGL["useGeminiLive.ts<br/>Session Ready"]
end
S --> INQ
S --> OUTQ
CAP --> INQ
CAP --> AEC
CAP --> VAD
CAP --> PM
CAP --> SM
CAP --> JB
CAP --> AS
CAP --> TL
PB --> OUTQ
PB --> AS
TG --> S
TG --> AS
UAP --> PB
UAP --> CAP
PCE --> CAP
UGL --> S
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L174-L235)
- [capture.py](file://core/audio/capture.py#L193-L510)
- [playback.py](file://core/audio/playback.py#L27-L111)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L490-L780)
- [processing.py](file://core/audio/processing.py#L256-L508)
- [state.py](file://core/audio/state.py#L36-L129)
- [telemetry.py](file://core/audio/telemetry.py#L151-L394)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L247)
- [pcm-processor.js](file://apps/portal/public/pcm-processor.js#L31-L81)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L230-L252)

**Section sources**
- [session.py](file://core/ai/session.py#L1-L120)
- [capture.py](file://core/audio/capture.py#L1-L120)
- [playback.py](file://core/audio/playback.py#L1-L60)
- [README.md](file://README.md#L97-L120)

## Core Components
- GeminiLiveSession: Orchestrates bidirectional audio streaming, integrates Thalamic Gate V2, manages tool calls, and handles interruptions.
- AudioCapture: Microphone capture with C-callback, AEC, VAD, gating, and queue injection.
- AudioPlayback: Speaker output with interruption and resampling for AEC reference.
- DynamicAEC: Adaptive echo cancellation with GCC-PHAT delay estimation, NLMS filtering, double-talk detection, and ERLE computation.
- VAD Engines: AdaptiveVAD and AetherVAD for dual-threshold and hysteresis gating.
- AudioState: Thread-safe singleton for global audio state and AEC telemetry.
- AudioTelemetryLogger: Per-frame metrics and session summaries.
- Frontend Hooks: useAudioPipeline.ts and useGeminiLive.ts coordinate UI and audio pipeline actions.

**Section sources**
- [session.py](file://core/ai/session.py#L43-L155)
- [capture.py](file://core/audio/capture.py#L193-L510)
- [playback.py](file://core/audio/playback.py#L27-L111)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L490-L780)
- [processing.py](file://core/audio/processing.py#L256-L508)
- [state.py](file://core/audio/state.py#L36-L129)
- [telemetry.py](file://core/audio/telemetry.py#L151-L394)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L247)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L230-L252)

## Architecture Overview
The system establishes a bidirectional audio session with Gemini Live:
- Send loop reads PCM chunks from audio_in_queue and sends them to Gemini.
- Receive loop processes model turns, extracts audio, and pushes to audio_out_queue; handles tool calls and interruptions.
- Thalamic Gate V2 monitors audio state and triggers proactive interventions.
- AudioCapture applies DynamicAEC, VAD, and gating in the audio callback to minimize echo and prevent barge-in false positives.
- AudioPlayback consumes audio_out_queue and supports instant interruption.

```mermaid
sequenceDiagram
participant CAP as "AudioCapture"
participant INQ as "audio_in_queue"
participant S as "GeminiLiveSession"
participant GEM as "Gemini Live API"
participant OUTQ as "audio_out_queue"
participant PB as "AudioPlayback"
CAP->>INQ : "Push PCM chunks (AEC + VAD gated)"
S->>INQ : "Send loop reads and sends to Gemini"
GEM-->>S : "Server content with audio parts"
S->>OUTQ : "Put audio bytes"
PB->>OUTQ : "Consume audio for playback"
S->>S : "Handle tool calls / interruptions"
S->>GEM : "Send realtime input (backchannel/intervention)"
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L237-L478)
- [capture.py](file://core/audio/capture.py#L490-L508)
- [playback.py](file://core/audio/playback.py#L101-L111)

**Section sources**
- [session.py](file://core/ai/session.py#L174-L235)
- [capture.py](file://core/audio/capture.py#L329-L510)
- [playback.py](file://core/audio/playback.py#L27-L111)

## Detailed Component Analysis

### Bidirectional Audio Streaming: Send Loop and Receive Loop
- Send loop continuously drains audio_in_queue and sends PCM chunks to Gemini. It logs periodic frame counts and handles closure conditions.
- Receive loop iterates over the live stream, extracts audio parts, broadcasts transcripts, and enqueues audio to audio_out_queue. It handles tool calls in parallel and manages interruptions by draining the output queue and invoking callbacks.

```mermaid
flowchart TD
Start(["Receive Loop"]) --> Next["session.receive()"]
Next --> ForEach["Async for response in turn"]
ForEach --> Usage["Handle usage metadata"]
ForEach --> ToolCall{"tool_call?"}
ToolCall --> |Yes| HandleTool["Dispatch tool calls (parallel)"]
ToolCall --> |No| ModelTurn{"server_content.model_turn?"}
ModelTurn --> |Yes| Parts["Iterate parts"]
Parts --> Text{"part.text?"}
Text --> |Yes| BroadcastTranscript["Broadcast transcript"]
Text --> |No| Audio{"part.inline_data.audio?"}
Audio --> |Yes| EnqueueOut["Enqueue audio bytes<br/>Overflow drop oldest"]
Audio --> |No| Continue["Continue"]
EnqueueOut --> SpeakState["Broadcast engine_state=SPEAKING"]
ModelTurn --> |No| Interrupt{"interrupted?"}
Interrupt --> |Yes| DrainOut["Drain output queue"]
DrainOut --> CallOnInterrupt["Invoke on_interrupt()"]
ForEach --> End(["Loop Continues"])
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L383-L478)

**Section sources**
- [session.py](file://core/ai/session.py#L237-L265)
- [session.py](file://core/ai/session.py#L383-L478)
- [test_gemini_live_session.py](file://tests/unit/test_gemini_live_session.py#L96-L122)

### Thalamic Gate V2 Integration (AEC, VAD, MFCC Fingerprinting)
- ThalamicGate monitors audio_state and triggers proactive interventions based on frustration scoring derived from silence types and RMS.
- AudioCapture applies DynamicAEC in the callback, feeding far-end reference from audio_state.far_end_pcm via a jitter buffer. It updates AEC state and determines whether the user is speaking post-AEC.
- VAD engines compute dual-threshold decisions (soft/hard) and classify silence types to inform backchannel and empathy triggers.

```mermaid
classDiagram
class ThalamicGate {
+start()
+stop()
-_monitor_loop()
-_compute_frustration_score()
-_trigger_intervention()
}
class AudioCapture {
-_callback(...)
-_dynamic_aec : DynamicAEC
-_jitter_buffer : AdaptiveJitterBuffer
-_smooth_muter : SmoothMuter
-_vad : AdaptiveVAD
-_analyzer : SilentAnalyzer
}
class DynamicAEC {
+process_frame(near, far)
+is_user_speaking(chunk)
+update_parameters(...)
}
class AdaptiveVAD {
+update(rms)
}
class AudioState {
+update_aec_state(...)
+set_playing(...)
+far_end_pcm
}
ThalamicGate --> AudioState : "reads"
AudioCapture --> DynamicAEC : "uses"
AudioCapture --> AdaptiveVAD : "uses"
AudioCapture --> AudioState : "updates"
```

**Diagram sources**
- [thalamic.py](file://core/ai/thalamic.py#L11-L122)
- [capture.py](file://core/audio/capture.py#L329-L510)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L490-L780)
- [processing.py](file://core/audio/processing.py#L256-L508)
- [state.py](file://core/audio/state.py#L36-L129)

**Section sources**
- [thalamic.py](file://core/ai/thalamic.py#L25-L80)
- [capture.py](file://core/audio/capture.py#L343-L498)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L579-L780)
- [processing.py](file://core/audio/processing.py#L256-L508)
- [state.py](file://core/audio/state.py#L76-L125)

### Audio Queue Management: audio_in_queue and audio_out_queue
- audio_in_queue: PCM chunks produced by AudioCapture are pushed into this queue. The send loop drains it and sends to Gemini. Overflow protection drops the oldest item when full.
- audio_out_queue: Audio bytes from model responses are enqueued here. AudioPlayback consumes from it. The receive loop enforces overflow by dropping the oldest item when the queue is full, incrementing telemetry counters.

```mermaid
flowchart TD
CAP["AudioCapture"] --> |put_nowait| INQ["audio_in_queue"]
S["Send Loop"] --> |get| INQ
S --> |send_realtime_input| GEM["Gemini"]
GEM --> |audio parts| S
S --> |put_nowait| OUTQ["audio_out_queue"]
PB["AudioPlayback"] --> |get| OUTQ
PB --> |play| SPEAKER["Speaker"]
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L422-L461)
- [capture.py](file://core/audio/capture.py#L490-L498)

**Section sources**
- [session.py](file://core/ai/session.py#L422-L461)
- [capture.py](file://core/audio/capture.py#L298-L328)

### Real-Time Audio Processing Pipeline and PCM Chunk Handling
- AudioCapture’s callback performs:
  - AEC using far-end reference from audio_state.far_end_pcm via AdaptiveJitterBuffer
  - Optional Rust-accelerated spectral denoise
  - SmoothMuter for graceful gain transitions
  - VAD and silence classification
  - Throttled telemetry broadcasting
  - Conditional queue injection based on VAD and gating
- AudioPlayback:
  - Consumes audio_out_queue and writes to speaker via PyAudio callback
  - Supports instant interruption by draining both asyncio and thread-safe queues
  - Resamples AI output to 16 kHz for AEC reference buffer

```mermaid
sequenceDiagram
participant MIC as "Microphone"
participant CAP as "AudioCapture._callback"
participant AEC as "DynamicAEC"
participant JB as "AdaptiveJitterBuffer"
participant AS as "AudioState"
participant Q as "audio_in_queue"
participant S as "Send Loop"
MIC->>CAP : "PCM chunk"
CAP->>AS : "Read far_end_pcm"
CAP->>JB : "Write far-end"
CAP->>AEC : "process_frame(mic, jittered_far)"
AEC-->>CAP : "cleaned_chunk, state"
CAP->>AS : "update_aec_state(...)"
CAP->>Q : "put_nowait PCM if hard speech or not muted"
S->>Q : "get PCM"
S->>GEM : "send_realtime_input"
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L329-L510)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L579-L668)
- [playback.py](file://core/audio/playback.py#L85-L99)

**Section sources**
- [capture.py](file://core/audio/capture.py#L329-L510)
- [playback.py](file://core/audio/playback.py#L85-L111)

### Latency Optimization Techniques
- Direct C-callback injection avoids thread-hop latency.
- AdaptiveJitterBuffer stabilizes far-end reference for AEC convergence.
- SmoothMuter ensures click-free gain transitions.
- Hysteresis gating reduces false positives and abrupt toggles.
- Rust acceleration (aether-cortex) for spectral denoise and VAD.
- Telemetry-driven profiling identifies bottlenecks and optimizes parameters.

**Section sources**
- [capture.py](file://core/audio/capture.py#L38-L191)
- [processing.py](file://core/audio/processing.py#L37-L96)
- [telemetry.py](file://core/audio/telemetry.py#L151-L394)

### Interrupt Handling Mechanism for Barge-In and Output Queue Management
- On interruption, the receive loop drains audio_out_queue to achieve instant silence.
- AudioManager exposes interrupt() and flash_interrupt() to clear pipelines.
- Frontend hook stopPlayback stops active audio sources and resets speaker level.

```mermaid
flowchart TD
User["User Speech / Interrupt"] --> S["Receive Loop"]
S --> Interrupt{"interrupted?"}
Interrupt --> |Yes| Drain["Drain audio_out_queue"]
Drain --> PB["AudioPlayback"]
PB --> |Queue Empty| Silence["Immediate Silence"]
PB --> |Interrupt Hook| AM["AudioManager.interrupt()"]
AM --> FP["Flash Interrupt"]
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L463-L469)
- [audio.py](file://core/logic/managers/audio.py#L63-L71)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L228)

**Section sources**
- [session.py](file://core/ai/session.py#L463-L469)
- [audio.py](file://core/logic/managers/audio.py#L63-L71)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L228)

### Audio State Monitoring and Backchannel Loop Integration
- AudioState maintains is_playing, last_rms, last_zcr, silence_type, and AEC telemetry.
- Backchannel loop monitors silence_type and emits empathetic cues when the user appears to be thinking.
- ThalamicGate computes frustration scores and triggers proactive interventions.

```mermaid
sequenceDiagram
participant AS as "AudioState"
participant BC as "Backchannel Loop"
participant TG as "ThalamicGate"
participant S as "GeminiLiveSession"
AS-->>BC : "silence_type, is_playing"
BC->>S : "send_realtime_input(parts=[text])"
AS-->>TG : "last_rms, is_speaking"
TG->>S : "send_realtime_input(parts=[text])"
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L343-L382)
- [state.py](file://core/audio/state.py#L36-L129)
- [thalamic.py](file://core/ai/thalamic.py#L41-L80)

**Section sources**
- [session.py](file://core/ai/session.py#L343-L382)
- [state.py](file://core/audio/state.py#L36-L129)
- [thalamic.py](file://core/ai/thalamic.py#L41-L80)

### Compression Strategies for Efficient Audio Streaming
- NeuralSummarizer compresses conversation history and working memory into compact semantic seeds for handover contexts, reducing token bloat and optimizing throughput.

**Section sources**
- [compression.py](file://core/ai/compression.py#L24-L115)

### Telemetry Collection for Audio Quality Metrics
- AudioTelemetryLogger captures per-frame metrics (latency, ERLE, convergence, VAD states, queue sizes) and aggregates session metrics with percentiles and jitter analysis.
- AudioTelemetry throttles paralinguistic feature extraction to ~15 Hz for HUD visualization.

**Section sources**
- [telemetry.py](file://core/audio/telemetry.py#L151-L394)
- [telemetry.py](file://core/audio/telemetry.py#L21-L93)

## Dependency Analysis
Key dependencies and relationships:
- GeminiLiveSession depends on audio_in_queue and audio_out_queue for I/O coordination.
- AudioCapture depends on DynamicAEC, AdaptiveVAD, SilentAnalyzer, and SmoothMuter.
- AudioPlayback depends on audio_out_queue and resamples AI output for AEC reference.
- ThalamicGate depends on AudioState and EmotionCalibrator.
- Frontend hooks depend on AudioPlayback and AudioCapture for UI control.

```mermaid
graph LR
S["GeminiLiveSession"] --> INQ["audio_in_queue"]
S --> OUTQ["audio_out_queue"]
CAP["AudioCapture"] --> INQ
CAP --> AEC["DynamicAEC"]
CAP --> VAD["AdaptiveVAD"]
CAP --> SM["SmoothMuter"]
CAP --> JB["AdaptiveJitterBuffer"]
CAP --> AS["AudioState"]
PB["AudioPlayback"] --> OUTQ
PB --> AS
TG["ThalamicGate"] --> AS
UAP["useAudioPipeline.ts"] --> PB
UAP --> CAP
UGL["useGeminiLive.ts"] --> S
```

**Diagram sources**
- [session.py](file://core/ai/session.py#L54-L95)
- [capture.py](file://core/audio/capture.py#L193-L297)
- [playback.py](file://core/audio/playback.py#L27-L49)
- [thalamic.py](file://core/ai/thalamic.py#L11-L40)
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L247)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L230-L252)

**Section sources**
- [session.py](file://core/ai/session.py#L54-L95)
- [capture.py](file://core/audio/capture.py#L193-L297)
- [playback.py](file://core/audio/playback.py#L27-L49)
- [thalamic.py](file://core/ai/thalamic.py#L11-L40)

## Performance Considerations
- Use Rust acceleration (aether-cortex) for VAD and spectral denoise when available.
- Tune AEC parameters (filter length, step size, convergence threshold) for room characteristics.
- Optimize jitter buffer target and max latency to balance smoothness and latency.
- Monitor queue drops and adjust chunk sizes or rates to prevent backpressure.
- Profile end-to-end latency using AudioTelemetryLogger and targeted benchmarks.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and remedies:
- No audio input: Verify microphone permissions and device availability; check AudioDeviceNotFoundError exceptions.
- Echo or poor AEC: Adjust AEC filter length and step size; ensure stable far-end reference via jitter buffer.
- High latency: Reduce queue depths, increase chunk size, or enable Rust acceleration.
- Barge-in false positives: Increase hysteresis thresholds and refine VAD parameters.
- Output queue overflow: Monitor gemini_output_queue_drops and reduce model audio rate or increase playback speed.
- Interrupt latency: Validate flash_interrupt() path and ensure queue draining completes under 50 ms.

**Section sources**
- [capture.py](file://core/audio/capture.py#L511-L565)
- [test_interrupts.py](file://tests/benchmarks/test_interrupts.py#L40-L78)
- [session.py](file://core/ai/session.py#L426-L455)

## Conclusion
Aether Voice OS integrates a high-performance, low-latency audio pipeline with Gemini Live. The bidirectional streaming architecture, Thalamic Gate V2, and robust queue management deliver responsive, empathetic, and efficient real-time audio experiences. Telemetry and benchmarking support continuous optimization and reliability.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Audio Processing Configuration Examples
- Configure AEC parameters (filter length, step size, convergence threshold) via AudioConfig and update at runtime.
- Set chunk size and sample rate aligned with Gemini’s expectations.
- Enable/disable affective dialog and proactive audio based on AIConfig flags.

**Section sources**
- [capture.py](file://core/audio/capture.py#L273-L296)
- [session.py](file://core/ai/session.py#L96-L154)

### Frontend Audio Pipeline Controls
- Use useAudioPipeline.ts to stop playback and clear active sources for immediate barge-in.
- Use useGeminiLive.ts to monitor session readiness and model turns.

**Section sources**
- [useAudioPipeline.ts](file://apps/portal/src/hooks/useAudioPipeline.ts#L214-L247)
- [useGeminiLive.ts](file://apps/portal/src/hooks/useGeminiLive.ts#L230-L252)

### Web Worker PCM Processing
- pcm-processor.js demonstrates ring-buffered PCM accumulation, RMS computation, and zero-copy transfer to main thread.

**Section sources**
- [pcm-processor.js](file://apps/portal/public/pcm-processor.js#L31-L81)

### Interactive Audio Monitoring and Benchmarks
- Interactive benchmark collects metrics for latency, AEC ERLE, convergence, and VAD accuracy.

**Section sources**
- [gemini_live_interactive_benchmark.py](file://tests/gemini_live_interactive_benchmark.py#L469-L500)