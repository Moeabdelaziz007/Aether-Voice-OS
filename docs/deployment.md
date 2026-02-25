# ☁️ Aether OS Deployment: Cloud-Native Scaling

## 🚀 Infrastructure Strategy

Aether OS is designed to be **Serverless-First**, utilizing Google Cloud Platform (GCP) for elastic scaling and zero-maintenance overhead.

## 📦 Containerization (Docker)

The Aether Engine is packaged as a high-performance Python container.

### Highlights

- **Base Image:** `python:3.11-slim`
- **Dependencies:** `portaudio19-dev`, `build-essential` (for Rust cortex hooks).
- **Optimization:** Multi-stage builds to keep the production image under 200MB.

## 🏗️ Cloud Run (Gen 2)

We deploy to Google Cloud Run for its native WebSocket support and request-based scaling.

### Key Configurations

- **Concurrency:** Set to `1` (Each instance handles one high-fidelity voice session for deterministic latency).
- **Session Affinity:** Enabled to maintain the stateful WebSocket connection.
- **Resources:** 2 vCPU / 4GB RAM (Necessary for smooth audio buffer management and local DSP).

## 🔐 Security & Secret Management

- **API Keys:** Stored in **Google Secret Manager** and injected as environment variables (`GOOGLE_API_KEY`).
- **Gateway Auth:** Ed25519 private keys are stored as secrets; only the public key is exposed for client verification.

## 🛠️ CI/CD Pipeline (Cloud Build)

Aether uses a "Push-to-Live" workflow:

1. `git push origin main`
2. **Cloud Build** triggers:
   - Linting & Unit Tests (`pytest`).
   - Image Build (`docker build`).
   - Push to **Artifact Registry**.
   - Deploy to **Cloud Run** (Green-Blue deployment).

## 📊 Monitoring & Observability

- **Log Explorer:** Structured JSON logs for tracing agent thought processes.
- **Cloud Trace:** Measuring end-to-end latency (Mic → Gemini → Speaker).
- **Alerting:** PagerDuty integration for consecutive 502/504 WebSocket errors.

## 🌍 Global Distribution

By leveraging **Firebase Hosting** for the Frontend and **GCP Regions** (e.g., `us-central1`, `asia-northeast1`) for the Engine, Aether achieves sub-200ms latency globally by routing users to the nearest neural node.
