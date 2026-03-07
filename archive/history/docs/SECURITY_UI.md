# 🛡️ Security & Interface: The Shield and HUD

## 1. Overview: The Perimeter

AetherOS security (The Shield) ensures that only authorized entities can access the neural stream, while the Frontend HUD (AetherOrb) provides a transparent window into the system's "Cognition."

---

## 2. Neural Security (The Shield)

AetherOS implements a Zero-Trust communication layer between the Engine and external clients (HUD, Terminal, Mobile).

### A. Authentication Protocol

The `AetherGateway` handles a dual-mode handshake:

- **Primary: Ed25519 Challenge-Response**: Clients must sign a 32-byte cryptographic challenge using their private key. Verification is done against the Public Key stored in the `Agent Manifest`.
- **Secondary: JWT (JSON Web Tokens)**: Used for intra-service communication and ephemeral frontend sessions. Uses `AETHER_JWT_SECRET` (HS256).

### B. Capability Negotiation

During the handshake, clients negotiate capabilities:

- `audio_control`: Ability to interrupt or start the engine.
- `telemetry_view`: Access to internal latency and affective metrics.
- `tool_injection`: Ability to propose new tools to the Hive.

---

## 3. DevOps & Deployment

### A. Infrastructure as Code (IaC)

- **Dockerization**: AetherOS uses a multi-stage Docker build to keep the image slim (~800MB) while including the necessary PCM processing libraries (ffmpeg, libportaudio).
- **Container Orchestration**: `docker-compose` manages the Engine, Redis (Session Store), and the Admin API.

### B. CI/CD (GitHub Actions)

The `.github/workflows/` pipeline automates:

1. **Linting & Type-Checking**: Ruff + MyPy.
2. **Neural Audit**: Ensuring Hive handover logic passes the deterministic state test.
3. **Cloud Build**: Pushing the verified image to Google Artifact Registry.

---

## 4. Visual Interface (The AetherOrb HUD)

Aether is designed for "Zero-Interaction" efficiency. The UI is a diagnostic visualizer rather than a control panel.

### A. AetherOrb (15Hz Bio-Feedback)

The HUD visualizes the `affective_score` metrics broadcast from the `AudioManager`:

- **Orb Motion**: Represents the `rms_variance` (Excitement/Arousal).
- **Color Shift**: Maps `engagement_score` (Valence) to a neon spectrum (e.g., Deep Cyan to Neon Orchid).
- **Zen Mode**: A visual state for when Aether is actively listening without responding (Acoustic Empathy).

### B. The Whisper Layer (Ambient Transcript)

A real-time text stream of both user and system audio, allowing for silent "Over-the-Shoulder" monitoring of complex coding sessions.

---

## 5. Verification

- **JWT Expiry Tests**: Validating that stale tokens are rejected instantly.
- **Docker Boundary Audit**: Ensuring containers have no root privileges and minimal attack surface.
- **UI Latency Benchmark**: Verifying that the Orb visualizer maintains a steady 15Hz update rate even under high system load.
