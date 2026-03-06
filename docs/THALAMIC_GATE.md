# Thalamic Gate — Audio Control and Intervention Model

## Purpose

Thalamic Gate is the runtime control strategy that governs how incoming and outgoing audio are mediated to protect interaction quality under interruption, leakage, and variable room conditions.

## Core Responsibilities

- Gate microphone flow using adaptive voice-activity logic.
- Reduce feedback/leakage risks through mute/gain shaping.
- Support interruption behavior without destructive clipping artifacts.
- Feed paralinguistic and telemetry signals to the higher-level decision loop.

## Main Runtime Components

- `core/audio/capture.py`: callback-driven ingest, gating hooks, queue writes.
- `core/audio/processing.py`: adaptive VAD support and analysis helpers.
- `core/audio/paralinguistics.py`: expressive features for downstream logic.
- `core/audio/playback.py`: output queue drain and playback state alignment.

## Operational Behavior

1. Read input frame from capture callback.
2. Apply gate/mute strategy and maintain stable queue flow.
3. Emit affective and telemetry signals.
4. Forward eligible audio chunks to AI session input.
5. Coordinate interruption response with playback/output handling.

## Quality Targets

- Avoid queue overflows under normal session load.
- Minimize audible artifacts during mute/unmute transitions.
- Keep barge-in response predictable and fast.
- Keep telemetry lightweight enough for real-time use.

## Validation Touchpoints

- Unit and benchmark coverage in `tests/unit` and `tests/benchmarks`.
- Integration behavior through gateway/session tests where audio state affects transport events.
