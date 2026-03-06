# Aether Voice OS Agents

## Core

- AetherCore: primary orchestrator for voice pipeline and tool routing.
- ArchitectExpert: architecture and planning specialist.
- CodingExpert: implementation and debugging specialist.

## Runtime Roles

- Orchestrate session lifecycle across capture, Gemini session, gateway, and playback.
- Route tool calls through secure middleware and capability-aware dispatch.
- Coordinate handovers between specialists with context preservation.

## Identity Artifacts

- `brain/packages/*/manifest.json`: package identity and capabilities.
- `brain/packages/*/Soul.md`: persona and behavior profile.
- `brain/packages/*/Skills.md`: actionable skill definitions where present.

## Operational Notes

- Keep package manifests valid JSON and versioned.
- Keep soul and skills docs aligned with implemented capabilities.
- Do not commit secrets in agent manifests or soul definitions.
