# 🚀 AetherOS Quickstart (Judge's Edition)

Welcome to the **AetherOS** production environment. This guide ensures you can launch and verify the agent for the **Gemini Live Agent Challenge 2026**.

## 1. Zero-Friction Environment (Auto-Fallback)

AetherOS is designed with a **"Resilient DSP"** architecture.

- **Rust Acceleration (Default)**: Uses the `aether-cortex` DSP layer (Rust) for sub-5ms VAD and Echo Cancellation.
- **NumPy Fallback (Auto)**: If the Rust binaries are not found or platform-incompatible, Aether strictly falls back to a high-performance **NumPy-based DSP** (DynamicAEC).

> [!NOTE]
> The system will run "Out of the box" on any standard Linux/macOS environment using the Python fallback if you do not wish to build the Rust layer.

## 2. Launching Locally (Docker)

The fastest way to witness the full stack:

```bash
# 1. Setup secrets
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 2. Fire up the Kernel
docker-compose up --build
```

The gateway will be available at `ws://localhost:18789`.

## 3. Building the Rust "ThalamicGate" (Optional)

For maximum performance (low-latency audio), build the Rust core:

```bash
cd core/audio/cortex
# Requires Rust (cargo) installed
cargo build --release

# The system will automatically detect the new binary in core/audio/cortex/target/release
```

## 4. Cloud Deployment (The "Cloud Strike")

We have provided a unified deployment script for Google Cloud:

```bash
./deploy.sh
```

This script:

1. Builds the backend container (including Rust compilation).
2. Deploys to **Google Cloud Run**.
3. Injects the live URL into the frontend.
4. Deploys the UI to **Firebase Hosting**.

## 5. Verification Checkpoints

- **Backend Status**: `curl <URL>/health` should return `{"status": "Aether Core Healthy"}`.
- **WebSocket Handshake**: Connect via the frontend and check the "SRE Heartbeat" HUD for p50 latency metrics.

---
*Aether Architect v2.0 — Scaling for the Moonshot.*
