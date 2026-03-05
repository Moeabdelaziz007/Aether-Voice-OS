# Agent Management System

<cite>
**Referenced Files in This Document**
- [integrated.py](file://core/ai/agents/integrated.py)
- [proactive.py](file://core/ai/agents/proactive.py)
- [bridge.py](file://core/ai/agents/bridge.py)
- [registry.py](file://core/ai/agents/registry.py)
- [router.py](file://core/ai/router.py)
- [hive.py](file://core/ai/hive.py)
- [manager.py](file://core/ai/handover/manager.py)
- [handover_protocol.py](file://core/ai/handover_protocol.py)
- [architect.py](file://core/ai/agents/specialists/architect.py)
- [debugger.py](file://core/ai/agents/specialists/debugger.py)
- [security.py](file://core/utils/security.py)
- [admin_api.py](file://core/services/admin_api.py)
- [Skills.md](file://brain/personas/Skills.md)
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
This document describes the Agent Management System that powers the Aether Voice OS. It covers agent registration, task orchestration, proactive intervention, and the integrated agent architecture. It explains the bridge agent system for cross-agent communication and task delegation, the proactive agent functionality for autonomous task initiation and context-aware interventions, and the hive swarm intelligence system for collective agent coordination and distributed decision-making. It also documents agent specialization patterns, personality configurations, expertise domains, lifecycle management, handover protocols, security, resource management, and fault tolerance. Guidance is included for developing custom agents and extending the agent ecosystem.

## Project Structure
The Agent Management System spans several modules:
- Agent orchestration and integration: Integrated agent pipeline, proactive intervention, and bridge to external tooling.
- Specialized agents: Architect Expert and Debugger, coordinated via the Deep Handover Protocol.
- Hive coordinator: Centralized orchestration with deep handover, negotiation, validation checkpoints, and rollback.
- Routing and registry: Intelligent routing of intents to the best agent and centralized agent registry.
- Security and admin: Signature verification utilities and a local admin API for telemetry and system state.

```mermaid
graph TB
subgraph "Agent Orchestration"
IA["IntegratedAetherAgent"]
BR["ADKGeminiBridge"]
PR["ProactiveInterventionEngine"]
CA["CodeAwareProactiveAgent"]
end
subgraph "Specialists"
AR["ArchitectAgent"]
DG["DebuggerAgent"]
end
subgraph "Hive Coordination"
HC["HiveCoordinator"]
MAO["MultiAgentOrchestrator"]
end
subgraph "Routing & Registry"
IR["IntelligenceRouter"]
REG["AgentRegistry"]
end
subgraph "Security & Admin"
SEC["Security Utils"]
ADM["AdminAPIServer"]
end
IA --> BR
IA --> PR
PR --> CA
AR --> MAO
DG --> MAO
MAO --> HC
IR --> REG
HC --> REG
HC --> MAO
SEC --> HC
ADM --> HC
```

**Diagram sources**
- [integrated.py](file://core/ai/agents/integrated.py#L15-L66)
- [bridge.py](file://core/ai/agents/bridge.py#L7-L35)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L125)
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L133)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L139)
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [router.py](file://core/ai/router.py#L14-L84)
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [security.py](file://core/utils/security.py#L18-L71)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)

**Section sources**
- [integrated.py](file://core/ai/agents/integrated.py#L15-L66)
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [router.py](file://core/ai/router.py#L14-L84)
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [security.py](file://core/utils/security.py#L18-L71)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)

## Core Components
- IntegratedAetherAgent: Master wrapper that composes the voice pipeline, proactive intervention, code-aware proactive agent, ADK bridge, and latency optimizer.
- ProactiveInterventionEngine: Emotion-driven intervention engine that detects frustration and triggers empathetic responses.
- CodeAwareProactiveAgent: Context-aware agent that suggests tools for investigation during interventions.
- ADKGeminiBridge: Routes tool calls from Gemini sessions to ADK agents and tracks semantic recovery.
- HiveCoordinator: Orchestrates the hive with deep handover protocol, negotiation, validation checkpoints, and rollback.
- MultiAgentOrchestrator: Manages handovers between specialists, validation checkpoints, and telemetry.
- ArchitectAgent and DebuggerAgent: Specialized agents that collaborate via the deep handover protocol for design and verification.
- IntelligenceRouter and AgentRegistry: Route intents to the best agent and manage agent identities and capabilities.
- Security utilities and Admin API: Provide cryptographic verification and expose system telemetry.

**Section sources**
- [integrated.py](file://core/ai/agents/integrated.py#L15-L66)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L125)
- [bridge.py](file://core/ai/agents/bridge.py#L7-L35)
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L133)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L139)
- [router.py](file://core/ai/router.py#L14-L84)
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [security.py](file://core/utils/security.py#L18-L71)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)

## Architecture Overview
The system integrates voice processing, proactive intervention, and specialized agents behind a unified orchestration layer. The HiveCoordinator coordinates deep handovers with negotiation, validation checkpoints, and rollback. The MultiAgentOrchestrator delegates tasks to specialists and preserves context across transitions. The IntelligenceRouter selects the best agent based on intent semantics and keyword rules, while the AgentRegistry maintains agent identities and capabilities.

```mermaid
sequenceDiagram
participant User as "User"
participant IA as "IntegratedAetherAgent"
participant PR as "ProactiveInterventionEngine"
participant CA as "CodeAwareProactiveAgent"
participant BR as "ADKGeminiBridge"
participant HC as "HiveCoordinator"
participant MAO as "MultiAgentOrchestrator"
participant AR as "ArchitectAgent"
participant DG as "DebuggerAgent"
User->>IA : "Audio stream"
IA->>PR : "Emotion scores"
PR-->>IA : "Intervention decision"
alt Intervention triggered
IA->>CA : "Get investigation tools"
CA-->>IA : "Tool suggestions"
end
IA->>BR : "Route tool call"
BR->>MAO : "Collaborate(task)"
MAO->>AR : "Handover with context"
AR->>DG : "Handover with context"
DG-->>AR : "Feedback / rework"
AR-->>MAO : "Final result"
MAO-->>BR : "Handover result"
BR-->>IA : "Stream response"
IA-->>User : "Response"
```

**Diagram sources**
- [integrated.py](file://core/ai/agents/integrated.py#L39-L61)
- [proactive.py](file://core/ai/agents/proactive.py#L60-L83)
- [bridge.py](file://core/ai/agents/bridge.py#L17-L31)
- [manager.py](file://core/ai/handover/manager.py#L581-L631)
- [architect.py](file://core/ai/agents/specialists/architect.py#L116-L132)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L195-L234)

## Detailed Component Analysis

### Integrated Agent Pipeline
The IntegratedAetherAgent initializes and coordinates:
- VoiceAgent streaming and emotion extraction
- ProactiveInterventionEngine for empathy-driven interventions
- CodeAwareProactiveAgent for context-aware tool suggestions
- ADKGeminiBridge for tool routing
- LatencyOptimizer for performance tracking

```mermaid
classDiagram
class IntegratedAetherAgent {
+process_audio_chunk(pcm_chunk)
+shutdown()
}
class ProactiveInterventionEngine {
+should_intervene(valence, arousal)
+calculate_frustration(valence, arousal)
+generate_empathetic_message()
}
class CodeAwareProactiveAgent {
+get_investigation_tools()
}
class ADKGeminiBridge {
+route_tool_call(tool_name, arguments)
+reset_recovery_state()
}
class MultiAgentOrchestrator {
+collaborate(task, agents)
}
IntegratedAetherAgent --> ProactiveInterventionEngine : "uses"
IntegratedAetherAgent --> CodeAwareProactiveAgent : "registers"
IntegratedAetherAgent --> ADKGeminiBridge : "bridges"
ADKGeminiBridge --> MultiAgentOrchestrator : "routes"
```

**Diagram sources**
- [integrated.py](file://core/ai/agents/integrated.py#L25-L38)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L89)
- [bridge.py](file://core/ai/agents/bridge.py#L13-L31)
- [manager.py](file://core/ai/handover/manager.py#L581-L631)

**Section sources**
- [integrated.py](file://core/ai/agents/integrated.py#L15-L66)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L125)
- [bridge.py](file://core/ai/agents/bridge.py#L7-L35)
- [manager.py](file://core/ai/handover/manager.py#L581-L631)

### Proactive Intervention Engine
The ProactiveInterventionEngine:
- Computes frustration from acoustic valence/arousal
- Applies dynamic baselines and thresholds
- Enforces cooldowns
- Generates empathetic messages

```mermaid
flowchart TD
Start(["Emotion Input"]) --> Calc["Compute Frustration Score"]
Calc --> Thresh{"Exceeds Threshold?"}
Thresh --> |No| End(["No Intervention"])
Thresh --> |Yes| Cooldown{"Cooldown Passed?"}
Cooldown --> |No| End
Cooldown --> |Yes| Message["Generate Empathetic Message"]
Message --> Log["Log Intervention"]
Log --> End
```

**Diagram sources**
- [proactive.py](file://core/ai/agents/proactive.py#L30-L83)

**Section sources**
- [proactive.py](file://core/ai/agents/proactive.py#L10-L125)

### Code-Aware Proactive Agent
The CodeAwareProactiveAgent suggests investigation tools during interventions, including codebase search and screenshot capture.

**Section sources**
- [proactive.py](file://core/ai/agents/proactive.py#L92-L125)

### Bridge Agent System
The ADKGeminiBridge:
- Receives tool calls from Gemini
- Routes them to the orchestrator
- Tracks semantic recovery

**Section sources**
- [bridge.py](file://core/ai/agents/bridge.py#L7-L35)

### Hive Swarm Intelligence
The HiveCoordinator:
- Tracks the active “soul” (expert)
- Finds the best expert for a task
- Manages rich context transfer, pre/post validation, and rollback
- Integrates neural summarization and genetic evolution

```mermaid
classDiagram
class HiveCoordinator {
+request_handoff(target_name, task_context)
+prepare_handoff(target_name, task, payload, code_context, enable_negotiation)
+complete_handoff(handover_id, validation_results)
+rollback_handover(handover_id)
+evaluate_intent(query)
}
class MultiAgentOrchestrator {
+register_agent(name, agent)
+handover_with_context(from_agent, to_agent, context, enable_negotiation)
+create_validation_checkpoint(handover_id, stage, partial_output)
+negotiate_handover(handover_id, action, ...)
+collaborate(task, primary_agent)
}
class HandoverContext {
+add_history(action, agent)
+create_snapshot()
+restore_snapshot()
+add_task_node(description, parent_id, assigned_to)
+complete_task_node(node_id)
}
HiveCoordinator --> MultiAgentOrchestrator : "coordinates"
MultiAgentOrchestrator --> HandoverContext : "manages"
```

**Diagram sources**
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L107-L246)

**Section sources**
- [hive.py](file://core/ai/hive.py#L47-L723)
- [manager.py](file://core/ai/handover/manager.py#L207-L631)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L107-L246)

### Specialized Agents: Architect and Debugger
ArchitectAgent:
- Builds architectural blueprints
- Adds decisions, risks, and task nodes
- Requests Debugger verification via deep handover

DebuggerAgent:
- Verifies designs and identifies issues
- Produces warnings and proposed fixes
- Requests rework when necessary

```mermaid
sequenceDiagram
participant AR as "ArchitectAgent"
participant MAO as "MultiAgentOrchestrator"
participant DG as "DebuggerAgent"
AR->>MAO : "Handover with ArchitectOutput"
MAO->>DG : "Transfer context"
DG->>DG : "Verify blueprint"
alt Issues found
DG-->>MAO : "DebuggerOutput with warnings/fixes"
MAO-->>AR : "Rework handover"
else Approved
DG-->>MAO : "Approved output"
MAO-->>AR : "Final result"
end
```

**Diagram sources**
- [architect.py](file://core/ai/agents/specialists/architect.py#L35-L132)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L34-L139)
- [manager.py](file://core/ai/handover/manager.py#L53-L165)

**Section sources**
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L189)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L272)
- [manager.py](file://core/ai/handover/manager.py#L37-L205)

### Agent Registration and Routing
AgentRegistry:
- Stores agent metadata, capabilities, and semantic fingerprints
- Supports discovery by capability and unregistration

IntelligenceRouter:
- Keyword-based routing for system commands
- Semantic similarity routing using embeddings
- Fallback to the orchestrator

```mermaid
classDiagram
class AgentRegistry {
+register_agent(metadata)
+find_agents_by_capability(capability)
+list_all_agents()
+unregister_agent(agent_id)
}
class IntelligenceRouter {
+route_intent(user_intent, embedding)
}
AgentRegistry <.. IntelligenceRouter : "uses"
```

**Diagram sources**
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [router.py](file://core/ai/router.py#L14-L84)

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [router.py](file://core/ai/router.py#L14-L84)

### Agent Lifecycle Management
Lifecycle encompasses initialization, task assignment, collaboration, and termination:
- Initialization: IntegratedAetherAgent and HiveCoordinator construct orchestrators and registries.
- Task Assignment: IntelligenceRouter selects the best agent; MultiAgentOrchestrator delegates via deep handover.
- Collaboration: Architect and Debugger exchange validated outputs with checkpoints and rework handovers.
- Termination: Handover completion, telemetry recording, and cleanup.

**Section sources**
- [integrated.py](file://core/ai/agents/integrated.py#L25-L38)
- [hive.py](file://core/ai/hive.py#L111-L124)
- [manager.py](file://core/ai/handover/manager.py#L262-L394)

### Handover Protocol Details
The Deep Handover Protocol defines:
- HandoverContext with rich metadata, task trees, working memory, and snapshots
- ArchitectOutput and DebuggerOutput schemas
- Negotiation, validation checkpoints, and rollback
- Serialization and diff utilities

```mermaid
classDiagram
class HandoverContext {
+history : str[]
+payload : Dict
+intent_confidence : IntentConfidence
+code_context : CodeContext
+add_history(action, agent)
+create_snapshot()
+restore_snapshot()
+add_task_node(...)
+complete_task_node(...)
}
class ArchitectOutput {
+blueprints : BlueprintSection[]
+decisions : ArchitectDecision[]
+risk_assessment : RiskAssessment[]
}
class DebuggerOutput {
+verification_results : VerificationResult[]
+fixes : CodeFix[]
+warnings : DebuggerWarning[]
}
class HandoverNegotiation {
+propose_terms(scope, deliverables, deadline)
+counter_terms(...)
+accept_terms()
+reject_terms(reason)
}
class ValidationCheckpoint {
+stage : str
+partial_output : Dict
+add_validation(result)
}
HandoverContext --> ArchitectOutput : "carries"
HandoverContext --> DebuggerOutput : "carries"
HandoverContext --> HandoverNegotiation : "supports"
HandoverContext --> ValidationCheckpoint : "creates"
```

**Diagram sources**
- [handover_protocol.py](file://core/ai/handover_protocol.py#L107-L246)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L284-L381)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L421-L457)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L583-L728)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L525-L570)

**Section sources**
- [handover_protocol.py](file://core/ai/handover_protocol.py#L107-L800)

### Security and Fault Tolerance
Security:
- Ed25519 signature verification and keypair generation for agent identity and integrity.

Fault Tolerance:
- Snapshot/rollback capability in HandoverContext
- Validation checkpoints for iterative refinement
- Telemetry and analytics reporting
- Admin API for monitoring system state

**Section sources**
- [security.py](file://core/utils/security.py#L18-L71)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L175-L198)
- [manager.py](file://core/ai/handover/manager.py#L395-L464)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)

### Examples and Use Cases
- Agent Creation: Register agents via AgentRegistry and bootstrap defaults.
- Task Routing: Use IntelligenceRouter to select the best agent based on intent.
- Performance Monitoring: Observe telemetry via Admin API endpoints.
- Proactive Intervention: Trigger empathetic responses when frustration thresholds are met.
- Handover: Architect hands off to Debugger with rich context and negotiation support.

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L78-L98)
- [router.py](file://core/ai/router.py#L22-L48)
- [admin_api.py](file://core/services/admin_api.py#L37-L74)
- [proactive.py](file://core/ai/agents/proactive.py#L60-L83)
- [manager.py](file://core/ai/handover/manager.py#L262-L394)

## Dependency Analysis
The system exhibits layered dependencies:
- Orchestration depends on routing and registry
- HiveCoordinator depends on the handover protocol and telemetry
- Specialized agents depend on the orchestrator and protocol models
- Bridge connects external tooling to the orchestrator

```mermaid
graph LR
REG["AgentRegistry"] --> IR["IntelligenceRouter"]
IR --> HC["HiveCoordinator"]
HC --> MAO["MultiAgentOrchestrator"]
MAO --> AR["ArchitectAgent"]
MAO --> DG["DebuggerAgent"]
IA["IntegratedAetherAgent"] --> BR["ADKGeminiBridge"]
BR --> MAO
PR["ProactiveInterventionEngine"] --> IA
CA["CodeAwareProactiveAgent"] --> IA
```

**Diagram sources**
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [router.py](file://core/ai/router.py#L14-L84)
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L133)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L139)
- [integrated.py](file://core/ai/agents/integrated.py#L25-L38)
- [bridge.py](file://core/ai/agents/bridge.py#L13-L31)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L89)
- [proactive.py](file://core/ai/agents/proactive.py#L92-L125)

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L30-L98)
- [router.py](file://core/ai/router.py#L14-L84)
- [hive.py](file://core/ai/hive.py#L47-L124)
- [manager.py](file://core/ai/handover/manager.py#L207-L394)
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L133)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L139)
- [integrated.py](file://core/ai/agents/integrated.py#L25-L38)
- [bridge.py](file://core/ai/agents/bridge.py#L13-L31)
- [proactive.py](file://core/ai/agents/proactive.py#L10-L125)

## Performance Considerations
- Latency tracking: IntegratedAetherAgent records pipeline latency for optimization.
- Neural summarization: Context compression reduces handover overhead.
- Telemetry: Comprehensive metrics and analytics for performance insights.
- Pre-warming: Speculative warming for zero-friction handovers.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Handover Preparation Failed: Check agent availability and protocol readiness.
- Validation Failures: Review checkpoints and adjust deliverables.
- Rollback Required: Use snapshot/rollback to revert to a stable state.
- Signature Verification Errors: Confirm Ed25519 keys and signatures.

**Section sources**
- [manager.py](file://core/ai/handover/manager.py#L309-L394)
- [manager.py](file://core/ai/handover/manager.py#L434-L464)
- [handover_protocol.py](file://core/ai/handover_protocol.py#L175-L198)
- [security.py](file://core/utils/security.py#L18-L56)

## Conclusion
The Agent Management System integrates voice processing, proactive intervention, and specialized agents under a robust hive coordination layer. The Deep Handover Protocol enables rich context preservation, negotiation, validation, and rollback. The registry and router ensure intelligent agent selection, while security and admin utilities provide integrity and observability. Together, these components form a scalable, fault-tolerant, and context-aware agent ecosystem.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Agent Specialization Patterns and Expertise Domains
- ArchitectExpert: High-level system design, blueprint creation, risk assessment.
- Debugger: Structural verification, warnings, and proposed fixes.
- Coder Agent: Code generation, debugging, refactoring.
- Orchestrator: Global task routing and state management.

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L78-L98)
- [architect.py](file://core/ai/agents/specialists/architect.py#L20-L133)
- [debugger.py](file://core/ai/agents/specialists/debugger.py#L20-L139)

### Personality Configurations and Capabilities
- Personality: System prompts define agent roles and behaviors.
- Capabilities: List of skills for discovery and routing.
- Tools: Agent-defined tool sets for task execution.

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L11-L24)
- [registry.py](file://core/ai/agents/registry.py#L78-L98)

### Resource Management and Fault Tolerance
- Context Compression: Reduces payload sizes for handovers.
- Validation Checkpoints: Enable iterative refinement and rollback.
- Telemetry Export: Analytics and performance reporting.
- Admin API: Local monitoring and diagnostics.

**Section sources**
- [hive.py](file://core/ai/hive.py#L254-L262)
- [manager.py](file://core/ai/handover/manager.py#L395-L433)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)

### Developing Custom Agents and Extending the Ecosystem
- Define AgentMetadata with capabilities and system prompt.
- Register the agent with the registry.
- Implement process() to handle HandoverContext.
- Integrate with MultiAgentOrchestrator for handovers.
- Use the Admin API for monitoring and telemetry.

**Section sources**
- [registry.py](file://core/ai/agents/registry.py#L11-L51)
- [manager.py](file://core/ai/handover/manager.py#L231-L261)
- [admin_api.py](file://core/services/admin_api.py#L88-L117)
- [Skills.md](file://brain/personas/Skills.md#L1-L20)