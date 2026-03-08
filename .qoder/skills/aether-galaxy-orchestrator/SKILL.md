---
name: aether-galaxy-orchestrator
description: Orchestrate multi-agent AI workflows using gravity-based routing, circuit breakers, and policy enforcement. Use when coordinating multiple AI agents, routing tasks to specialized agents, or implementing fault-tolerant agent collaboration.
---

# Aether Galaxy Orchestrator

## Overview

This skill implements the Galaxy Orchestration System from Aether OS v3.0 - a sophisticated multi-agent coordination framework using gravity-based scoring for intelligent task routing.

## When to Use

Use this skill when:
- You need to coordinate multiple specialized AI agents
- Tasks require dynamic routing based on capabilities, latency, and load
- You need fault tolerance with circuit breaker fallbacks
- Implementing agent-to-agent handoff protocols
- Building resilient multi-agent workflows

## Core Components

### 1. GravityRouter

Routes tasks to optimal "planets" (AI agents) using weighted scoring:

```python
# Gravity Score Formula
score = (
    0.35 * capability_match      # Does agent have required capabilities?
    + 0.25 * confidence           # How confident is the agent?
    - 0.15 * normalized_latency   # Lower latency is better
    - 0.15 * load                 # Lower load is better
    + 0.10 * continuity           # Bonus for recently used agents
)
```

**Usage**:
```python
from core.ai.handover.gravity_router import GravityRouter

router = GravityRouter()
best_agent = router.route_task(
    task="Debug this Python error",
    candidates=[agent1, agent2, agent3]
)
```

### 2. FallbackStrategy

Circuit breaker pattern for resilience:

- **Opens after**: 3 consecutive hard failures
- **Max retry budget**: 2 retries per task node
- **Activates**: Fallback agents when primary fails

**Usage**:
```python
from core.ai.handover.fallback_strategy import FallbackStrategy

fallback = FallbackStrategy()
if not primary_success:
    fallback_agent = fallback.activate(context)
```

### 3. GalaxyPolicyEnforcer

Enforces domain/capability policies:

- Domain allowlist validation
- Capability verification
- Latency threshold (<500ms)
- Load limit (<0.9)

**Usage**:
```python
from core.ai.handover.policy_enforcer import GalaxyPolicyEnforcer

enforcer = GalaxyPolicyEnforcer()
if enforcer.validate(agent, task):
    proceed_with_routing()
```

## Agent Types (Planets)

### Architect Agent
**Capabilities**: `design.create`, `blueprint.generate`, `risk.assess`
**Use for**: System design, architecture planning, blueprint generation

### Debugger Agent
**Capabilities**: `debug.analyze`, `verify.design`, `risk.assess`
**Use for**: Error analysis, code verification, debugging

### CodingExpert Agent
**Capabilities**: `code.write`, `code.review`, `refactor`
**Use for**: Implementation, code review, refactoring

## Workflow Patterns

### Task Routing Workflow

```markdown
1. Extract required capabilities from task
2. Filter agents by domain allowlist
3. Calculate gravity scores for candidates
4. Select highest-scoring agent
5. Monitor execution with circuit breaker
6. Activate fallback if needed
```

### Handoff Protocol

```markdown
1. Source agent completes subtask
2. Update HandoverContext with results
3. Router selects next agent
4. Transfer context with continuity bonus
5. Target agent acknowledges receipt
6. Continue execution
```

## Configuration

### AetherConfig Settings

```python
GALAXY_CONFIG = {
    'gravity_weights': {
        'capability': 0.35,
        'confidence': 0.25,
        'latency': -0.15,
        'load': -0.15,
        'continuity': 0.10
    },
    'circuit_breaker': {
        'failure_threshold': 3,
        'retry_budget': 2,
        'timeout_seconds': 30
    },
    'policy': {
        'latency_threshold_ms': 500,
        'load_threshold': 0.9,
        'domain_allowlist': ['Architect', 'Debugger', 'CodingExpert']
    }
}
```

## Testing

### Unit Tests

```python
def test_gravity_routing():
    router = GravityRouter()
    candidate = PlanetCandidate(
        planet_id="Debugger",
        capabilities=["debug.analyze"],
        confidence=0.95,
        latency_ms=50.0,
        load=0.2,
        continuity_bonus=0.8,
    )
    score = router.calculate_gravity_score(candidate)
    assert score > 0.6  # Expected: 0.6225
```

### Integration Tests

```python
def test_multi_agent_handoff():
    orchestrator = MultiAgentOrchestrator()
    result = orchestrator.execute_task(
        task="Design and implement authentication",
        agents=["Architect", "CodingExpert"]
    )
    assert result.success
    assert len(result.handoffs) >= 1
```

## Performance Metrics

- **Routing Latency**: <50ms average
- **Circuit Breaker Response**: Opens within 100ms of 3rd failure
- **Fallback Activation**: <200ms
- **Success Rate**: >95% with fallback enabled

## Troubleshooting

### Issue: Agent Not Selected

**Check**:
1. Domain allowlist includes agent
2. Capabilities match task requirements
3. Policy enforcer not blocking

### Issue: Circuit Breaker Opens Frequently

**Solutions**:
1. Increase failure threshold (default: 3)
2. Improve agent error handling
3. Add more fallback agents

### Issue: Low Gravity Scores

**Optimize**:
1. Reduce agent latency
2. Balance load across agents
3. Improve capability matching

## Examples

### Example 1: Debugging Workflow

```python
# User: "Fix this TypeError in the authentication module"
context = HandoverContext(
    task="Fix TypeError in authentication",
    source_planet="User"
)

# Router selects Debugger (highest gravity: 0.72)
# Debugger analyzes error, verifies fix needed
# Router routes to CodingExpert for implementation (gravity: 0.68)
# CodingExpert writes fix, commits code
```

### Example 2: Design + Implementation

```python
# User: "Create a REST API for user management"
context = HandoverContext(
    task="Create REST API for user management",
    source_planet="User"
)

# Router selects Architect (gravity: 0.81)
# Architect creates API blueprint
# Router routes to CodingExpert (gravity: 0.75)
# CodingExpert implements endpoints
```

## Related Resources

- [Galaxy Orchestration Guide](docs/GALAXY_ORCHESTRATION.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)
- [Multi-Agent Collaboration Patterns](plans/aether-v3-living-workspace-plan.md)

## Security Considerations

- Validate all agent inputs
- Enforce domain allowlists strictly
- Monitor for anomalous behavior
- Implement rate limiting per agent
- Audit all handoff transactions
