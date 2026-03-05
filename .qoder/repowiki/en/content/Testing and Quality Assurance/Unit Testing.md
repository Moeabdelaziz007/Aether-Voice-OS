# Unit Testing

<cite>
**Referenced Files in This Document**
- [engine.py](file://core/engine.py)
- [audio.py](file://core/logic/managers/audio.py)
- [router.py](file://core/tools/router.py)
- [event_bus.py](file://core/infra/event_bus.py)
- [telemetry.py](file://core/infra/telemetry.py)
- [test_core.py](file://tests/unit/test_core.py)
- [test_audio.py](file://tests/unit/test_audio.py)
- [test_telemetry.py](file://tests/unit/test_telemetry.py)
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py)
- [test_gateway.py](file://tests/unit/test_gateway.py)
- [test_agent_manager.py](file://tests/unit/test_agent_manager.py)
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py)
- [test_spectral.py](file://tests/unit/test_spectral.py)
- [test_vad.py](file://tests/unit/test_vad.py)
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
This document provides comprehensive unit testing guidance for Aether Voice OS. It explains how to test individual components, modules, and functions across the core engine, audio processing, memory systems, and telemetry. It covers testing patterns for asynchronous code, event-driven components, and audio processing functions. It also details mocking strategies for external dependencies (Gemini API, Firebase services, and hardware), test isolation techniques, fixtures, parameterized testing, edge-case validation, and boundary testing. Guidance on test coverage and maintaining high-quality unit tests is included.

## Project Structure
The unit tests are primarily located under tests/unit and exercise core Python modules in core/, including:
- Engine orchestration and lifecycle
- Audio processing and capture/playback
- Tool routing and biometric middleware
- Event bus and telemetry sinks
- Memory tool and Firebase integration
- Gateway transport and WebSocket handshake

```mermaid
graph TB
subgraph "Unit Tests"
UT1["tests/unit/test_core.py"]
UT2["tests/unit/test_audio.py"]
UT3["tests/unit/test_telemetry.py"]
UT4["tests/unit/test_memory_deep.py"]
UT5["tests/unit/test_gateway.py"]
UT6["tests/unit/test_agent_manager.py"]
UT7["tests/unit/test_voice_tool.py"]
UT8["tests/unit/test_spectral.py"]
UT9["tests/unit/test_vad.py"]
end
subgraph "Core Modules"
ENG["core/engine.py"]
AUD["core/logic/managers/audio.py"]
RTR["core/tools/router.py"]
EVT["core/infra/event_bus.py"]
TLM["core/infra/telemetry.py"]
end
UT1 --> ENG
UT2 --> ENG
UT3 --> ENG
UT4 --> ENG
UT5 --> ENG
UT6 --> ENG
UT7 --> ENG
UT8 --> ENG
UT9 --> ENG
ENG --> AUD
ENG --> RTR
ENG --> EVT
ENG --> TLM
```

**Diagram sources**
- [test_core.py](file://tests/unit/test_core.py#L1-L503)
- [test_audio.py](file://tests/unit/test_audio.py#L1-L139)
- [test_telemetry.py](file://tests/unit/test_telemetry.py#L1-L77)
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py#L1-L94)
- [test_gateway.py](file://tests/unit/test_gateway.py#L1-L198)
- [test_agent_manager.py](file://tests/unit/test_agent_manager.py#L1-L93)
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py#L1-L234)
- [test_spectral.py](file://tests/unit/test_spectral.py#L1-L63)
- [test_vad.py](file://tests/unit/test_vad.py#L1-L141)
- [engine.py](file://core/engine.py#L1-L240)
- [audio.py](file://core/logic/managers/audio.py#L1-L98)
- [router.py](file://core/tools/router.py#L1-L360)
- [event_bus.py](file://core/infra/event_bus.py#L1-L152)
- [telemetry.py](file://core/infra/telemetry.py#L1-L130)

**Section sources**
- [test_core.py](file://tests/unit/test_core.py#L1-L503)
- [engine.py](file://core/engine.py#L1-L240)

## Core Components
Key components commonly tested in unit suites:
- AetherEngine: Orchestrator initializing managers, gateway, audio, infrastructure, and admin API; manages lifecycle and async task groups.
- AudioManager: Manages capture, playback, VAD, and paralinguistic analysis; bridges affective data to gateway and event bus.
- ToolRouter: Registers tools, generates declarations, dispatches function calls, applies biometric middleware, and profiles performance.
- EventBus: Tiered event bus with three queues and subscribers; enforces latency budgets and drops expired events.
- TelemetryManager: OpenTelemetry-based sink exporting traces; records usage and cost estimates.

Testing patterns demonstrated:
- Isolation via mocking external libraries and hardware dependencies
- Fixture usage for configuration and shared mocks
- Parameterized tests for edge cases and boundary conditions
- Async fixtures and callbacks for event-driven and audio pipelines
- Assertions on state transitions, counts, and performance metrics

**Section sources**
- [engine.py](file://core/engine.py#L26-L240)
- [audio.py](file://core/logic/managers/audio.py#L18-L98)
- [router.py](file://core/tools/router.py#L120-L360)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [telemetry.py](file://core/infra/telemetry.py#L14-L130)

## Architecture Overview
The unit testing architecture focuses on isolating modules and validating interactions through mocks and fixtures.

```mermaid
sequenceDiagram
participant Test as "Unit Test"
participant Engine as "AetherEngine"
participant Router as "ToolRouter"
participant AudioMgr as "AudioManager"
participant EventBus as "EventBus"
participant Gateway as "AetherGateway"
Test->>Engine : Initialize with mocks
Test->>Engine : _register_tools()
Engine->>Router : register_module(...) for each tool
Test->>Engine : run()
Engine->>AudioMgr : start()
Engine->>Gateway : run()
Engine->>EventBus : start()
Test->>Engine : shutdown_event.set()
Engine->>Engine : _shutdown()
Engine->>AudioMgr : stop()
Engine->>Gateway : stop()
```

**Diagram sources**
- [engine.py](file://core/engine.py#L189-L240)
- [router.py](file://core/tools/router.py#L183-L200)
- [audio.py](file://core/logic/managers/audio.py#L51-L57)
- [event_bus.py](file://core/infra/event_bus.py#L102-L124)

## Detailed Component Analysis

### AetherEngine
- Responsibilities: Initializes managers, registers tools, starts/stops subsystems, coordinates async tasks, and handles shutdown.
- Testing focus:
  - Configuration loading and defaults
  - Tool registration pipeline
  - Async lifecycle and task group coordination
  - Shutdown sequence and cleanup
  - Delegate/handle complex task helpers for ADK runners

```mermaid
flowchart TD
Start(["Engine.run()"]) --> Init["Initialize Managers<br/>and Gateway"]
Init --> Register["Register Tools"]
Register --> StartAudio["Start AudioManager"]
StartAudio --> StartGateway["Start Admin API and Gateway"]
StartGateway --> StartWatchdog["Start Watchdog"]
StartWatchdog --> SpawnTasks["Spawn Core Tasks<br/>EventBus, Pulse, Gateway, Audio"]
SpawnTasks --> WaitShutdown{"Shutdown?"}
WaitShutdown --> |No| SpawnTasks
WaitShutdown --> |Yes| Shutdown["_shutdown(): Stop Audio, Gateway,<br/>Agents, Infra, Admin API"]
Shutdown --> End(["Exit"])
```

**Diagram sources**
- [engine.py](file://core/engine.py#L189-L240)

**Section sources**
- [engine.py](file://core/engine.py#L26-L240)
- [test_core.py](file://tests/unit/test_core.py#L458-L503)

### AudioManager
- Responsibilities: Capture, playback, VAD, paralinguistics; bridges affective data to gateway and event bus.
- Testing focus:
  - Start/stop and task spawning
  - Interrupt and flash interrupt semantics
  - Affective data bridge publishing to EventBus

```mermaid
sequenceDiagram
participant AM as "AudioManager"
participant CAP as "AudioCapture"
participant PB as "AudioPlayback"
participant GW as "Gateway"
participant EB as "EventBus"
AM->>CAP : start()
AM->>PB : start()
AM->>CAP : run() in TaskGroup
AM->>PB : run() in TaskGroup
CAP-->>AM : on_affective_data(features)
AM->>GW : broadcast("affective_score", traits)
AM->>EB : publish(AcousticTraitEvent)
```

**Diagram sources**
- [audio.py](file://core/logic/managers/audio.py#L51-L98)
- [event_bus.py](file://core/infra/event_bus.py#L144-L152)

**Section sources**
- [audio.py](file://core/logic/managers/audio.py#L18-L98)
- [test_telemetry.py](file://tests/unit/test_telemetry.py#L23-L77)

### ToolRouter
- Responsibilities: Tool registration, declarations, dispatch, biometric middleware, performance profiling, semantic recovery.
- Testing focus:
  - Registration of modules and individual tools
  - Dispatch with synchronous and asynchronous handlers
  - Biometric middleware authorization
  - Performance statistics and latency tiers
  - Semantic recovery via vector store

```mermaid
flowchart TD
Reg["register_module(get_tools())"] --> Decl["get_declarations()"]
Decl --> Dispatch["dispatch(FunctionCall)"]
Dispatch --> CheckName{"Tool exists?"}
CheckName --> |No| Recover["Semantic recovery via vector store"]
Recover --> NameMatch{"Match found?"}
NameMatch --> |No| Error["Return error with available tools"]
NameMatch --> |Yes| Exec
CheckName --> |Yes| Exec
Exec --> BioLock{"Sensitive tool?"}
BioLock --> |Yes| Verify["BiometricMiddleware.verify()"]
Verify --> |Denied| BioErr["Return 403 error"]
Verify --> |Authorized| RunHandler["Run handler (sync/async)"]
BioLock --> |No| RunHandler
RunHandler --> Prof["Record duration and update profiler"]
Prof --> Wrap["Wrap result with A2A metadata"]
Wrap --> Done["Return standardized response"]
```

**Diagram sources**
- [router.py](file://core/tools/router.py#L183-L360)

**Section sources**
- [router.py](file://core/tools/router.py#L120-L360)
- [test_core.py](file://tests/unit/test_core.py#L458-L503)
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py#L178-L203)

### EventBus
- Responsibilities: Three-tier queues, subscribers, expiration enforcement, and concurrent routing.
- Testing focus:
  - Publishing to correct queues by event type
  - Worker lanes dropping expired events when configured
  - Concurrent delivery to subscribers

```mermaid
classDiagram
class SystemEvent {
+float timestamp
+string source
+int latency_budget
+is_expired() bool
}
class AudioFrameEvent
class ControlEvent
class TelemetryEvent
class AcousticTraitEvent
class VisionPulseEvent
class EventBus {
+subscribe(event_type, callback)
+publish(event)
+start()
+stop()
-_tier_worker(name, queue, drop_if_expired)
-_route_event(event)
}
SystemEvent <|-- AudioFrameEvent
SystemEvent <|-- ControlEvent
SystemEvent <|-- TelemetryEvent
SystemEvent <|-- AcousticTraitEvent
SystemEvent <|-- VisionPulseEvent
EventBus --> SystemEvent : "publish/route"
```

**Diagram sources**
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)

**Section sources**
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [audio.py](file://core/logic/managers/audio.py#L72-L98)

### TelemetryManager
- Responsibilities: OpenTelemetry initialization, exporter selection, usage recording, and cost estimation.
- Testing focus:
  - Initialization with environment variables
  - Usage recording and span attribute updates
  - No-op fallback on initialization failure

```mermaid
flowchart TD
Init["initialize()"] --> Env["Read ARIZE_* env vars"]
Env --> Provider["Create TracerProvider"]
Provider --> Exporter["Create OTLPSpanExporter"]
Exporter --> Processor["BatchSpanProcessor or SimpleSpanProcessor"]
Processor --> SetTracer["Set tracer and mark initialized"]
SetTracer --> Ready["get_tracer() returns tracer"]
Record["record_usage(session_id, tokens, model)"] --> Cost["Compute cost"]
Cost --> Span["Set gen_ai.* attributes if recording"]
```

**Diagram sources**
- [telemetry.py](file://core/infra/telemetry.py#L35-L130)

**Section sources**
- [telemetry.py](file://core/infra/telemetry.py#L14-L130)

### Audio Processing and DSP
- Focus areas:
  - RingBuffer: wrap-around, overflow, clear, empty reads
  - Zero-crossing detection: crossings at boundaries, no crossings
  - Energy VAD: silence detection, thresholds, result structure
  - Adaptive VAD: baseline adaptation, soft/hard thresholds
  - Spectral coherence and ERLE: signal coherence and echo metrics

```mermaid
flowchart TD
RB["RingBuffer"] --> Write["write(data)"]
Write --> Count["count updated"]
Count --> ReadLast["read_last(n)"]
ReadLast --> Wrap{"Wrapped?"}
Wrap --> |Yes| Circular["Circular read"]
Wrap --> |No| Linear["Linear read"]
VAD["energy_vad(data, threshold)"] --> Result["HyperVADResult"]
Result --> Fields{"Fields present?"}
Fields --> |Yes| Asserts["Assert is_hard/is_soft, energy_rms, sample_count"]
Spectral["SpectralAnalyzer"] --> Coherence["compute_coherence(x,y)"]
Coherence --> High["High coherence for identical signals"]
High --> Low["Lower coherence for unrelated"]
```

**Diagram sources**
- [test_audio.py](file://tests/unit/test_audio.py#L18-L139)
- [test_vad.py](file://tests/unit/test_vad.py#L39-L141)
- [test_spectral.py](file://tests/unit/test_spectral.py#L28-L63)

**Section sources**
- [test_audio.py](file://tests/unit/test_audio.py#L1-L139)
- [test_vad.py](file://tests/unit/test_vad.py#L1-L141)
- [test_spectral.py](file://tests/unit/test_spectral.py#L1-L63)

### Memory Tool and Firebase Integration
- Focus areas:
  - Offline fallback behavior for save/recall/list
  - Priority and tag handling in memory storage
  - Pruning logic targeting priority collections
  - Semantic search using array_contains_any

```mermaid
sequenceDiagram
participant Test as "Unit Test"
participant MT as "memory_tool"
participant FB as "Firebase Connector"
Test->>FB : set_firebase_connector(mock)
Test->>MT : save_memory(key,value,priority,tags)
MT->>FB : doc.set({...}) via mock
Test->>MT : prune_memories(priority="low")
MT->>FB : query.where(...).stream()
FB-->>MT : stream(doc1)
MT->>doc1 : delete()
Test->>MT : semantic_search(tags=["home","iot"])
MT->>FB : where("tags","array_contains_any",...)
```

**Diagram sources**
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py#L24-L94)

**Section sources**
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py#L1-L94)

### Gateway Transport and WebSocket Handshake
- Focus areas:
  - Handshake challenge/response and ACK
  - Heartbeat tick/pong and client pruning
  - Broadcast to multiple clients

```mermaid
sequenceDiagram
participant Client as "WebSocket Client"
participant GW as "AetherGateway"
Client->>GW : Connect ws : //host : port
GW-->>Client : Challenge {challenge}
Client->>GW : Response {client_id, signature, capabilities}
GW-->>Client : ACK {session_id, granted_capabilities}
loop Heartbeat
GW-->>Client : TICK
Client->>GW : PONG
end
GW->>GW : Prune dead clients after max_missed_ticks
GW->>Client : Broadcast {type : "audio_level", payload}
```

**Diagram sources**
- [test_gateway.py](file://tests/unit/test_gateway.py#L83-L198)

**Section sources**
- [test_gateway.py](file://tests/unit/test_gateway.py#L1-L198)

### VoiceTool State Machine and Lifecycle
- Focus areas:
  - State transitions and active state checks
  - Tool declaration structure and required fields
  - Setup/teardown lifecycle and interrupt handling

```mermaid
stateDiagram-v2
[*] --> Idle
Idle --> Initializing : "setup()"
Initializing --> Listening : "start"
Listening --> Processing : "process"
Processing --> Speaking : "respond"
Speaking --> Listening : "interrupt"
Listening --> Stopped : "teardown()"
Stopped --> [*]
```

**Diagram sources**
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py#L43-L85)

**Section sources**
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py#L1-L234)

## Dependency Analysis
Unit tests isolate external dependencies and enforce test boundaries:
- Hardware and system libraries are mocked (e.g., pyaudio) to avoid runtime requirements.
- External services (Firebase, Gemini) are mocked via connectors and environment overrides.
- Async fixtures and callbacks decouple timing-sensitive components.

```mermaid
graph LR
Test["Unit Test"] --> Mocks["Mocked Dependencies"]
Mocks --> Sys["pydantic, numpy, websockets"]
Mocks --> Cloud["firebase_admin, google.genai"]
Mocks --> HW["pyaudio (optional)"]
Test --> Core["core/* modules"]
Core --> |Imports| Sys
Core --> |Optional| HW
```

**Diagram sources**
- [test_agent_manager.py](file://tests/unit/test_agent_manager.py#L7-L47)
- [test_telemetry.py](file://tests/unit/test_telemetry.py#L10-L13)

**Section sources**
- [test_agent_manager.py](file://tests/unit/test_agent_manager.py#L1-L93)
- [test_telemetry.py](file://tests/unit/test_telemetry.py#L1-L77)

## Performance Considerations
- Asynchronous task orchestration: Use fixtures to spin up subsystems and cancel tasks deterministically.
- Event bus throughput: Validate tiered queue behavior and expiration policies.
- ToolRouter dispatch: Measure latency tiers and profile execution times.
- Audio telemetry throttling: Validate rate limiting and callback invocation windows.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Missing external dependencies: Mock modules during import to avoid installation requirements.
- Async teardown failures: Ensure tasks are cancelled and gathered before assertions.
- Gateway handshake timeouts: Adjust heartbeat intervals and timeouts in fixtures.
- Memory tool offline behavior: Verify fallback statuses when Firebase is unavailable.

**Section sources**
- [test_agent_manager.py](file://tests/unit/test_agent_manager.py#L7-L47)
- [test_gateway.py](file://tests/unit/test_gateway.py#L110-L126)
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py#L354-L374)

## Conclusion
Aether Voice OS unit tests emphasize isolation, deterministic behavior, and comprehensive coverage of asynchronous and event-driven paths. By leveraging fixtures, mocks, and targeted assertions, the suite validates core engine orchestration, audio processing correctness, tool routing reliability, and telemetry integrity. Adhering to these patterns ensures maintainable, high-quality unit tests across the platform.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Testing Patterns and Examples
- Configuration and defaults: Validate default configs and environment-driven loading.
- Audio processing: Boundary-value tests for silence, thresholds, and wrap-around behavior.
- Tool declarations: Verify handler presence and function declaration structure.
- Memory tool: Offline fallback, priority/tag handling, pruning, and semantic search queries.
- Gateway: Handshake, heartbeat, and broadcast behaviors.
- VoiceTool: State machine transitions and lifecycle.
- Telemetry: Throttling and usage recording.

**Section sources**
- [test_core.py](file://tests/unit/test_core.py#L28-L503)
- [test_audio.py](file://tests/unit/test_audio.py#L1-L139)
- [test_memory_deep.py](file://tests/unit/test_memory_deep.py#L1-L94)
- [test_gateway.py](file://tests/unit/test_gateway.py#L1-L198)
- [test_voice_tool.py](file://tests/unit/test_voice_tool.py#L1-L234)
- [test_telemetry.py](file://tests/unit/test_telemetry.py#L1-L77)