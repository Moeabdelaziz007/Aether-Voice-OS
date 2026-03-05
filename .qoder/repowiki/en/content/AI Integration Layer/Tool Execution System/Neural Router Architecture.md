# Neural Router Architecture

<cite>
**Referenced Files in This Document**
- [core/tools/router.py](file://core/tools/router.py)
- [core/tools/vector_store.py](file://core/tools/vector_store.py)
- [core/tools/system_tool.py](file://core/tools/system_tool.py)
- [core/ai/session.py](file://core/ai/session.py)
- [tests/unit/test_core.py](file://tests/unit/test_core.py)
- [tests/integration/test_adk_stress.py](file://tests/integration/test_adk_stress.py)
- [docs/gateway_protocol.md](file://docs/gateway_protocol.md)
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
This document explains the Neural Router architecture component responsible for dispatching Gemini Live function calls to registered tool handlers. It covers the ToolRouter class design, the ToolRegistration dataclass, the tool registration process, semantic recovery via vector similarity, function declaration generation for Gemini, and the A2A protocol response wrapping with status code management. It also includes examples of tool registration, parameter schemas, and handler patterns.

## Project Structure
The Neural Router lives in the tools subsystem and integrates with the AI session layer to orchestrate function execution. The vector store provides semantic indexing for tool name recovery. System tools demonstrate typical handler patterns and parameter schemas.

```mermaid
graph TB
subgraph "AI Layer"
Session["GeminiLiveSession<br/>core/ai/session.py"]
end
subgraph "Tools Layer"
Router["ToolRouter<br/>core/tools/router.py"]
VS["LocalVectorStore<br/>core/tools/vector_store.py"]
SysTools["System Tools Module<br/>core/tools/system_tool.py"]
end
Session --> Router
Router --> VS
Router --> SysTools
```

**Diagram sources**
- [core/ai/session.py](file://core/ai/session.py#L493-L589)
- [core/tools/router.py](file://core/tools/router.py#L120-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [core/tools/system_tool.py](file://core/tools/system_tool.py#L198-L310)

**Section sources**
- [core/ai/session.py](file://core/ai/session.py#L390-L589)
- [core/tools/router.py](file://core/tools/router.py#L1-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L1-L112)
- [core/tools/system_tool.py](file://core/tools/system_tool.py#L1-L310)

## Core Components
- ToolRouter: Central dispatcher for Gemini Live function calls. Handles registration, discovery, dispatch, biometric middleware, semantic recovery, and A2A response wrapping.
- ToolRegistration: Dataclass capturing tool metadata: name, description, parameters, handler, latency tier, idempotency, and biometric requirement.
- LocalVectorStore: Lightweight semantic index for tool name recovery using cosine similarity.
- System Tools Module: Example tool definitions with handlers and parameter schemas.

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L33-L44)
- [core/tools/router.py](file://core/tools/router.py#L120-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [core/tools/system_tool.py](file://core/tools/system_tool.py#L198-L310)

## Architecture Overview
The Neural Router sits between the AI session and tool modules. When Gemini emits a function call, the session forwards it to ToolRouter.dispatch(), which resolves the handler, optionally performs semantic recovery, enforces biometric middleware for sensitive tools, executes the handler (sync or async), and wraps the result in an A2A-compliant response.

```mermaid
sequenceDiagram
participant Gemini as "Gemini Live"
participant Session as "GeminiLiveSession<br/>core/ai/session.py"
participant Router as "ToolRouter<br/>core/tools/router.py"
participant VS as "LocalVectorStore<br/>core/tools/vector_store.py"
participant Handler as "Tool Handler"
Gemini->>Session : "tool_call" with function_calls
Session->>Router : dispatch(function_call)
alt Tool name exists
Router->>Handler : invoke handler(**args)
else Tool name missing
Router->>VS : get_query_embedding(name)
VS-->>Router : query_vector
Router->>VS : search(query_vector, limit=1)
VS-->>Router : top hit
alt Similarity > threshold
Router->>Handler : invoke handler(**args)
else No close match
Router-->>Session : error response (404)
end
end
Router-->>Session : A2A-wrapped result (x-a2a-status)
Session-->>Gemini : FunctionResponse
```

**Diagram sources**
- [core/ai/session.py](file://core/ai/session.py#L493-L589)
- [core/tools/router.py](file://core/tools/router.py#L234-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L106-L112)

## Detailed Component Analysis

### ToolRouter
ToolRouter is the central dispatcher. It maintains a registry of tools, generates Gemini-compatible function declarations, supports module-based registration, performs semantic recovery, enforces biometric middleware for sensitive tools, and wraps results in A2A responses with standardized status codes.

Key responsibilities:
- Registration: register(), register_module(), un_register()
- Discovery: get_declarations() for Gemini
- Dispatch: dispatch() with neural routing logic
- Semantics: semantic recovery via LocalVectorStore
- Security: BiometricMiddleware for sensitive tools
- Observability: ToolExecutionProfiler and performance reporting

```mermaid
classDiagram
class ToolRouter {
-dict~str, ToolRegistration~ _tools
-ToolExecutionProfiler _profiler
-LocalVectorStore _vector_store
-BiometricMiddleware _biometric_middleware
+register(name, description, parameters, handler, latency_tier, idempotent)
+un_register(name)
+register_module(module)
+get_declarations() list
+dispatch(function_call) dict
+get_performance_report() dict
+count int
+names str[]
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
-bool _fallback_authorized
+verify(tool_name, context) bool
}
class ToolExecutionProfiler {
-dict~str, float[]~ _execution_times
+record(tool_name, duration) void
+get_stats(tool_name) dict
}
ToolRouter --> ToolRegistration : "manages"
ToolRouter --> BiometricMiddleware : "uses"
ToolRouter --> ToolExecutionProfiler : "uses"
ToolRouter --> LocalVectorStore : "optional semantic index"
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L33-L44)
- [core/tools/router.py](file://core/tools/router.py#L120-L360)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L120-L360)

### ToolRegistration Dataclass
ToolRegistration encapsulates the tool’s identity, schema, and runtime metadata:
- name: Unique tool identifier
- description: Human-readable description for Gemini
- parameters: JSON Schema defining the tool’s arguments
- handler: Callable implementing the tool logic
- latency_tier: Performance classification (e.g., low latency)
- idempotent: Whether the tool can be retried safely
- requires_biometric: Enables biometric middleware enforcement

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L33-L44)

### Tool Registration Process
- Manual registration: register() adds a single tool definition and asynchronously indexes its name/description in the semantic store if present.
- Module registration: register_module() discovers tools via a module’s get_tools() and registers each definition.
- Unregistration: un_register() removes a tool from the registry.

```mermaid
flowchart TD
Start(["Register Tool"]) --> BuildDef["Build ToolRegistration"]
BuildDef --> AddToRegistry["Add to _tools registry"]
AddToRegistry --> MaybeIndex{"Vector store initialized?"}
MaybeIndex --> |Yes| IndexAsync["Async index: add_text(name, title+desc)"]
MaybeIndex --> |No| SkipIndex["Skip indexing"]
IndexAsync --> Done(["Registered"])
SkipIndex --> Done
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L146-L176)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L146-L200)
- [core/tools/system_tool.py](file://core/tools/system_tool.py#L198-L310)

### Function Declaration Generation for Gemini
get_declarations() produces a list of FunctionDeclaration objects compatible with Gemini Live. Each declaration includes name, description, and optional parameters schema.

```mermaid
flowchart TD
GenStart(["Generate Declarations"]) --> Iterate["Iterate registered tools"]
Iterate --> BuildDecl["Build FunctionDeclaration(name, description, parameters)"]
BuildDecl --> Collect["Collect into list"]
Collect --> GenEnd(["Return declarations"])
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L211-L232)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L211-L232)
- [tests/unit/test_core.py](file://tests/unit/test_core.py#L487-L502)

### Tool Discovery Mechanism
- During session setup, ToolRouter.get_declarations() is used to inform Gemini of available tools.
- During runtime, ToolRouter.dispatch() resolves the handler by name lookup. If missing, it attempts semantic recovery.

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L211-L232)
- [core/tools/router.py](file://core/tools/router.py#L234-L284)

### Dispatch Method: Neural Routing Logic
dispatch() orchestrates:
- Parameter extraction from function_call.args
- Name resolution: exact match or semantic recovery
- Biometric middleware enforcement for sensitive tools
- Handler invocation supporting both sync and async handlers
- A2A response wrapping with standardized headers and status codes

```mermaid
flowchart TD
DStart(["dispatch(function_call)"]) --> Extract["Extract name and args"]
Extract --> Exists{"Tool exists?"}
Exists --> |No| Recover["Semantic recovery via vector store"]
Recover --> Match{"Close match (> threshold)?"}
Match --> |Yes| UseMatch["Use matched tool name"]
Match --> |No| Return404["Return error + available tools (404)"]
Exists --> |Yes| LoadTool["Load ToolRegistration"]
UseMatch --> LoadTool
LoadTool --> BioCheck{"Sensitive tool?"}
BioCheck --> |Yes| Verify["BiometricMiddleware.verify()"]
Verify --> |Denied| Return403["Return 403"]
Verify --> |Authorized| Invoke["Invoke handler (**args)"]
BioCheck --> |No| Invoke
Invoke --> Wrap["Wrap result in A2A response"]
Wrap --> DEnd(["Return"])
Return404 --> DEnd
Return403 --> DEnd
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L234-L360)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L234-L360)

### Semantic Recovery Sequence
When a tool name is not found, ToolRouter attempts semantic recovery:
- Generate query embedding for the tool name
- Search the vector store for the nearest neighbor
- If similarity exceeds a threshold, redirect execution to the matched tool; otherwise return an error with available tools.

```mermaid
flowchart TD
SRStart(["Semantic Recovery"]) --> Embed["get_query_embedding(name)"]
Embed --> Search["search(query_vector, limit=1)"]
Search --> Threshold{"similarity > 0.75?"}
Threshold --> |Yes| Redirect["Redirect to matched tool"]
Threshold --> |No| ReturnErr["Return error + available tools"]
Redirect --> SREnd(["Proceed to dispatch"])
ReturnErr --> SREnd
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L244-L284)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L106-L112)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L244-L284)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L83-L112)

### A2A Protocol Response Wrapping and Status Codes
ToolRouter wraps results with:
- result: Ensures a dict-shaped payload; scalar results are placed under a data key
- x-a2a-status: 200 for normal, 202 if recovered, 400/403/500 for errors
- x-a2a-latency: latency tier from ToolRegistration
- x-a2a-idempotent: idempotency flag
- x-a2a-duration_ms: execution duration in milliseconds

```mermaid
flowchart TD
WrapStart(["Wrap Result"]) --> CheckDict{"Is result a dict?"}
CheckDict --> |No| ToDict["Place under 'data' key"]
CheckDict --> |Yes| UseAsIs["Use as-is"]
ToDict --> StatusSel["Select status: 202 if recovered else 200"]
UseAsIs --> StatusSel
StatusSel --> Override{"Result has 'a2a_code'?"}
Override --> |Yes| UseCode["Pop 'a2a_code' and use it"]
Override --> |No| KeepSel["Keep selected status"]
UseCode --> BuildResp["Build A2A response"]
KeepSel --> BuildResp
BuildResp --> WrapEnd(["Return"])
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L325-L342)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L325-L342)

### Examples: Tool Registration, Parameter Schemas, and Handler Patterns
- System tools module demonstrates:
  - get_tools() returning a list of tool definitions with name, description, parameters JSON Schema, and handler
  - Handlers as async functions returning structured dicts
  - Parameter schemas with required fields and descriptions

**Section sources**
- [core/tools/system_tool.py](file://core/tools/system_tool.py#L198-L310)
- [tests/unit/test_core.py](file://tests/unit/test_core.py#L251-L302)

## Dependency Analysis
ToolRouter depends on:
- LocalVectorStore for semantic recovery
- Gemini types for function declarations and calls
- Python asyncio and inspect for async execution and introspection
- Logging for observability

```mermaid
graph LR
Router["ToolRouter<br/>core/tools/router.py"] --> VS["LocalVectorStore<br/>core/tools/vector_store.py"]
Router --> Types["google.genai.types<br/>FunctionDeclaration/FunctionCall"]
Router --> Inspect["inspect<br/>iscoroutinefunction/isawaitable"]
Router --> Asyncio["asyncio<br/>to_thread/gather"]
Router --> Logging["logging"]
```

**Diagram sources**
- [core/tools/router.py](file://core/tools/router.py#L17-L30)
- [core/tools/router.py](file://core/tools/router.py#L120-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L15-L16)

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L17-L30)
- [core/tools/router.py](file://core/tools/router.py#L120-L360)
- [core/tools/vector_store.py](file://core/tools/vector_store.py#L15-L16)

## Performance Considerations
- Parallel dispatch: The AI session executes multiple function calls concurrently, reducing total latency.
- Profiling: ToolExecutionProfiler records execution times and computes percentiles for latency reporting.
- Async handlers: Dispatch supports both sync and async handlers, with sync handlers executed in threads to avoid blocking the event loop.
- Semantic indexing: Vector store indexing is asynchronous to avoid blocking registration.

**Section sources**
- [core/ai/session.py](file://core/ai/session.py#L512-L520)
- [core/tools/router.py](file://core/tools/router.py#L87-L118)
- [core/tools/router.py](file://core/tools/router.py#L312-L323)
- [core/tools/router.py](file://core/tools/router.py#L165-L173)

## Troubleshooting Guide
Common issues and diagnostics:
- Unknown tool: Returned when the tool name is not registered and semantic recovery fails. The response includes available tools and a 404 status.
- Argument errors: Raised when handler signature mismatch occurs; response carries a 400 status.
- Execution failures: Exceptions during handler execution yield a 500 status and an error message.
- Biometric verification failure: Sensitive tools require biometric verification; denial yields a 403 status.
- Stress scenarios: Tests validate high concurrency and crash isolation.

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L277-L355)
- [tests/integration/test_adk_stress.py](file://tests/integration/test_adk_stress.py#L10-L79)

## Conclusion
The Neural Router provides a robust, secure, and observable dispatch layer for Gemini Live function calls. It combines explicit tool registration with semantic recovery, enforces biometric middleware for sensitive operations, and standardizes responses for multi-agent interoperability. Its design supports both synchronous and asynchronous handlers, integrates with a lightweight vector store for resilience, and scales via parallel execution.

## Appendices

### A2A Protocol Notes
- A2A response fields: result, x-a2a-status, x-a2a-latency, x-a2a-idempotent, x-a2a-duration_ms
- Status code semantics:
  - 200: Normal success
  - 202: Success after semantic recovery
  - 400: Bad request (argument error)
  - 403: Forbidden (biometric verification failed)
  - 404: Not found (unknown tool and no semantic match)
  - 500: Internal error

**Section sources**
- [core/tools/router.py](file://core/tools/router.py#L325-L355)
- [docs/gateway_protocol.md](file://docs/gateway_protocol.md#L108-L124)