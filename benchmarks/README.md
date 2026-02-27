# Aether Benchmarks: Performance & Fidelity Validation

This directory contains the automated benchmark suite used to verify AetherOS's "Zero-Friction" and "Competitive Edge" claims for the Gemini Live Agent Challenge 2026.

## ⚡ 1. Latency Benchmark (`bench_latency.py`)

Verifies the internal processing budget only. Excludes Gemini API, WebSocket transport, and Firebase latencies. Aether aims for sub-10ms overhead to leave 170ms+ for network and Gemini inference within the 180ms E2E goal.

**Results (Verified 2026-02-27, Internal Only):**

- **Avg Internal Latency:** 0.72 ms
- **p99 Latency:** 2.52 ms
- **Processing Budget Used:** 0.4%

**Execution:**

```bash
PYTHONPATH="." python3 benchmarks/bench_latency.py
```

## 🧠 2. Focus Accuracy Benchmark (`bench_focus.py`)

Evaluates the `ParalinguisticAnalyzer` against synthetic audio signatures to verify "Zen Mode" detection (Neural Shield).

**Targets:**

- **Accuracy:** >95% (Measured: 95.6% synthetic)
- **Precision:** 100%
- **Recall:** 89.3%
- **F1 Score:** 94.3%

**Execution:**

```bash
PYTHONPATH="." python3 benchmarks/bench_focus.py
```

**Real-World Dataset Mode:**

Set `AETHER_FOCUS_REAL_DATA_DIR` to a folder of 16kHz mono WAV files. Label
files by name: `zen_*.wav` or `typing_*.wav` (label 1), and `speech_*.wav`
or `silence_*.wav` (label 0).

## 🧬 3. DSP Performance (Cortex vs Simulation)

Comparative analysis of the Rust Synapse layer vs Python fallback.

**Key Metrics:**

- **Rust (Axon/Synapse):** 10-50x speedup in DSP operations.
- **VAD Stability:** Adaptive noise floor tracking (AdaptiveVAD).

---
*These benchmarks ensure that AetherOS isn't just a wrapper, but a high-performance Sovereign Engineer.*
