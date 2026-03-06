# Tool Execution System

<cite>
**Referenced Files in This Document**
- [engine.py](file://core/engine.py)
- [server.py](file://core/server.py)
- [router.py](file://core/tools/router.py)
- [system_tool.py](file://core/tools/system_tool.py)
- [memory_tool.py](file://core/tools/memory_tool.py)
- [vision_tool.py](file://core/tools/vision_tool.py)
- [tasks_tool.py](file://core/tools/tasks_tool.py)
- [hive_tool.py](file://core/tools/hive_tool.py)
- [camera_tool.py](file://core/tools/camera_tool.py)
- [hive_memory.py](file://core/tools/hive_memory.py)
- [voice_auth.py](file://core/tools/voice_auth.py)
- [scheduler.py](file://core/ai/scheduler.py)
- [vector_store.py](file://core/tools/vector_store.py)
- [security.py](file://core/utils/security.py)
- [router.py](file://core/ai/router.py)
</cite>

## Update Summary
**Changes Made**
- Updated tool registration system to reflect 12 registered modules (expanded from 9)
- Added documentation for new camera_tool, hive_memory, and voice_auth tools
- Enhanced biometric middleware integration documentation
- Updated tool categories and parameter schemas to include new tools
- Expanded security considerations for voice authentication

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
This document describes the Tool Execution System powering the Aether Voice OS neural dispatcher. It explains the Neural Router architecture, function declaration patterns, and the execution pipeline with biometric middleware. It covers tool registration, parameter validation, parallel execution via asyncio TaskGroup, tool categories (system, memory, vision, task automation, camera, hive memory, voice authentication), scheduling and priority management, result processing, multimodal injection, and security considerations including Soul-Lock verification. Guidance is included for building custom tools and optimizing performance.

## Project Structure
The Tool Execution System spans several modules:
- Engine orchestration initializes managers, registers tools, and runs the system with parallel tasks.
- Tool router handles function declarations, dispatching, biometric middleware, and performance profiling.
- Individual tool modules define handlers and schemas for system, memory, vision, tasks, hive coordination, camera capture, collective memory, and voice authentication.
- Vector store enables semantic recovery and indexing.
- Scheduler coordinates proactive speculation and temporal memory.
- Security utilities support cryptographic primitives.

```mermaid
graph TB
subgraph "Runtime"
Engine["AetherEngine<br/>core/engine.py"]
Server["Entry Point<br/>core/server.py"]
end
subgraph "AI"
Scheduler["CognitiveScheduler<br/>core/ai/scheduler.py"]
IntRouter["IntelligenceRouter<br/>core/ai/router.py"]
end
subgraph "Tools"
TRouter["ToolRouter<br/>core/tools/router.py"]
Sys["System Tool<br/>core/tools/system_tool.py"]
Mem["Memory Tool<br/>core/tools/memory_tool.py"]
Vision["Vision Tool<br/>core/tools/vision_tool.py"]
Tasks["Tasks Tool<br/>core/tools/tasks_tool.py"]
Hive["Hive Tool<br/>core/tools/hive_tool.py"]
Camera["Camera Tool<br/>core/tools/camera_tool.py"]
HiveMem["Hive Memory<br/>core/tools/hive_memory.py"]
VoiceAuth["Voice Auth<br/>core/tools/voice_auth.py"]
end
subgraph "Infra"
VS["LocalVectorStore<br/>core/tools/vector_store.py"]
Sec["Security Utils<br/>core/utils/security.py"]
end
Server --> Engine
Engine --> TRouter
Engine --> Scheduler
Engine --> Sys
Engine --> Mem
Engine --> Vision
Engine --> Tasks
Engine --> Hive
Engine --> Camera
Engine --> HiveMem
Engine --> VoiceAuth
TRouter --> VS
TRouter --> Sec
Scheduler --> TRouter
IntRouter --> Engine
```

**Diagram sources**
- [engine.py](file://core/engine.py#L26-L240)
- [server.py](file://core/server.py#L105-L149)
- [router.py](file://core/tools/router.py#L120-L360)
- [system_tool.py](file://core/tools/system_tool.py#L198-L310)
- [memory_tool.py](file://core/tools/memory_tool.py#L246-L330)
- [vision_tool.py](file://core/tools/vision_tool.py#L58-L75)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L216-L325)
- [hive_tool.py](file://core/tools/hive_tool.py#L51-L78)
- [camera_tool.py](file://core/tools/camera_tool.py#L53-L65)
- [hive_memory.py](file://core/tools/hive_memory.py#L89-L122)
- [voice_auth.py](file://core/tools/voice_auth.py#L97-L111)
- [scheduler.py](file://core/ai/scheduler.py#L10-L114)
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [security.py](file://core/utils/security.py#L18-L71)

**Section sources**
- [engine.py](file://core/engine.py#L26-L240)
- [server.py](file://core/server.py#L105-L149)

## Core Components
- AetherEngine: Initializes managers, registers tools, and runs the system with parallel tasks using asyncio TaskGroup.
- ToolRouter: Central dispatcher that generates function declarations, routes tool calls, applies biometric middleware, and records performance metrics.
- Tool Modules: Provide handlers and JSON Schema parameter definitions for system, memory, vision, tasks, hive coordination, camera capture, collective memory, and voice authentication.
- LocalVectorStore: Lightweight semantic index for tool name recovery and metadata storage.
- CognitiveScheduler: Proactive speculation, overlap buffering, and echo generation to manage cognitive load and responsiveness.
- Security Utilities: Ed25519 signature verification and keypair generation for cryptographic operations.

**Section sources**
- [engine.py](file://core/engine.py#L26-L240)
- [router.py](file://core/tools/router.py#L120-L360)
- [system_tool.py](file://core/tools/system_tool.py#L198-L310)
- [memory_tool.py](file://core/tools/memory_tool.py#L246-L330)
- [vision_tool.py](file://core/tools/vision_tool.py#L58-L75)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L216-L325)
- [hive_tool.py](file://core/tools/hive_tool.py#L51-L78)
- [camera_tool.py](file://core/tools/camera_tool.py#L16-L65)
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L122)
- [voice_auth.py](file://core/tools/voice_auth.py#L20-L111)
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [scheduler.py](file://core/ai/scheduler.py#L10-L114)
- [security.py](file://core/utils/security.py#L18-L71)

## Architecture Overview
The system integrates a neural dispatcher with biometric middleware and a scheduler to coordinate tool execution. The engine registers tool modules, initializes a vector store for semantic indexing, and runs parallel subsystems. Tool calls are dispatched to handlers with standardized response wrapping and A2A metadata.

```mermaid
sequenceDiagram
participant User as "User"
participant Engine as "AetherEngine"
participant Router as "ToolRouter"
participant Handler as "Tool Handler"
participant VS as "LocalVectorStore"
participant Sec as "BiometricMiddleware"
User->>Engine : "Invoke tool call"
Engine->>Router : "dispatch(function_call)"
Router->>Router : "Resolve tool name"
alt Semantic recovery enabled
Router->>VS : "embed query + search"
VS-->>Router : "nearest tool"
end
Router->>Sec : "verify(tool_name, context)"
Sec-->>Router : "authorized?"
alt Not authorized
Router-->>Engine : "error 403"
else Authorized
Router->>Handler : "invoke handler(**args)"
Handler-->>Router : "result"
Router-->>Engine : "wrapped result + A2A metadata"
end
```

**Diagram sources**
- [engine.py](file://core/engine.py#L189-L240)
- [router.py](file://core/tools/router.py#L234-L360)
- [vector_store.py](file://core/tools/vector_store.py#L66-L112)

## Detailed Component Analysis

### Neural Router and Biometric Middleware
The ToolRouter centralizes tool registration, function declaration generation, dispatching, and performance tracking. It supports:
- Registration via decorator-like definitions or module discovery.
- Biometric middleware enforcement for sensitive tools.
- Semantic recovery using a local vector store.
- A2A response wrapping with latency tier, idempotency, and status codes.

```mermaid
classDiagram
class ToolRouter {
+register(name, description, parameters, handler, latency_tier, idempotent)
+register_module(module)
+un_register(name)
+get_declarations() list
+dispatch(function_call) dict
+get_performance_report() dict
}
class ToolRegistration {
+string name
+string description
+dict parameters
+Callable handler
+string latency_tier
+bool idempotent
+bool requires_biometric
}
class BiometricMiddleware {
+verify(tool_name, context) bool
}
class ToolExecutionProfiler {
+record(tool_name, duration) void
+get_stats(tool_name) dict
}
ToolRouter --> ToolRegistration : "manages"
ToolRouter --> BiometricMiddleware : "uses"
ToolRouter --> ToolExecutionProfiler : "uses"
```

**Diagram sources**
- [router.py](file://core/tools/router.py#L120-L360)

**Section sources**
- [router.py](file://core/tools/router.py#L120-L360)

### Tool Categories and Parameter Schemas

#### System Tools
- Purpose: Host-local actions for time, system info, timers, safe terminal commands, codebase listing, and file reading.
- Validation: Required fields enforced via JSON Schema; safety measures include command blacklists and timeouts.
- Examples: get_current_time, get_system_info, run_timer, run_terminal_command, list_codebase, read_file_content.

```mermaid
flowchart TD
Start(["System Tool Entry"]) --> Validate["Validate parameters via JSON Schema"]
Validate --> Allowed{"Command allowed?"}
Allowed --> |No| Block["Return blocked error"]
Allowed --> |Yes| Exec["Execute with timeout and isolation"]
Exec --> Return["Return stdout/stderr/return_code"]
Block --> End(["Exit"])
Return --> End
```

**Diagram sources**
- [system_tool.py](file://core/tools/system_tool.py#L87-L135)

**Section sources**
- [system_tool.py](file://core/tools/system_tool.py#L198-L310)

#### Memory Tools
- Purpose: Persistent memory persistence and recall using Firestore; graceful offline fallback.
- Validation: Enumerated priorities; required keys enforced.
- Operations: save_memory, recall_memory, list_memories, semantic_search, prune_memories.

```mermaid
flowchart TD
Start(["Memory Tool Entry"]) --> DBCheck{"Firebase connected?"}
DBCheck --> |No| Local["Return local-only fallback"]
DBCheck --> |Yes| Write["Write/Read via Firestore"]
Write --> Return["Return structured result"]
Local --> End(["Exit"])
Return --> End
```

**Diagram sources**
- [memory_tool.py](file://core/tools/memory_tool.py#L40-L93)
- [memory_tool.py](file://core/tools/memory_tool.py#L131-L170)

**Section sources**
- [memory_tool.py](file://core/tools/memory_tool.py#L246-L330)

#### Vision Tools
- Purpose: Desktop screenshot capture and multimodal injection.
- Validation: No parameters required; returns MIME type and Base64-encoded image.
- Integration: Result can be injected into the multimodal session context.

```mermaid
sequenceDiagram
participant Vision as "Vision Tool"
participant MSS as "mss"
Vision->>MSS : "grab(monitor)"
MSS-->>Vision : "raw pixels"
Vision->>Vision : "convert to PNG bytes"
Vision->>Vision : "base64 encode"
Vision-->>Vision : "return {status, mime_type, data}"
```

**Diagram sources**
- [vision_tool.py](file://core/tools/vision_tool.py#L19-L55)

**Section sources**
- [vision_tool.py](file://core/tools/vision_tool.py#L58-L75)

#### Task Automation Tools
- Purpose: Task and note persistence via Firestore with graceful fallback.
- Validation: Required fields enforced; enums for priority/status.
- Operations: create_task, list_tasks, complete_task, add_note.

```mermaid
flowchart TD
Start(["Task Tool Entry"]) --> DBCheck{"Firebase connected?"}
DBCheck --> |No| ReturnOffline["Return offline-friendly result"]
DBCheck --> |Yes| CRUD["Firestore CRUD operation"]
CRUD --> Return["Return structured result"]
ReturnOffline --> End(["Exit"])
Return --> End
```

**Diagram sources**
- [tasks_tool.py](file://core/tools/tasks_tool.py#L43-L87)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L140-L181)

**Section sources**
- [tasks_tool.py](file://core/tools/tasks_tool.py#L216-L325)

#### Hive Coordination Tools
- Purpose: Trigger Hive handovers and expert switching.
- Validation: Required target and reason fields.
- Operation: switch_expert_soul.

```mermaid
flowchart TD
Start(["Hive Tool Entry"]) --> Check{"Hive Coordinator ready?"}
Check --> |No| Error["Return initialization error"]
Check --> |Yes| Handoff["Request handoff to target soul"]
Handoff --> Result{"Success?"}
Result --> |Yes| Ok["Return success"]
Result --> |No| Fail["Return failure"]
Error --> End(["Exit"])
Ok --> End
Fail --> End
```

**Diagram sources**
- [hive_tool.py](file://core/tools/hive_tool.py#L27-L49)

**Section sources**
- [hive_tool.py](file://core/tools/hive_tool.py#L51-L78)

#### Camera Tools
- Purpose: Capture real-time frames from the user's camera for Spatio-Temporal Grounding.
- Validation: No parameters required; returns JPEG bytes for immediate processing.
- Integration: Provides visual feedback during hard interrupts and user interaction analysis.

```mermaid
flowchart TD
Start(["Camera Tool Entry"]) --> Open["Open camera device"]
Open --> Capture["Capture single frame"]
Capture --> Encode["Encode as JPEG (70 quality)"]
Encode --> Return["Return JPEG bytes"]
Open --> Error["Return None on failure"]
Error --> End(["Exit"])
Return --> End
```

**Diagram sources**
- [camera_tool.py](file://core/tools/camera_tool.py#L20-L47)

**Section sources**
- [camera_tool.py](file://core/tools/camera_tool.py#L16-L65)

#### Hive Memory Tools
- Purpose: Provide shared collective memory persistence across expert souls during handoffs.
- Validation: Key-value pairs with optional tags; required keys enforced.
- Operations: write_memory, read_memory with consistent envelope structure.

```mermaid
flowchart TD
Start(["Hive Memory Entry"]) --> DBCheck{"Firebase connected?"}
DBCheck --> |No| Offline["Return offline error"]
DBCheck --> |Yes| Access["Access hive_memory collection"]
Access --> Write{"Operation Type?"}
Write --> |Write| Store["Store with timestamp and session_id"]
Store --> Success["Return success"]
Write --> |Read| Retrieve["Retrieve document"]
Retrieve --> Found{"Document exists?"}
Found --> |Yes| ReturnData["Return data envelope"]
Found --> |No| NotFound["Return not_found with value=None"]
Offline --> End(["Exit"])
Success --> End
ReturnData --> End
NotFound --> End
```

**Diagram sources**
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L86)

**Section sources**
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L122)

#### Voice Authentication Tools
- Purpose: Biometric voice authentication for secure tool execution with calibration capabilities.
- Validation: No parameters required for verification; calibration validates audio state.
- Operations: verify_admin, calibrate_admin_voice with pitch-based authentication.

```mermaid
flowchart TD
Start(["Voice Auth Entry"]) --> Presence{"Audio detected?"}
Presence --> |No| Denied["Return denied (no presence)"]
Presence --> |Yes| Calibrated{"System calibrated?"}
Calibrated --> |No| DefaultRange["Check default pitch range (100-180Hz)"]
Calibrated --> |Yes| Compare["Compare against calibrated window"]
DefaultRange --> Authorized{"Within default range?"}
Authorized --> |Yes| Success["Return authorized"]
Authorized --> |No| Denied
Compare --> Within{"Within calibration window?"}
Within --> |Yes| Success
Within --> |No| Denied
Denied --> End(["Exit"])
Success --> End
```

**Diagram sources**
- [voice_auth.py](file://core/tools/voice_auth.py#L27-L51)

**Section sources**
- [voice_auth.py](file://core/tools/voice_auth.py#L20-L111)

### Tool Registration and Discovery
- Module-level get_tools(): Returns a list of tool definitions with name, description, parameters (JSON Schema), and handler.
- ToolRouter.register_module(): Iterates module definitions and registers each tool.
- ToolRouter.register(): Registers a single tool with A2A metadata (latency tier, idempotency).
- **Updated**: Engine now registers 12 tools in total: system_tool, tasks_tool, memory_tool, voice_tool, voice_auth, vision_tool, camera_tool, hive_tool, hive_memory, rag_tool, discovery_tool, context_scraper.

```mermaid
sequenceDiagram
participant Engine as "AetherEngine"
participant TR as "ToolRouter"
participant Mod as "Tool Module"
Engine->>TR : "register_module(system_tool)"
TR->>Mod : "get_tools()"
Mod-->>TR : "list of tool defs"
loop For each tool
TR->>TR : "register(name, description, parameters, handler, ...)"
end
Note over Engine,TR : Now registers 12 total tools including camera_tool, hive_memory, voice_auth
```

**Diagram sources**
- [engine.py](file://core/engine.py#L150-L194)
- [router.py](file://core/tools/router.py#L183-L200)
- [system_tool.py](file://core/tools/system_tool.py#L205-L310)
- [memory_tool.py](file://core/tools/memory_tool.py#L246-L330)
- [vision_tool.py](file://core/tools/vision_tool.py#L58-L75)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L216-L325)
- [hive_tool.py](file://core/tools/hive_tool.py#L51-L78)
- [camera_tool.py](file://core/tools/camera_tool.py#L53-L65)
- [hive_memory.py](file://core/tools/hive_memory.py#L89-L122)
- [voice_auth.py](file://core/tools/voice_auth.py#L97-L111)

**Section sources**
- [engine.py](file://core/engine.py#L150-L194)
- [router.py](file://core/tools/router.py#L183-L200)

### Execution Pipeline and Parallelism
- Engine.run(): Starts the event bus, gateway, audio, and admin loops concurrently using asyncio TaskGroup.
- ToolRouter.dispatch(): Supports both sync and async handlers; wraps results with A2A metadata and records latency.

```mermaid
sequenceDiagram
participant Engine as "AetherEngine"
participant TG as "TaskGroup"
participant Bus as "EventBus"
participant GW as "Gateway"
participant Aud as "AudioManager"
participant TR as "ToolRouter"
Engine->>TG : "create_task(event-bus)"
Engine->>TG : "create_task(pulse-heartbeat)"
Engine->>TG : "create_task(gateway)"
Engine->>TG : "audio.run_tasks(tg)"
Engine->>TG : "create_task(admin_sync)"
TG-->>Engine : "parallel execution"
Engine->>TR : "dispatch(tool_call)"
```

**Diagram sources**
- [engine.py](file://core/engine.py#L189-L225)
- [router.py](file://core/tools/router.py#L234-L360)

**Section sources**
- [engine.py](file://core/engine.py#L189-L225)
- [router.py](file://core/tools/router.py#L234-L360)

### Biometric Middleware and Soul-Lock Verification
- BiometricMiddleware.verify(): Enforces biometric "Soul-Lock" verification using a context flag; supports a development fallback.
- SENSITIVE_TOOLS: A curated set of tools requiring biometric verification.
- **Enhanced**: Voice authentication tools integrate with the biometric middleware system for secure execution.
- Integration: ToolRouter.dispatch() checks if a tool is sensitive and invokes middleware before execution.

```mermaid
flowchart TD
Start(["Dispatch Tool"]) --> Check{"Sensitive tool?"}
Check --> |No| Run["Run handler"]
Check --> |Yes| Verify["BiometricMiddleware.verify()"]
Verify --> |Authorized| Run
Verify --> |Unauthorized| Deny["Return 403 error"]
Run --> Wrap["Wrap result + A2A metadata"]
Deny --> End(["Exit"])
Wrap --> End
```

**Diagram sources**
- [router.py](file://core/tools/router.py#L287-L302)
- [router.py](file://core/tools/router.py#L46-L85)

**Section sources**
- [router.py](file://core/tools/router.py#L46-L85)
- [router.py](file://core/tools/router.py#L126-L134)
- [router.py](file://core/tools/router.py#L287-L302)

### Tool Result Processing and Multimodal Injection
- A2A Response Wrapping: Results are normalized into a standard shape with x-a2a-* metadata.
- Vision Injection: Vision tool returns Base64 image data suitable for multimodal injection into the session context.
- **Enhanced**: Camera tool returns JPEG bytes for immediate visual processing and user feedback.

```mermaid
flowchart TD
Start(["Tool Result"]) --> Normalize["Normalize to dict"]
Normalize --> AddMeta["Attach A2A metadata"]
AddMeta --> Vision{"Is vision result?"}
Vision --> |Yes| Inject["Inject Base64 image into context"]
Vision --> |No| Camera{"Is camera result?"}
Camera --> |Yes| Process["Process JPEG bytes for visual feedback"]
Camera --> |No| Forward["Forward to session"]
Process --> End(["Exit"])
Inject --> End
Forward --> End
```

**Diagram sources**
- [router.py](file://core/tools/router.py#L325-L342)
- [vision_tool.py](file://core/tools/vision_tool.py#L45-L52)
- [camera_tool.py](file://core/tools/camera_tool.py#L40-L47)

**Section sources**
- [router.py](file://core/tools/router.py#L325-L342)
- [vision_tool.py](file://core/tools/vision_tool.py#L45-L52)
- [camera_tool.py](file://core/tools/camera_tool.py#L40-L47)

### Tool Scheduling and Priority Management
- CognitiveScheduler: Proactive speculation based on keywords, temporal memory retention, interrupt overlap buffer, and echo generation for long-running tools.
- Priority Signals: Adjusts focus based on acoustic traits (e.g., arousal).

```mermaid
flowchart TD
Start(["Scheduler Entry"]) --> Pulse{"Vision/Acoustic Pulse?"}
Pulse --> |Vision| Record["Record temporal memory"]
Pulse --> |Acoustic| Adjust["Adjust priority by arousal"]
Record --> Speculate["Speculate tools by keywords"]
Adjust --> Speculate
Speculate --> Echo["Schedule echo for long tools"]
Echo --> End(["Exit"])
```

**Diagram sources**
- [scheduler.py](file://core/ai/scheduler.py#L33-L114)

**Section sources**
- [scheduler.py](file://core/ai/scheduler.py#L10-L114)

### Security Utilities
- Ed25519 Signature Verification: Validates signatures using PyNaCl.
- Keypair Generation: Generates public/private key pairs for cryptographic identities.

```mermaid
flowchart TD
Start(["Verify Signature"]) --> Decode["Decode hex inputs to bytes"]
Decode --> MakeKey["Construct VerifyKey"]
MakeKey --> Verify["Verify signature against message"]
Verify --> Result{"Valid?"}
Result --> |Yes| Ok["Return True"]
Result --> |No| Fail["Return False"]
Ok --> End(["Exit"])
Fail --> End
```

**Diagram sources**
- [security.py](file://core/utils/security.py#L18-L56)

**Section sources**
- [security.py](file://core/utils/security.py#L18-L71)

## Dependency Analysis
- ToolRouter depends on LocalVectorStore for semantic recovery and on BiometricMiddleware for security gating.
- AetherEngine composes managers and registers tools via ToolRouter.
- CognitiveScheduler subscribes to events and interacts with ToolRouter for speculative execution.
- Tool modules depend on their respective connectors (Firebase) for persistence.
- **Enhanced**: Camera tool depends on OpenCV for video capture, Hive memory depends on Firebase connector, Voice auth depends on audio state for biometric verification.

```mermaid
graph LR
Engine["AetherEngine"] --> TRouter["ToolRouter"]
Engine --> Scheduler["CognitiveScheduler"]
TRouter --> VS["LocalVectorStore"]
TRouter --> Sec["BiometricMiddleware"]
Sys["System Tool"] --> TRouter
Mem["Memory Tool"] --> TRouter
Vision["Vision Tool"] --> TRouter
Tasks["Tasks Tool"] --> TRouter
Hive["Hive Tool"] --> TRouter
Camera["Camera Tool"] --> TRouter
HiveMem["Hive Memory"] --> TRouter
VoiceAuth["Voice Auth"] --> TRouter
Scheduler --> TRouter
```

**Diagram sources**
- [engine.py](file://core/engine.py#L26-L100)
- [router.py](file://core/tools/router.py#L120-L200)
- [vector_store.py](file://core/tools/vector_store.py#L21-L82)
- [scheduler.py](file://core/ai/scheduler.py#L16-L32)

**Section sources**
- [engine.py](file://core/engine.py#L26-L100)
- [router.py](file://core/tools/router.py#L120-L200)

## Performance Considerations
- Latency Tiering: Tools declare latency tiers to guide prioritization and expectations.
- Idempotency: Tools can mark themselves idempotent to enable safe retries.
- Profiling: ToolExecutionProfiler tracks durations and computes percentiles for observability.
- Semantic Recovery: Vector store embeddings reduce misrouting and improve resilience.
- Concurrency: Engine uses asyncio TaskGroup to run subsystems in parallel.
- **Enhanced**: Camera tool uses JPEG encoding with 70 quality to balance latency and payload size.

Recommendations:
- Prefer idempotent tools for operations that may be retried.
- Use latency tiers to guide scheduling and resource allocation.
- Monitor p95/p99 metrics to identify bottlenecks.
- Limit context sizes (e.g., truncated file reads) to control overhead.
- **Enhanced**: Optimize camera capture by considering permanent camera connection for reduced latency.

**Section sources**
- [router.py](file://core/tools/router.py#L154-L176)
- [router.py](file://core/tools/router.py#L87-L118)
- [router.py](file://core/tools/router.py#L357-L360)
- [engine.py](file://core/engine.py#L212-L225)
- [camera_tool.py](file://core/tools/camera_tool.py#L40-L47)

## Troubleshooting Guide
Common issues and resolutions:
- Unknown Tool: ToolRouter attempts semantic recovery; if no close match, returns available tools and error details.
- Argument Errors: Dispatch catches TypeError and returns a 400 with details.
- Execution Failures: Exceptions are caught and returned as 500 errors with logs.
- Biometric Failure: Middleware denies execution with 403; verify context flags or development fallback mode.
- Offline Persistence: Memory and Tasks tools fall back gracefully when Firebase is unavailable.
- **Enhanced**: Camera capture failures: Check camera permissions and hardware availability; consider alternative camera indices.
- **Enhanced**: Hive memory offline: Verify Firebase connectivity and hive_memory collection access.
- **Enhanced**: Voice authentication failures: Ensure microphone is active and speak clearly during calibration.

Operational tips:
- Inspect A2A status codes and latency metadata in responses.
- Review performance reports from ToolRouter to identify slow tools.
- Confirm tool registration via ToolRouter.names and get_declarations.
- **Enhanced**: Monitor camera tool status and JPEG encoding quality.
- **Enhanced**: Verify voice authentication calibration state and pitch range validation.

**Section sources**
- [router.py](file://core/tools/router.py#L244-L282)
- [router.py](file://core/tools/router.py#L344-L356)
- [router.py](file://core/tools/router.py#L55-L84)
- [memory_tool.py](file://core/tools/memory_tool.py#L56-L93)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L67-L87)
- [camera_tool.py](file://core/tools/camera_tool.py#L25-L47)
- [hive_memory.py](file://core/tools/hive_memory.py#L37-L86)
- [voice_auth.py](file://core/tools/voice_auth.py#L77-L94)

## Conclusion
The Tool Execution System provides a robust, secure, and extensible framework for neural-driven tool invocation. Its architecture balances concurrency, resilience, and security through biometric middleware, semantic recovery, and standardized result wrapping. The enhanced system now supports 12 registered modules including camera capture, collective memory persistence, and voice authentication, expanding the platform's capabilities while maintaining security and performance standards. Developers can extend the system by adding new tool modules with JSON Schema parameter definitions and integrating with the existing router and scheduler.

## Appendices

### Developing Custom Tools
Steps to add a new tool:
1. Define handler function(s) with validated parameters.
2. Provide a JSON Schema for parameters in get_tools().
3. Register the tool via ToolRouter.register(...) or module.get_tools().
4. If sensitive, mark requires_biometric or rely on SENSITIVE_TOOLS.
5. Test with Engine.run() and observe A2A metadata and performance metrics.

Integration patterns:
- Use async handlers for I/O-bound workloads.
- Wrap results consistently for downstream consumers.
- Leverage CognitiveScheduler for speculative pre-warming of related tools.
- **Enhanced**: Consider biometric middleware integration for sensitive operations.

Security considerations:
- Enforce parameter validation using JSON Schema.
- Apply biometric middleware for sensitive operations.
- Avoid exposing unsafe commands or privileged actions.
- Use cryptographic utilities for identity and integrity where applicable.
- **Enhanced**: Implement proper error handling for hardware dependencies (camera, microphone).
- **Enhanced**: Validate audio state and pitch ranges for voice authentication tools.

**Section sources**
- [router.py](file://core/tools/router.py#L146-L176)
- [router.py](file://core/tools/router.py#L183-L200)
- [system_tool.py](file://core/tools/system_tool.py#L87-L135)
- [memory_tool.py](file://core/tools/memory_tool.py#L246-L330)
- [vision_tool.py](file://core/tools/vision_tool.py#L58-L75)
- [tasks_tool.py](file://core/tools/tasks_tool.py#L216-L325)
- [hive_tool.py](file://core/tools/hive_tool.py#L51-L78)
- [camera_tool.py](file://core/tools/camera_tool.py#L53-L65)
- [hive_memory.py](file://core/tools/hive_memory.py#L89-L122)
- [voice_auth.py](file://core/tools/voice_auth.py#L97-L111)
- [security.py](file://core/utils/security.py#L18-L71)