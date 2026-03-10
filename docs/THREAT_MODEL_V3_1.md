# Aether Voice OS Threat Model (V3.1 Security Hardening)

This document outlines the security mitigations applied to the realtime voice and agent forging pipeline.

| Attack Vector | Impacted File(s) | Mitigation Strategy |
| :--- | :--- | :--- |
| **Cross-Site Scripting (XSS) / Payload Injection** | `apps/portal/src/components/forge/ForgeWizard.tsx`, `apps/portal/src/components/forge/widgets/ClawHubWidget.tsx` | Strict regex sanitization and length bounds applied to `name`, `role`, `tone`, and `skills` fields prior to WebSocket transmission. |
| **Credential Theft via LocalStorage** | `apps/portal/src/hooks/useAetherGateway.ts` | Ed25519 `seed` generation was migrated from `localStorage` persistence to an ephemeral, per-session in-memory keypair. |
| **Memory Extraction / Temporal Leakage** | `apps/portal/public/pcm-processor.js`, `apps/portal/src/hooks/useAetherGateway.ts` | Applied buffer zeroization (`.fill(0)`) to the audio ring buffer immediately after postMessage, and to cryptographic seed buffers after use. |
| **Runtime Prototype Pollution** | `apps/portal/public/pcm-processor.js` | Enforced `Object.freeze(PCMEncoderProcessor.prototype)` to prevent DOM or script modification attacks within the AudioWorklet. |
| **Unauthorized Tool Invocation** | `core/infra/transport/gateway.py` | Implemented strict deny-by-default capability checks for `forge_commit` and `claw_inject`. Requests without explicit authorization drop the connection. |
| **Malformed Payload DoS / Crashes** | `core/infra/transport/gateway.py`, `core/infra/transport/messages.py` | Added Pydantic schemas (`ForgeCommitPayload`, `ClawInjectPayload`) to forcefully validate expected types before parsing. |
| **CORS / Cross-Origin Websocket Hijacking** | `core/infra/transport/gateway.py` | Added explicit `Origin` validation within the WebSocket `/health` upgrade handler, pinning access to known secure origins (e.g., `localhost:3000`, `tauri://localhost`). |
| **Information Disclosure / Stack Trace Leakage** | `core/infra/transport/gateway.py` | Standardized `_send_error` to mask code `500+` tracebacks with a generic "Internal Server Error" message to prevent path and logic leakage. |

## Quick Verification Commands

### 1. Test Pytest Suite
```bash
python -m pytest tests/ -v
```

### 2. Verify Linting
```bash
ruff check core/ apps/portal/src/
```

### 3. Verify Types
```bash
cd apps/portal && npm run build
```
