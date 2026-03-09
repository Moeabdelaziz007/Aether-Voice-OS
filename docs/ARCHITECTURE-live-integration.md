# Aether Voice OS - Gemini Live Integration Architecture

This document outlines the architectural updates made to fully integrate and harden the Gemini Live session within Aether Voice OS.

## Overview
The Gemini Live Integration updates the interaction pattern by:
1. **Multimodal Grounding:** Injecting temporal visual frames into the Gemini session via the gateway.
2. **Resilience:** Introducing exponential backoff reconnections, and token budget tracking to prevent failures.
3. **Structured Handoffs:** Implementing deep handover protocols allowing A2A communication without context loss.
4. **Safety Boundaries:** Wrapping the generative AI client initialization to enforce content generation bounds.

## Key Components

### `core/ai/session.py` (GeminiLiveSession)
Acts as the main AI "brain", handling realtime audio stream interactions directly with the Gemini model.
- **jsonschema Validation:** Tool declarations are checked using `jsonschema.Draft202012Validator.check_schema` before payload delivery.
- **Firestore Logging:** Deep handover events and token usages are transparently logged to Firestore for structured auditing.
- **Token Budget Tracking:** Allows capping tokens mid-session to limit resource consumption.

### `core/infra/transport/gateway.py`
The WebSocket single source of truth for connecting users with the backend.
- **Improved reconnect logic:** Added multi-attempt reconnection mechanism with exponential backoff on failure scenarios.
- **Handoff Mechanism:** Exposes a `request_handoff` workflow with `is_ready` health check assertions to protect against unstable states.

### Frontend Integration
Located in `apps/portal/src/hooks/useGeminiLive.ts` & `useAetherGateway.ts`
- **Vision Frame Streaming:** Added capability to periodically capture and transmit screen states to the backend via base64 encoding with back-pressure handling.
- **ACK mechanism:** Surfaces frame IDs into the WS stream to manage synchrony with Gemini.

## Deployment Setup

Ensure required environment variables (`GCP_SERVICE_KEY`, `FIRESTORE_PROJECT`, `GEMINI_API_KEY`) are present via a local `.env` or CI secret.

To run the full stack deployment to Google Cloud Run:
```bash
bash infra/deploy_cloudrun.sh
```

To run integration tests:
```bash
pytest tests/test_gemini_session.py
```