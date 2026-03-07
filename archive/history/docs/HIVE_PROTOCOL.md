# Hive Protocol — Expert Handover and Coordination

## Purpose

Hive Protocol defines how Aether coordinates specialist experts, transfers context, and maintains continuity during multi-agent handovers.

## Main Building Blocks

- `core/ai/hive.py`: coordination entrypoint.
- `core/ai/handover_protocol.py`: handover data structures and validation flow.
- `core/ai/handover/manager.py`: orchestration logic for specialist transitions.
- `core/ai/handover_telemetry.py`: handover outcome metrics and reporting.
- `core/infra/transport/gateway.py`: transport-facing triggers and state propagation.

## Handover Flow

1. A handover request is raised with target specialist and reason.
2. Context is serialized into handover-safe payload.
3. Target expert session is pre-warmed when possible.
4. Active session transitions to handover state.
5. Success path commits target control; failure path rolls back safely.

## State and Safety Guarantees

- Session state transitions are explicit through state manager calls.
- Failed specialist stabilization must trigger deterministic rollback behavior.
- Handover metadata is retained for observability and debugging.

## Transport Coupling

- Gateway remains source of truth for client-facing session state.
- Frontend receives handover and engine-state updates as broadcast events.
- Handshake integrity and client auth remain independent from handover logic.

## Validation

- Integration paths are exercised in gateway and orchestration tests.
- Telemetry counters track pass/fail outcomes and checkpoint results.
