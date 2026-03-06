# Aether Cortex — Rust Acceleration Layer

## Scope

Aether Cortex is the Rust-backed performance layer under `cortex/src`, exposed to Python through PyO3 bindings and used as an acceleration path for DSP-critical routines.

## Module Layout

- `cortex/src/lib.rs`: Python module entrypoint and exports.
- `cortex/src/cochlea.rs`: lock-efficient buffering primitives.
- `cortex/src/synapse.rs`: fast VAD/energy-oriented computations.
- `cortex/src/axon.rs`: waveform boundary operations such as clean cut points.
- `cortex/src/thalamus.rs`: spectral/noise reduction primitives.

## Integration Contract

- Python runtime keeps functional fallbacks to maintain availability when Rust extension is unavailable.
- Rust routines are treated as acceleration helpers, not mandatory hard dependencies for startup.
- Input/output boundaries remain PCM-oriented and are marshaled through predictable numeric buffers.

## Build and Validation

- Local check: `cd cortex && cargo check`
- CI check is already included in the main pipeline (`aether_pipeline.yml`).

## Design Targets

- Keep latency stable under callback timing constraints.
- Keep memory allocations bounded and predictable.
- Prefer deterministic numerics where audio behavior depends on threshold comparisons.

## Change Safety Rules

- Any Rust-side interface change must preserve Python call compatibility.
- Any algorithmic change must be validated with benchmark and audio regression tests.
