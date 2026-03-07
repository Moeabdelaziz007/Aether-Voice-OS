# 🧪 AetherOS: Testing Matrix (Verification Strategy)

> **"AetherOS is verified, not just tested."**
> A multi-layered verification strategy ensures p95 latency targets and cross-session stability.

---

## 🏗️ 1. Architecture of Verification

AetherOS follows a **Strict Tiered Testing** model:

| Tier | Focus | Tooling |
| :--- | :--- | :--- |
| **Unit** | Core Logic & Math | `pytest tests/unit` |
| **Integration** | Bus & Cloud Connectivity | `pytest tests/integration` |
| **E2E Audit** | User-perceived Latency | `scripts/benchmark.py` |
| **Stress** | Stability & Memory Pressure | `scripts/stability_test.py` |

---

## ⚡ 2. Performance Benchmarks

To prove "First Principles" efficiency, all major structural changes must undergo a **Performance Audit**.

### Latency Tracing (p50/p95/p99)

Run the automated benchmark suite:

```bash
python scripts/benchmark.py --iterations 10
```

- **Target p50**: < 200ms (Internal Engine)
- **Target p95**: < 500ms (End-to-End)

### Thalamic Gate Accuracy (F1 Score)

We use synthetic audio probes to measure "Barge-in" precision.

- **Goal**: 95% accuracy in distinguishing user speech from AI echo leakage.

---

## 🧠 3. Multi-Agent Handover Verification

Verified via `tests/e2e/test_e2e_singularity.py`. We test:

1. **Context Continuity**: Confirming that Agent B knows exactly what Agent A was doing.
2. **Switch Latency**: Measuring the time between `REQUEST_HANDOVER` and `HANDOVER_COMPLETE`.
3. **Integrity**: Verifying Ed25519 signatures across the gateway during the transition.

---

## 🔐 4. Security Audits

We use `bandit` and `ruff` for automated security scanning:

```bash
# Security check
bandit -r core/

# Linting & Type Consistency
ruff check .
```

---

## 🚧 5. Chaos Engineering (SRE)

**Port Flipping**:

- **Test**: Force-bind port 18790 with another process.
- **Expected**: AetherOS should detect `OSError: [Errno 48]` and dynamically shift to a backup port without crashing.

**Redis Disconnect**:

- **Test**: Kill the local Redis server during an active session.
- **Expected**: The Global Bus should log a failure and enter a **Retry State** without interrupting the primary Gemini audio stream.
