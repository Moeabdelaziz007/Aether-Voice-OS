# Adaptive Jitter Buffer and Smooth Muter

<cite>
**Referenced Files in This Document**
- [capture.py](file://core/audio/capture.py)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py)
- [processing.py](file://core/audio/processing.py)
- [state.py](file://core/audio/state.py)
- [config.py](file://core/infra/config.py)
- [telemetry.py](file://core/audio/telemetry.py)
- [test_smooth_muter.py](file://tests/unit/test_smooth_muter.py)
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

## Introduction
This document explains the adaptive jitter buffer and smooth muter components that stabilize audio processing and eliminate artifacts. The adaptive jitter buffer smooths bursty far-end (speaker) audio arrivals to provide a stable reference for acoustic echo cancellation (AEC), preventing convergence loss. The smooth muter applies deterministic, ramp-based gain control to avoid clicks and pops during muting/unmuting transitions. Together, they coordinate with the audio state management system and hardware latency compensation to maintain high-quality voice communication.

## Project Structure
The relevant implementation spans the audio capture pipeline, dynamic AEC, ring buffers, and configuration:
- Adaptive jitter buffer: circular buffer for far-end reference alignment
- Smooth muter: linear-gain ramp with deterministic completion
- Audio state: shared singleton for AEC state and gating decisions
- Dynamic AEC: adaptive echo cancellation with delay estimation and double-talk detection
- Configuration: target/max latency, ramp duration, and latency compensation parameters

```mermaid
graph TB
subgraph "Audio Capture Pipeline"
AC["AudioCapture (_callback)"]
AJB["AdaptiveJitterBuffer"]
SM["SmoothMuter"]
DAE["DynamicAEC"]
end
subgraph "State Management"
AS["AudioState (singleton)"]
HG["HysteresisGate"]
end
subgraph "Configuration"
CFG["AudioConfig"]
end
AC --> AJB
AC --> DAE
AC --> SM
AC --> AS
AC --> HG
CFG --> AC
CFG --> AJB
CFG --> SM
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L38-L105)
- [capture.py](file://core/audio/capture.py#L106-L191)
- [capture.py](file://core/audio/capture.py#L193-L510)
- [state.py](file://core/audio/state.py#L36-L129)
- [config.py](file://core/infra/config.py#L11-L44)

**Section sources**
- [capture.py](file://core/audio/capture.py#L38-L105)
- [capture.py](file://core/audio/capture.py#L106-L191)
- [capture.py](file://core/audio/capture.py#L193-L510)
- [state.py](file://core/audio/state.py#L36-L129)
- [config.py](file://core/infra/config.py#L11-L44)

## Core Components
- AdaptiveJitterBuffer: circular buffer for far-end PCM aligned to the capture chunk size, enabling stable AEC reference and preventing convergence loss.
- SmoothMuter: linear-gain ramp generator that ensures continuous amplitude envelopes across chunk boundaries, eliminating clicks/pops.
- AudioState: thread-safe singleton tracking playback state, AEC metrics, and gating decisions.
- DynamicAEC: adaptive echo cancellation with GCC-PHAT delay estimation, frequency-domain NLMS filtering, and double-talk detection.
- Configuration: defines target/max jitter buffer latency, ramp duration, and hardware latency compensation.

**Section sources**
- [capture.py](file://core/audio/capture.py#L38-L105)
- [capture.py](file://core/audio/capture.py#L106-L191)
- [state.py](file://core/audio/state.py#L36-L129)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L490-L779)
- [config.py](file://core/infra/config.py#L11-L44)

## Architecture Overview
The capture callback integrates jitter buffering, AEC, hysteresis gating, and smooth muting. The far-end reference is written into the jitter buffer and read back aligned to the current chunk size. The AEC cleans the microphone signal using the aligned far-end reference. A hysteresis gate decides whether to mute based on AI playback state and user speech detection. The smooth muter applies a linear gain ramp to avoid transients. Hardware latency compensation adds guard times for mute/unmute transitions.

```mermaid
sequenceDiagram
participant MIC as "Microphone"
participant ACB as "AudioCapture._callback"
participant AJB as "AdaptiveJitterBuffer"
participant DAE as "DynamicAEC"
participant HG as "HysteresisGate"
participant SM as "SmoothMuter"
participant AS as "AudioState"
MIC->>ACB : "PCM chunk"
ACB->>AJB : "Write far-end PCM"
ACB->>AJB : "Read aligned far-end"
ACB->>DAE : "Clean with far-end"
DAE-->>ACB : "Cleaned chunk + AEC state"
ACB->>HG : "Update with AS.is_playing"
ACB->>ACB : "Decide should_mute"
ACB->>SM : "mute()/unmute()"
SM-->>ACB : "Ramped chunk"
ACB->>AS : "Update AEC state, RMS, ZCR"
ACB-->>MIC : "Optional : enqueue processed chunk"
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L329-L509)
- [capture.py](file://core/audio/capture.py#L106-L191)
- [state.py](file://core/audio/state.py#L13-L34)

**Section sources**
- [capture.py](file://core/audio/capture.py#L329-L509)
- [state.py](file://core/audio/state.py#L13-L34)

## Detailed Component Analysis

### Adaptive Jitter Buffer
Purpose:
- Stabilize far-end reference arrivals to prevent AEC convergence loss caused by bursty or misaligned audio.
- Provide a controlled latency budget via target and maximum latency settings.

Key behaviors:
- Circular buffer with separate read/write indices and size tracking.
- Writes handle wrap-around and overruns; reads return zero-padding on underrun.
- Maintains a fixed capacity to bound memory and latency.

Target and maximum latency:
- Configurable in samples derived from milliseconds and sample rate.
- Target latency sets the desired steady-state depth; maximum latency caps worst-case drift.

Integration:
- Capture writes newly received far-end PCM to the buffer.
- Capture reads exactly the current chunk size for AEC processing.

```mermaid
flowchart TD
Start(["Write/Read Entry"]) --> CheckLen["Check data length"]
CheckLen --> |Empty| Exit["Return"]
CheckLen --> |Non-empty| CalcEnd["Compute end index"]
CalcEnd --> WrapCheck{"Wrap around?"}
WrapCheck --> |No| CopyInline["Copy to buffer slice"]
WrapCheck --> |Yes| SplitCopy["Copy first part<br/>then second part"]
CopyInline --> UpdatePos["Update write/read index and size"]
SplitCopy --> UpdatePos
UpdatePos --> Done(["Exit"])
%% Read path
ReadStart(["Read Entry"]) --> SizeCheck{"Size > 0?"}
SizeCheck --> |No| ZeroPad["Return zero-padded output"]
SizeCheck --> |Yes| ReadLen["Compute read length"]
ReadLen --> ReadWrap{"Wrap around?"}
ReadWrap --> |No| ReadInline["Read from buffer slice"]
ReadWrap --> |Yes| ReadSplit["Read first part<br/>then second part"]
ReadInline --> UpdateRead["Update read index and size"]
ReadSplit --> UpdateRead
UpdateRead --> ReadDone(["Exit"])
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L58-L104)

**Section sources**
- [capture.py](file://core/audio/capture.py#L38-L105)
- [config.py](file://core/infra/config.py#L37-L43)

### Smooth Muter
Purpose:
- Eliminate clicks/pops during muting/unmuting by applying a smooth, deterministic linear gain ramp.
- Maintain continuity across chunk boundaries with minimal allocations and branching.

Linear ramp generation:
- Computes remaining ramp samples based on a fixed ramp length in samples for a full 0→1 or 1→0 transition.
- Uses a linear segment over the chunk, then holds at the target or carries forward the last gain.
- Ensures deterministic completion: the ramp lands exactly on the target gain.

Fast-path optimizations:
- If current and target gain are equal, returns a copy or zero-filled buffer when appropriate.
- Avoids unnecessary allocations by generating gains inline and casting once.

```mermaid
flowchart TD
Enter(["process(pcm_chunk)"]) --> EmptyCheck{"Chunk empty?"}
EmptyCheck --> |Yes| ReturnOrig["Return original chunk"]
EmptyCheck --> |No| GainEq{"current == target?"}
GainEq --> |Yes| CurOne{"current == 1.0?"}
CurOne --> |Yes| ReturnCopy["Return chunk copy"]
CurOne --> |No| CurZero{"current == 0.0?"}
CurZero --> |Yes| ReturnZero["Return zeros-like"]
CurZero --> |No| ScaleOnce["Scale once and cast"]
GainEq --> |No| ComputeRem["Compute remaining ramp samples"]
ComputeRem --> RemainingGT0{"remaining > 0?"}
RemainingGT0 --> |No| SetTarget["Set current = target<br/>use full chunk gains"]
RemainingGT0 --> |Yes| RampLen["ramp_len = min(chunk, remaining)"]
RampLen --> Linspace["Generate ramp with linspace"]
Linspace --> RampDone{"Ramp completes in chunk?"}
RampDone --> |Yes| HoldTarget["Hold at target<br/>set current=target"]
RampDone --> |No| HoldLast["Hold at last gain<br/>keep partial ramp"]
HoldTarget --> ApplyGain["Scale chunk by gains"]
HoldLast --> ApplyGain
ScaleOnce --> ApplyGain
ReturnOrig --> Exit(["Exit"])
ReturnCopy --> Exit
ReturnZero --> Exit
SetTarget --> ApplyGain
ApplyGain --> Exit
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L125-L182)

**Section sources**
- [capture.py](file://core/audio/capture.py#L106-L191)
- [test_smooth_muter.py](file://tests/unit/test_smooth_muter.py#L102-L134)

### Audio State Management and Hysteresis Gate
Role:
- Provides a thread-safe singleton for global audio state, including AEC metrics and playback flags.
- Hysteresis gate prevents rapid toggling of mute decisions, reducing transient clicks.

Integration:
- Capture callback updates AEC state and RMS/ZCR for downstream logic.
- Hysteresis gate consumes the global playback flag to compute a stable mute decision.

```mermaid
classDiagram
class AudioState {
+bool is_playing
+bool just_started_playing
+bool just_stopped_playing
+float last_rms
+float last_zcr
+dict get_aec_state()
+update_aec_state(...)
+set_playing(playing)
}
class HysteresisGate {
-bool _mute_state
-float _mute_confidence
+update(is_playing) bool
}
AudioState <.. HysteresisGate : "consumes is_playing"
```

**Diagram sources**
- [state.py](file://core/audio/state.py#L36-L129)

**Section sources**
- [state.py](file://core/audio/state.py#L13-L34)
- [state.py](file://core/audio/state.py#L36-L129)
- [capture.py](file://core/audio/capture.py#L387-L419)

### Dynamic AEC Integration
Role:
- Implements adaptive echo cancellation with GCC-PHAT delay estimation, frequency-domain NLMS filtering, and double-talk detection.
- Provides AEC state used by the audio state singleton and capture logic.

Integration:
- Capture reads aligned far-end PCM from the jitter buffer and supplies it to AEC alongside the microphone chunk.
- AEC state updates are broadcast to the audio state singleton for monitoring and gating decisions.

```mermaid
sequenceDiagram
participant ACB as "AudioCapture._callback"
participant AJB as "AdaptiveJitterBuffer"
participant DAE as "DynamicAEC"
participant AS as "AudioState"
ACB->>AJB : "write(far_end)"
ACB->>AJB : "read(chunk_size)"
AJB-->>ACB : "aligned far_end"
ACB->>DAE : "process_frame(near=microphone, far=aligned)"
DAE-->>ACB : "cleaned, AECState"
ACB->>AS : "update_aec_state(...)"
```

**Diagram sources**
- [capture.py](file://core/audio/capture.py#L344-L373)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L579-L668)

**Section sources**
- [capture.py](file://core/audio/capture.py#L344-L373)
- [dynamic_aec.py](file://core/audio/dynamic_aec.py#L490-L779)

## Dependency Analysis
- AudioCapture depends on AdaptiveJitterBuffer for stable far-end alignment, DynamicAEC for echo cancellation, SmoothMuter for artifact-free transitions, and AudioState for gating and telemetry.
- Configuration drives jitter buffer latency targets, ramp duration, and hardware latency compensation.
- Telemetry logs frame-level metrics for latency, AEC performance, and VAD outcomes.

```mermaid
graph LR
CFG["AudioConfig"] --> ACB["AudioCapture"]
ACB --> AJB["AdaptiveJitterBuffer"]
ACB --> DAE["DynamicAEC"]
ACB --> SM["SmoothMuter"]
ACB --> AS["AudioState"]
ACB --> TL["AudioTelemetryLogger"]
```

**Diagram sources**
- [config.py](file://core/infra/config.py#L11-L44)
- [capture.py](file://core/audio/capture.py#L202-L267)
- [telemetry.py](file://core/audio/telemetry.py#L151-L276)

**Section sources**
- [config.py](file://core/infra/config.py#L11-L44)
- [capture.py](file://core/audio/capture.py#L202-L267)
- [telemetry.py](file://core/audio/telemetry.py#L151-L276)

## Performance Considerations
- Jitter buffer memory footprint is proportional to maximum latency in samples; choose maximum latency to balance stability and memory usage.
- Smooth muter uses vectorized ramp generation and fast-path branches to minimize CPU overhead per callback.
- Dynamic AEC uses frequency-domain processing with overlap-save; filter length and step size impact convergence speed and computational load.
- Hysteresis gate reduces unnecessary muting transitions, improving perceived audio quality and reducing transients.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Audio artifacts during muting/unmuting:
  - Verify ramp duration is sufficient for the chunk size; ensure deterministic completion.
  - Confirm that the ramp is applied consistently across chunk boundaries.
- AEC convergence problems:
  - Check jitter buffer alignment; misalignment can degrade echo cancellation.
  - Monitor AEC ERLE and convergence progress via audio state.
- Buffer under/overflow symptoms:
  - Inspect jitter buffer read/write indices and size; ensure writes do not exceed capacity.
  - Adjust target latency to match typical far-end arrival patterns.
- Performance bottlenecks:
  - Use telemetry to identify latency spikes and frame drops.
  - Tune AEC parameters (step size, filter length) and VAD thresholds.

**Section sources**
- [capture.py](file://core/audio/capture.py#L38-L105)
- [capture.py](file://core/audio/capture.py#L125-L182)
- [state.py](file://core/audio/state.py#L76-L109)
- [telemetry.py](file://core/audio/telemetry.py#L203-L276)

## Conclusion
The adaptive jitter buffer and smooth muter form a robust foundation for stable, artifact-free audio processing. The jitter buffer ensures a consistent far-end reference for AEC, while the smooth muter guarantees seamless transitions without clicks. Combined with hysteresis gating, hardware latency compensation, and comprehensive telemetry, the system maintains high fidelity and responsiveness across diverse audio conditions.