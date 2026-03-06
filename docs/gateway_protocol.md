# 🛰️ Aether Gateway Protocol V2.1

> Canonical WebSocket contract between backend gateway and portal clients.
> Port: **18789** | Transport: **JSON control + binary audio** | Auth: **Ed25519 challenge-response**

## Connection Lifecycle

1. `connect.challenge` (server → client)
2. `connect.response` (client → server)
3. `connect.ack` (server → client)
4. steady-state event exchange (`tick`, `audio.chunk`, `transcript`, `interrupt`, `tool_result`, `engine_state`)

## Versioning

- Canonical protocol version: `2.1`.
- Every control-plane JSON message SHOULD include `version`.
- New clients MUST accept missing `version` (legacy `<=2.0`).
- New clients MUST accept both:
  - canonical payload envelope: `{ "type": "...", "version": "2.1", "payload": { ... } }`
  - legacy flat payloads: `{ "type": "...", "field": "..." }`

## Handshake Messages

### `connect.challenge` (S → C)

```json
{
  "type": "connect.challenge",
  "version": "2.1",
  "challenge": "7f8b...",
  "server_version": "2.1"
}
```

### `connect.response` (C → S)

```json
{
  "type": "connect.response",
  "version": "2.1",
  "client_id": "<ed25519-public-key-hex>",
  "signature": "<signature-hex>",
  "capabilities": ["audio.input", "audio.output", "tools.client"]
}
```

### `connect.ack` (S → C)

```json
{
  "type": "connect.ack",
  "version": "2.1",
  "session_id": "uuid",
  "granted_capabilities": ["audio.input"],
  "tick_interval_s": 15.0
}
```

## Canonical Runtime Event Schemas

### 1) `audio.chunk`

- Direction:
  - C → S: client microphone audio
  - S → C: optional base64 audio fallback when binary channel unavailable
- Canonical JSON form:

```json
{
  "type": "audio.chunk",
  "version": "2.1",
  "payload": {
    "mime_type": "audio/pcm;rate=16000",
    "data": "<base64-pcm-bytes>"
  }
}
```

- Binary fast path (recommended): raw PCM frame as WebSocket binary frame.

### 2) `transcript`

```json
{
  "type": "transcript",
  "version": "2.1",
  "payload": {
    "role": "ai",
    "text": "Let me check that for you."
  }
}
```

### 3) `interrupt`

```json
{
  "type": "interrupt",
  "version": "2.1",
  "payload": {
    "reason": "barge-in"
  }
}
```

### 4) `tool_result`

- Server → client (result display):

```json
{
  "type": "tool_result",
  "version": "2.1",
  "payload": {
    "call_id": "tool-call-123",
    "tool_name": "show_silent_hint",
    "status": "success",
    "result": "Refactor complete"
  }
}
```

- Client → server (tool response ack):

```json
{
  "type": "tool_result",
  "version": "2.1",
  "payload": {
    "call_id": "tool-call-123",
    "result": {
      "accepted": true
    }
  }
}
```

### 5) `engine_state`

```json
{
  "type": "engine_state",
  "version": "2.1",
  "payload": {
    "state": "LISTENING"
  }
}
```

Supported state values: `INITIALIZING`, `CONNECTED`, `LISTENING`, `THINKING`, `SPEAKING`, `HANDING_OFF`, `ERROR`, `INTERRUPTED`.

## Compatibility Rules

- Server accepts legacy client input formats:
  - binary audio frames (unchanged)
  - legacy Gemini passthrough audio format (`realtimeInput.mediaChunks`)
- Clients accept legacy server output formats:
  - top-level event fields without `payload`
  - no `version` field

This keeps older portal builds functional while enabling stricter contracts in V2.1.
