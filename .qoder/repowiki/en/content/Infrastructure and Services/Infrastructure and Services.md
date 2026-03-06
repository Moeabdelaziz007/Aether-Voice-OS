# Infrastructure and Services

<cite>
**Referenced Files in This Document**
- [config.py](file://core/infra/config.py)
- [admin_api.py](file://core/services/admin_api.py)
- [watchdog.py](file://core/services/watchdog.py)
- [lifecycle.py](file://core/infra/lifecycle.py)
- [state_manager.py](file://core/infra/state_manager.py)
- [service_container.py](file://core/infra/service_container.py)
- [interface.py](file://core/infra/cloud/firebase/interface.py)
- [telemetry.py](file://core/infra/telemetry.py)
- [event_bus.py](file://core/infra/event_bus.py)
- [gateway.py](file://core/infra/transport/gateway.py)
- [bus.py](file://core/infra/transport/bus.py)
- [session_state.py](file://core/infra/transport/session_state.py)
- [messages.py](file://core/infra/transport/messages.py)
- [registry.py](file://core/services/registry.py)
- [infra.py](file://core/logic/managers/infra.py)
- [engine.py](file://core/engine.py)
- [di_injector.py](file://agents/di_injector.py)
- [agent_results.json](file://agent_results.json)
- [agents.py](file://core/logic/managers/agents.py)
- [registry.py](file://core/ai/agents/registry.py)
</cite>

## Update Summary
**Changes Made**
- Removed dependency injection container system in favor of direct class instantiation for improved clarity and reduced complexity
- Updated ServiceContainer to maintain singleton pattern for backward compatibility while eliminating DI usage
- Removed DIInjectorAgent functionality as dependency injection is no longer used
- Updated engine orchestration to use direct instantiation of components
- Simplified lifecycle management without container dependency

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
This document describes the infrastructure and services layer of Aether Voice OS. It covers configuration management, cloud integration, transport and gateway services, event bus and state management, telemetry and observability, watchdog-based health monitoring and recovery, lifecycle orchestration, direct class instantiation patterns, agent ecosystem management, and operational guidance for deployment, scaling, and maintenance.

## Project Structure
The infrastructure and services layer spans several modules with simplified direct instantiation patterns:
- Configuration and environment handling
- Transport and gateway for client connections
- Event bus and state machines for coordination
- Cloud persistence and telemetry
- Admin API for monitoring and control
- Watchdog for autonomous health checks and recovery
- Lifecycle manager for startup/shutdown orchestration
- ServiceContainer maintained for backward compatibility
- Agent ecosystem with registry and management
- Results tracking system for agent performance monitoring

```mermaid
graph TB
subgraph "Core Runtime"
CFG["Config Loader<br/>config.py"]
BUS["EventBus<br/>event_bus.py"]
STATE["State Manager<br/>state_manager.py"]
LIFE["Lifecycle Manager<br/>lifecycle.py"]
CONTAINER["ServiceContainer<br/>service_container.py"]
ENG["Engine Orchestrator<br/>engine.py"]
end
subgraph "Transport"
GW["AetherGateway<br/>gateway.py"]
MSG["Messages<br/>messages.py"]
SB["GlobalBus (Redis)<br/>bus.py"]
SS["Session State<br/>session_state.py"]
end
subgraph "Cloud & Observability"
FB["Firebase Connector<br/>firebase/interface.py"]
TELE["Telemetry Manager<br/>telemetry.py"]
end
subgraph "Services"
ADMIN["Admin API Server<br/>admin_api.py"]
WD["Watchdog<br/>watchdog.py"]
REG["Package Registry<br/>registry.py"]
INFRA["Infra Manager<br/>logic/managers/infra.py"]
AGENTMGR["Agent Manager<br/>logic/managers/agents.py"]
end
subgraph "Agent Ecosystem"
AGENTS["Agent Registry<br/>ai/agents/registry.py"]
RESULTS["Results Tracking<br/>agent_results.json"]
end
CFG --> ENG
ENG --> BUS
ENG --> GW
ENG --> ADMIN
ENG --> WD
ENG --> INFRA
ENG --> AGENTMGR
GW --> SB
GW --> SS
SS --> BUS
FB --> ENG
TELE --> ENG
REG --> ENG
AGENTMGR --> AGENTS
LIFE --> ENG
```

**Diagram sources**
- [engine.py](file://core/engine.py#L26-L110)
- [config.py](file://core/infra/config.py#L85-L110)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [gateway.py](file://core/infra/transport/gateway.py#L69-L153)
- [bus.py](file://core/infra/transport/bus.py#L25-L200)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [telemetry.py](file://core/infra/telemetry.py#L14-L76)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [registry.py](file://core/services/registry.py#L44-L125)
- [infra.py](file://core/logic/managers/infra.py#L11-L47)
- [lifecycle.py](file://core/infra/lifecycle.py#L10-L86)
- [service_container.py](file://core/infra/service_container.py#L1-L51)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)
- [agent_results.json](file://agent_results.json#L1-L315)

**Section sources**
- [engine.py](file://core/engine.py#L26-L110)
- [config.py](file://core/infra/config.py#L85-L110)
- [gateway.py](file://core/infra/transport/gateway.py#L69-L153)
- [bus.py](file://core/infra/transport/bus.py#L25-L200)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [telemetry.py](file://core/infra/telemetry.py#L14-L76)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [registry.py](file://core/services/registry.py#L44-L125)
- [infra.py](file://core/logic/managers/infra.py#L11-L47)
- [lifecycle.py](file://core/infra/lifecycle.py#L10-L86)
- [service_container.py](file://core/infra/service_container.py#L1-L51)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)
- [agent_results.json](file://agent_results.json#L1-L315)

## Core Components
- Configuration and Environment
  - Centralized configuration loader with environment-backed settings, nested keys, and JSON fallback.
  - Firebase credentials decoding for secure cloud connectivity.
- Transport and Gateway
  - WebSocket-based gateway with challenge-response authentication, capability negotiation, heartbeat, and session lifecycle management.
  - Session state machine with atomic transitions and persistence to the Global Bus.
- Event Bus and State Management
  - Tiered event bus with audio/control/telemetry lanes, expiration-aware routing, and subscriber dispatch.
  - System state machine enforcing allowed transitions and broadcasting control events.
- Cloud Integration and Telemetry
  - Firebase connector for sessions, messages, metrics, knowledge, and repair logs.
  - Telemetry sink exporting traces via OTLP to Arize/Phoenix with token usage recording.
- Admin API and Watchdog
  - Local Admin API server exposing system state and telemetry for the admin dashboard.
  - Autonomous watchdog monitoring logs and triggering healing actions.
- Lifecycle Orchestration
  - Deterministic boot and shutdown sequences with signal handling and graceful teardown.
- ServiceContainer and Direct Instantiation
  - ServiceContainer maintained for backward compatibility with singleton pattern.
  - Engine uses direct class instantiation for all components, eliminating dependency injection overhead.
- Agent Ecosystem
  - Centralized AgentRegistry for managing agent identities and capabilities.
  - AgentManager coordinating agent lifecycle, handovers, and integration with the system.
  - Results tracking system (agent_results.json) for monitoring agent performance and outcomes.
- Package Registry
  - Dynamic discovery and hot-reload of .ath packages with semantic indexing.

**Section sources**
- [config.py](file://core/infra/config.py#L113-L158)
- [gateway.py](file://core/infra/transport/gateway.py#L320-L507)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [telemetry.py](file://core/infra/telemetry.py#L14-L76)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [lifecycle.py](file://core/infra/lifecycle.py#L10-L86)
- [service_container.py](file://core/infra/service_container.py#L1-L51)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)
- [agent_results.json](file://agent_results.json#L1-L315)
- [registry.py](file://core/services/registry.py#L44-L125)

## Architecture Overview
The system is built around an event-driven architecture with a central EventBus and a Global Bus for distributed state and pub/sub. The AetherGateway manages client sessions, integrates with the Global Bus for multi-node synchronization, and coordinates with the State Manager and Session State Manager. Cloud services (Firebase) provide persistence and telemetry, while the Admin API and Watchdog support monitoring and autonomous recovery. The simplified architecture eliminates dependency injection overhead while maintaining clean component separation and direct instantiation patterns.

```mermaid
graph TB
subgraph "Client Layer"
WS["WebSocket Clients"]
end
subgraph "Edge"
GW["AetherGateway<br/>gateway.py"]
SB["GlobalBus (Redis)<br/>bus.py"]
SS["Session State Manager<br/>session_state.py"]
CONTAINER["ServiceContainer<br/>service_container.py"]
END
subgraph "Core"
BUS["EventBus<br/>event_bus.py"]
SM["System State Manager<br/>state_manager.py"]
INF["Infra Manager<br/>logic/managers/infra.py"]
WD["Watchdog<br/>watchdog.py"]
ADMIN["Admin API<br/>admin_api.py"]
AGENTMGR["Agent Manager<br/>logic/managers/agents.py"]
END
subgraph "Agent Ecosystem"
AGENTS["Agent Registry<br/>ai/agents/registry.py"]
RESULTS["Results Tracking<br/>agent_results.json"]
END
subgraph "Cloud"
FB["Firebase<br/>firebase/interface.py"]
TELE["Telemetry<br/>telemetry.py"]
END
WS --> GW
GW --> SB
GW --> SS
BUS --> SM
INF --> FB
INF --> WD
ADMIN --> BUS
TELE --> BUS
GW --> BUS
CONTAINER --> BUS
AGENTMGR --> AGENTS
RESULTS --> AGENTMGR
```

**Diagram sources**
- [gateway.py](file://core/infra/transport/gateway.py#L320-L507)
- [bus.py](file://core/infra/transport/bus.py#L25-L200)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [infra.py](file://core/logic/managers/infra.py#L11-L47)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [telemetry.py](file://core/infra/telemetry.py#L14-L76)
- [service_container.py](file://core/infra/service_container.py#L1-L51)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)
- [agent_results.json](file://agent_results.json#L1-L315)

## Detailed Component Analysis

### ServiceContainer and Direct Instantiation
The ServiceContainer maintains its singleton pattern for backward compatibility but is no longer actively used for dependency injection. The engine now uses direct class instantiation for all components, eliminating the complexity of dependency injection while maintaining the ability to access the container if needed for legacy purposes.

```mermaid
classDiagram
class ServiceContainer {
-_instance : ServiceContainer
-_services : Dict[str, Any]
-_factories : Dict[str, Callable]
-_lock : Lock
+register_singleton(name : str, service_class : Type, *args, **kwargs)
+register_factory(name : str, factory : Callable)
+get(name : str) Any
+clear()
+__new__(cls) ServiceContainer
}
class AetherEngine {
+__init__(config : AetherConfig)
+_setup_logging()
+_setup_vector_store()
+_register_tools()
+run()
+shutdown()
}
AetherEngine --> ServiceContainer : "maintained for compatibility"
```

**Diagram sources**
- [service_container.py](file://core/infra/service_container.py#L9-L51)
- [engine.py](file://core/engine.py#L22-L95)

**Section sources**
- [service_container.py](file://core/infra/service_container.py#L1-L51)
- [engine.py](file://core/engine.py#L22-L95)

### Simplified Lifecycle Management
The LifecycleManager operates without dependency injection, directly managing component initialization and shutdown sequences. The manager handles OS signals, coordinates component startup, and manages graceful shutdown procedures without container dependency.

```mermaid
stateDiagram-v2
[*] --> BOOTING
BOOTING --> IDLE : "Components initialized"
IDLE --> LISTENING : "EventBus started"
LISTENING --> THINKING : "Audio components ready"
THINKING --> SPEAKING : "Gateway active"
SPEAKING --> IDLE : "Task complete"
IDLE --> PAUSED : "Shutdown requested"
PAUSED --> [*] : "Graceful shutdown"
IDLE --> ERROR : "Critical failure"
ERROR --> BOOTING : "Recovery"
```

**Diagram sources**
- [lifecycle.py](file://core/infra/lifecycle.py#L24-L86)

**Section sources**
- [lifecycle.py](file://core/infra/lifecycle.py#L1-L110)

### Agent Ecosystem Management
The agent ecosystem continues to provide specialized capabilities through a registry-based approach. The AgentRegistry manages agent identities, capabilities, and semantic fingerprints for intelligent routing. The AgentManager coordinates agent lifecycle, handovers, and integration with the broader system architecture.

```mermaid
classDiagram
class AgentRegistry {
-_agents : Dict[str, AgentMetadata]
-_capability_map : Dict[str, List[str]]
+register_agent(metadata : AgentMetadata)
+get_agent(agent_id : str) AgentMetadata
+find_agents_by_capability(capability : str) List[AgentMetadata]
+list_all_agents() List[AgentMetadata]
+unregister_agent(agent_id : str)
}
class AgentManager {
-_config : AetherConfig
-_router : Any
-_event_bus : Any
-_registry : AetherRegistry
-_hive : HiveCoordinator
+scan_registry()
+stop_watcher()
}
class AgentMetadata {
+id : str
+name : str
+version : str
+description : str
+capabilities : List[str]
+system_prompt : str
+tools : List[Dict[str, Any]]
+semantic_fingerprint : List[float]
}
```

**Diagram sources**
- [registry.py](file://core/ai/agents/registry.py#L35-L83)
- [agents.py](file://core/logic/managers/agents.py#L11-L38)

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L1-L110)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)

### Results Tracking System
The agent_results.json file provides comprehensive tracking of agent performance, modifications, and outcomes. It captures detailed metrics for each agent including files modified, errors encountered, and specific performance indicators. This system enables monitoring and analysis of the agent ecosystem's effectiveness.

```mermaid
graph TB
subgraph "Agent Results Tracking"
FORMATTER["FormatterAgent<br/>formatted_files, lint_errors_fixed"]
REFAC["RefactorAgent<br/>files_modified, print_statements_converted"]
TEST["TestAgent<br/>tests_passed, tests_failed, coverage"]
SEC["SecurityAgent<br/>vulnerabilities_found, issues_fixed"]
LEARN["LearningAgent<br/>commits_analyzed, patterns_identified"]
OPT["OptimizationAgent<br/>files_analyzed, optimizations_found"]
end
RESULTS["agent_results.json"] --> FORMATTER
RESULTS --> REFAC
RESULTS --> TEST
RESULTS --> SEC
RESULTS --> LEARN
RESULTS --> OPT
```

**Diagram sources**
- [agent_results.json](file://agent_results.json#L1-L315)

**Section sources**
- [agent_results.json](file://agent_results.json#L1-L315)

### Configuration Management
- Loads environment variables with nested keys and JSON fallback.
- Provides typed configuration models for audio, AI, and gateway settings.
- Handles Base64-encoded Firebase credentials for secure cloud integration.

```mermaid
flowchart TD
Start(["load_config()"]) --> CheckJSON["Check 'aether_runtime_config.json'"]
CheckJSON --> JSONExists{"Exists?"}
JSONExists --> |Yes| MergeEnv["Merge JSON into environment"]
JSONExists --> |No| TryEnv["Try .env-based loading"]
MergeEnv --> TryEnv
TryEnv --> EnvOK{"Success?"}
EnvOK --> |Yes| ReturnCfg["Return AetherConfig()"]
EnvOK --> |No| TryNoEnv["Retry without .env file"]
TryNoEnv --> NoEnvOK{"Success?"}
NoEnvOK --> |Yes| ReturnCfg
NoEnvOK --> |No| RaiseErr["Raise OSError"]
```

**Diagram sources**
- [config.py](file://core/infra/config.py#L113-L158)

**Section sources**
- [config.py](file://core/infra/config.py#L85-L158)

### Transport and Gateway
- Implements WebSocket handshake with Ed25519 or JWT verification.
- Manages audio input/output queues and routes binary chunks to the session.
- Maintains session state machine with transitions and persistence to Redis via Global Bus.
- Broadcasts ticks and health signals to clients; prunes dead connections.

```mermaid
sequenceDiagram
participant Client as "Client"
participant GW as "AetherGateway"
participant SB as "GlobalBus"
participant SS as "Session State Manager"
Client->>GW : "connect.challenge"
GW->>Client : "connect.challenge"
Client->>GW : "connect.response (signature/JWT)"
GW->>GW : "verify signature/JWT"
GW-->>Client : "connect.ack (session_id, tick_interval)"
GW->>SB : "subscribe('frontend_events')"
GW->>SS : "initialize()"
loop Heartbeat
GW->>Client : "tick"
end
GW->>SS : "transition_to(CONNECTED)"
GW-->>Client : "session_state_change"
```

**Diagram sources**
- [gateway.py](file://core/infra/transport/gateway.py#L529-L617)
- [messages.py](file://core/infra/transport/messages.py#L16-L80)
- [bus.py](file://core/infra/transport/bus.py#L110-L128)
- [session_state.py](file://core/infra/transport/session_state.py#L120-L162)

**Section sources**
- [gateway.py](file://core/infra/transport/gateway.py#L529-L617)
- [messages.py](file://core/infra/transport/messages.py#L16-L80)
- [session_state.py](file://core/infra/transport/session_state.py#L120-L162)
- [bus.py](file://core/infra/transport/bus.py#L110-L128)

### Event Bus and State Machines
- EventBus routes events by tier, enforces deadlines, and dispatches to subscribers concurrently.
- System State Manager validates transitions and publishes control events.
- Session State Manager ensures atomic state changes, persists snapshots to Redis, and supports recovery.

```mermaid
classDiagram
class EventBus {
+publish(event)
+subscribe(event_type, callback)
+start()
+stop()
}
class SystemState {
+BOOTING
+IDLE
+LISTENING
+THINKING
+SPEAKING
+PAUSED
+ERROR
+NIGHT_TERRORS
}
class EngineStateManager {
+current_state
+request_transition(new_state, source, reason) bool
+is_state(state) bool
}
class SessionState {
+INITIALIZING
+CONNECTED
+HANDING_OFF
+RESTARTING
+ERROR
+RECOVERING
+SHUTDOWN
}
class SessionStateManager {
+transition_to(new_state, reason, metadata) bool
+persist_to_bus() bool
+restore_from_bus(session_id) bool
+start_health_monitoring()
}
EngineStateManager --> EventBus : "publish ControlEvent"
SessionStateManager --> GlobalBus : "set_state/get_state"
```

**Diagram sources**
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)

**Section sources**
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)

### Cloud Integration and Telemetry
- FirebaseConnector initializes app with Base64 credentials or default credentials, starts sessions, logs messages and metrics, and records repairs.
- TelemetryManager exports traces via OTLP to Arize/Phoenix, sets usage attributes, and provides a global singleton.

```mermaid
sequenceDiagram
participant ENG as "Engine"
participant INF as "Infra Manager"
participant FB as "FirebaseConnector"
participant TELE as "TelemetryManager"
ENG->>INF : "initialize()"
INF->>FB : "initialize()"
FB-->>INF : "is_connected"
INF-->>ENG : "firebase_ok"
ENG->>TELE : "get_tracer()/record_usage()"
TELE-->>ENG : "tracer ready"
```

**Diagram sources**
- [infra.py](file://core/logic/managers/infra.py#L22-L31)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L31-L60)
- [telemetry.py](file://core/infra/telemetry.py#L35-L76)

**Section sources**
- [interface.py](file://core/infra/cloud/firebase/interface.py#L31-L60)
- [telemetry.py](file://core/infra/telemetry.py#L35-L76)
- [infra.py](file://core/logic/managers/infra.py#L22-L31)

### Admin API and Monitoring
- AdminAPIServer exposes a lightweight REST API on localhost for the admin dashboard, serving shared state snapshots.
- AdminAPIHandler routes endpoints for sessions, synapse, status, tools, hive, telemetry, and health checks.

```mermaid
sequenceDiagram
participant UI as "Admin Dashboard"
participant API as "AdminAPIServer"
participant Handler as "AdminAPIHandler"
UI->>API : "GET /api/status"
API->>Handler : "do_GET('/api/status')"
Handler-->>UI : '{"status" : "..."}'
UI->>API : "GET /health"
API->>Handler : "do_GET('/health')"
Handler-->>UI : '{"status" : "pass"}'
```

**Diagram sources**
- [admin_api.py](file://core/services/admin_api.py#L26-L82)

**Section sources**
- [admin_api.py](file://core/services/admin_api.py#L26-L82)

### Watchdog and Health Monitoring
- SREWatchdog installs a logging handler to intercept ERROR+ logs, throttles alerts, publishes health alerts to the Global Bus, and executes healing actions.
- Healing registry maps failure patterns to recovery routines (e.g., bus reconnect, system failure diagnosis).

```mermaid
flowchart TD
Start(["Watchdog start()"]) --> Hook["Add logging handler"]
Hook --> Loop["Periodic _watchdog_loop()"]
Loop --> CheckVitals["_check_vitals() -> publish 'system_health'"]
CheckVitals --> Loop
Start --> OnError["_on_log_error(record)"]
OnError --> Coalesce["coalesce on loop thread"]
Coalesce --> Match{"Pattern match?"}
Match --> |No| Loop
Match --> |Yes| Alert["Publish 'health_alerts'"]
Alert --> Heal["Execute healing action"]
Heal --> Loop
```

**Diagram sources**
- [watchdog.py](file://core/services/watchdog.py#L74-L168)
- [bus.py](file://core/infra/transport/bus.py#L96-L108)

**Section sources**
- [watchdog.py](file://core/services/watchdog.py#L74-L168)
- [bus.py](file://core/infra/transport/bus.py#L96-L108)

### Package Registry and Extension
- AetherRegistry scans a packages directory, validates manifests, supports hot-reload via watchdog, and provides semantic search for experts.

```mermaid
flowchart TD
Scan["scan()"] --> Discover["discover manifests"]
Discover --> Load["load_package(path)"]
Load --> Index["index_package()"]
Index --> Find["find_expert(query)"]
FS["Filesystem Events"] --> Handle["handle_fs_change(path)"]
Handle --> Reload["reload package"]
```

**Diagram sources**
- [registry.py](file://core/services/registry.py#L64-L125)
- [registry.py](file://core/services/registry.py#L202-L246)

**Section sources**
- [registry.py](file://core/services/registry.py#L64-L125)
- [registry.py](file://core/services/registry.py#L202-L246)

## Dependency Analysis
- Coupling
  - Gateway depends on GlobalBus for distributed state and pub/sub, and on Session State Manager for lifecycle control.
  - Infra Manager depends on FirebaseConnector and SREWatchdog.
  - Engine orchestrates EventBus, Gateway, Admin API, Watchdog, Infra Manager, and lifecycle directly.
  - AgentManager depends on AgentRegistry and HiveCoordinator for agent management.
- Cohesion
  - Each module encapsulates a focused responsibility: transport, state, cloud, telemetry, monitoring, lifecycle, registry, and agent ecosystem.
- External Dependencies
  - Redis for Global Bus, Firebase Admin SDK for cloud persistence, OpenTelemetry for tracing, websockets for transport, Pydantic for agent metadata validation.

```mermaid
graph LR
Engine["Engine"] --> EventBus["EventBus"]
Engine --> Gateway["AetherGateway"]
Engine --> Admin["Admin API"]
Engine --> Infra["Infra Manager"]
Engine --> AgentMgr["Agent Manager"]
Gateway --> GlobalBus["GlobalBus (Redis)"]
Gateway --> SessionState["Session State Manager"]
EventBus --> SystemState["System State Manager"]
AgentMgr --> AgentRegistry["Agent Registry"]
Infra --> Firebase["FirebaseConnector"]
Infra --> Watchdog["SREWatchdog"]
```

**Diagram sources**
- [engine.py](file://core/engine.py#L26-L110)
- [gateway.py](file://core/infra/transport/gateway.py#L69-L153)
- [bus.py](file://core/infra/transport/bus.py#L25-L200)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [infra.py](file://core/logic/managers/infra.py#L11-L47)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)

**Section sources**
- [engine.py](file://core/engine.py#L26-L110)
- [gateway.py](file://core/infra/transport/gateway.py#L69-L153)
- [bus.py](file://core/infra/transport/bus.py#L25-L200)
- [session_state.py](file://core/infra/transport/session_state.py#L71-L120)
- [event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [state_manager.py](file://core/infra/state_manager.py#L46-L95)
- [infra.py](file://core/logic/managers/infra.py#L11-L47)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L61)
- [watchdog.py](file://core/services/watchdog.py#L39-L94)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [agents.py](file://core/logic/managers/agents.py#L1-L52)
- [registry.py](file://core/ai/agents/registry.py#L1-L110)

## Performance Considerations
- Event Bus
  - Three-tier queues prevent priority inversion; dropping expired events preserves responsiveness.
- Gateway
  - Heartbeat pruning prevents resource leaks; binary routing avoids blocking.
- Telemetry
  - BatchSpanProcessor in production reduces overhead; SimpleSpanProcessor for development.
- Cloud
  - Async I/O and thread-offloaded writes minimize latency; Base64 credentials reduce config complexity.
- State Persistence
  - Snapshots and TTL-based keys ensure timely cleanup and recovery.
- ServiceContainer
  - Thread-safe singleton access minimizes contention; maintained for backward compatibility.
- Agent Ecosystem
  - Semantic fingerprinting enables efficient agent matching; results tracking helps identify performance bottlenecks.

## Troubleshooting Guide
- Admin API Port Occupancy
  - The Admin API attempts dynamic port allocation if the configured port is taken.
  - Verify the actual port in logs after startup.
- Firebase Connectivity
  - If credentials are missing or invalid, Firebase initializes in offline mode; sessions are not persisted.
  - Confirm Base64 credentials and environment variables.
- Watchdog Alerts
  - Excessive alerts may be throttled; inspect logs for recurring patterns.
  - Healing actions include bus reconnection and autonomous diagnosis; verify Global Bus availability.
- Gateway Handshake Failures
  - Validate JWT secret or Ed25519 public key; ensure client capability negotiation aligns with server expectations.
- Session State Stalls
  - Health monitor transitions to recovery or shutdown after repeated errors; check logs for root cause.
- Telemetry Export
  - Ensure Arize endpoint and credentials are set; fallback to no-op tracer if export fails.
- ServiceContainer Issues
  - Container maintained for backward compatibility; direct instantiation preferred in current architecture.
  - Monitor thread safety when accessing container from multiple coroutines.
- Agent Ecosystem Problems
  - Check agent registry for proper metadata registration; verify semantic fingerprint calculations.
  - Review agent_results.json for performance trends and error patterns.

**Section sources**
- [admin_api.py](file://core/services/admin_api.py#L94-L109)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L31-L60)
- [watchdog.py](file://core/services/watchdog.py#L128-L168)
- [gateway.py](file://core/infra/transport/gateway.py#L559-L617)
- [session_state.py](file://core/infra/transport/session_state.py#L378-L426)
- [telemetry.py](file://core/infra/telemetry.py#L35-L76)
- [service_container.py](file://core/infra/service_container.py#L32-L46)
- [registry.py](file://core/ai/agents/registry.py#L46-L82)
- [agent_results.json](file://agent_results.json#L1-L315)

## Conclusion
Aether Voice OS infrastructure combines a robust event-driven core, resilient transport and state management, cloud-native persistence and telemetry, autonomous monitoring, lifecycle orchestration, and a comprehensive agent ecosystem. The simplified architecture eliminates dependency injection overhead while maintaining clean component separation through direct instantiation patterns. The modular design enables extension, monitoring, and reliable operation across diverse deployment scenarios.

## Appendices

### Deployment Considerations
- Environment Variables
  - Configure logging level, package directory, and cloud credentials via environment or JSON fallback.
  - Set Redis host/port for Global Bus and Arize endpoint/API key for telemetry.
- Scaling Strategies
  - Horizontal scale Gateways behind a load balancer; use Redis for state synchronization.
  - Separate Admin API and Watchdog into dedicated processes or containers.
  - Scale agent ecosystem based on workload patterns; monitor agent_results.json for capacity planning.
- Operational Best Practices
  - Monitor Admin API health endpoint and Watchdog logs.
  - Enable telemetry in production; use batch processors for throughput.
  - Maintain package registry directory with proper permissions for hot-reload.
  - Regularly review agent_results.json for performance optimization opportunities.
  - Monitor agent ecosystem health through semantic fingerprint analysis and capability matching.

### ServiceContainer Usage Patterns
- Backward Compatibility: ServiceContainer maintained for legacy code support
- Thread Safety: ServiceContainer is thread-safe for concurrent access
- Error Handling: Container raises KeyError for unregistered services; implement proper error handling

### Agent Ecosystem Monitoring
- Track agent performance through agent_results.json metrics
- Monitor semantic fingerprint accuracy for agent matching
- Analyze optimization suggestions from OptimizationAgent
- Review learning insights for development workflow improvements
- Monitor security agent findings for vulnerability management