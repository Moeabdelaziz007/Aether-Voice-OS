# Infrastructure and Services

<cite>
**Referenced Files in This Document**
- [config.py](file://core/infra/config.py)
- [admin_api.py](file://core/services/admin_api.py)
- [watchdog.py](file://core/services/watchdog.py)
- [lifecycle.py](file://core/infra/lifecycle.py)
- [state_manager.py](file://core/infra/state_manager.py)
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
This document describes the infrastructure and services layer of Aether Voice OS. It covers configuration management, cloud integration, transport and gateway services, event bus and state management, telemetry and observability, watchdog-based health monitoring and recovery, lifecycle orchestration, and operational guidance for deployment, scaling, and maintenance.

## Project Structure
The infrastructure and services layer spans several modules:
- Configuration and environment handling
- Transport and gateway for client connections
- Event bus and state machines for coordination
- Cloud persistence and telemetry
- Admin API for monitoring and control
- Watchdog for autonomous health checks and recovery
- Lifecycle manager for startup/shutdown orchestration
- Package registry for dynamic skill loading

```mermaid
graph TB
subgraph "Core Runtime"
CFG["Config Loader<br/>config.py"]
BUS["EventBus<br/>event_bus.py"]
STATE["State Manager<br/>state_manager.py"]
LIFE["Lifecycle Manager<br/>lifecycle.py"]
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
end
CFG --> ENG
ENG --> BUS
ENG --> GW
ENG --> ADMIN
ENG --> WD
ENG --> INFRA
GW --> SB
GW --> SS
SS --> BUS
FB --> ENG
TELE --> ENG
REG --> ENG
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
- [registry.py](file://core/services/registry.py#L44-L125)

## Architecture Overview
The system is built around an event-driven architecture with a central EventBus and a Global Bus for distributed state and pub/sub. The AetherGateway manages client sessions, integrates with the Global Bus for multi-node synchronization, and coordinates with the State Manager and Session State Manager. Cloud services (Firebase) provide persistence and telemetry, while the Admin API and Watchdog support monitoring and autonomous recovery.

```mermaid
graph TB
subgraph "Client Layer"
WS["WebSocket Clients"]
end
subgraph "Edge"
GW["AetherGateway<br/>gateway.py"]
SB["GlobalBus (Redis)<br/>bus.py"]
SS["Session State Manager<br/>session_state.py"]
end
subgraph "Core"
BUS["EventBus<br/>event_bus.py"]
SM["System State Manager<br/>state_manager.py"]
INF["Infra Manager<br/>logic/managers/infra.py"]
WD["Watchdog<br/>watchdog.py"]
ADMIN["Admin API<br/>admin_api.py"]
end
subgraph "Cloud"
FB["Firebase<br/>firebase/interface.py"]
TELE["Telemetry<br/>telemetry.py"]
end
WS --> GW
GW --> SB
GW --> SS
BUS --> SM
INF --> FB
INF --> WD
ADMIN --> BUS
TELE --> BUS
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

## Detailed Component Analysis

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

### Lifecycle Management
- LifecycleManager orchestrates boot and shutdown sequences, initializes the EventBus and state manager, and handles OS signals.

```mermaid
stateDiagram-v2
[*] --> BOOTING
BOOTING --> IDLE : "success"
IDLE --> LISTENING : "user speech"
LISTENING --> THINKING : "stream closed"
THINKING --> SPEAKING : "TTS start"
SPEAKING --> IDLE : "done"
IDLE --> PAUSED : "admin suspend"
PAUSED --> IDLE : "resume"
IDLE --> ERROR : "fatal"
ERROR --> BOOTING : "recovery"
```

**Diagram sources**
- [lifecycle.py](file://core/infra/lifecycle.py#L21-L86)
- [state_manager.py](file://core/infra/state_manager.py#L14-L38)

**Section sources**
- [lifecycle.py](file://core/infra/lifecycle.py#L21-L86)
- [state_manager.py](file://core/infra/state_manager.py#L14-L38)

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
  - Engine orchestrates EventBus, Gateway, Admin API, Watchdog, Infra Manager, and lifecycle.
- Cohesion
  - Each module encapsulates a focused responsibility: transport, state, cloud, telemetry, monitoring, lifecycle, and registry.
- External Dependencies
  - Redis for Global Bus, Firebase Admin SDK for cloud persistence, OpenTelemetry for tracing, websockets for transport.

```mermaid
graph LR
Engine["Engine"] --> EventBus["EventBus"]
Engine --> Gateway["AetherGateway"]
Engine --> Admin["Admin API"]
Engine --> Infra["Infra Manager"]
Infra --> Firebase["FirebaseConnector"]
Infra --> Watchdog["SREWatchdog"]
Gateway --> GlobalBus["GlobalBus (Redis)"]
Gateway --> SessionState["Session State Manager"]
EventBus --> SystemState["System State Manager"]
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

[No sources needed since this section provides general guidance]

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

**Section sources**
- [admin_api.py](file://core/services/admin_api.py#L94-L109)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L31-L60)
- [watchdog.py](file://core/services/watchdog.py#L128-L168)
- [gateway.py](file://core/infra/transport/gateway.py#L559-L617)
- [session_state.py](file://core/infra/transport/session_state.py#L378-L426)
- [telemetry.py](file://core/infra/telemetry.py#L35-L76)

## Conclusion
Aether Voice OS infrastructure combines a robust event-driven core, resilient transport and state management, cloud-native persistence and telemetry, autonomous monitoring, and lifecycle orchestration. The modular design enables extension, monitoring, and reliable operation across diverse deployment scenarios.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Deployment Considerations
- Environment Variables
  - Configure logging level, package directory, and cloud credentials via environment or JSON fallback.
  - Set Redis host/port for Global Bus and Arize endpoint/API key for telemetry.
- Scaling Strategies
  - Horizontal scale Gateways behind a load balancer; use Redis for state synchronization.
  - Separate Admin API and Watchdog into dedicated processes or containers.
- Operational Best Practices
  - Monitor Admin API health endpoint and Watchdog logs.
  - Enable telemetry in production; use batch processors for throughput.
  - Maintain package registry directory with proper permissions for hot-reload.

[No sources needed since this section provides general guidance]