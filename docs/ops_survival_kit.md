# 🛠️ AetherOS: Ops Survival Kit (SRE Guide)

> **"If it breaks, don't restart. Re-architect."**
> A common set of solutions for operational issues encountered during AetherOS deployment and scaling.

---

## 🏗️ 1. Infrastructure Diagnostics

### 📡 Port 18790: Address already in use

The `AdminAPIServer` defaults to port 18790. If this port is occupied:

- **Solution**: The engine now includes a **Dynamic Fallback** mechanism. It will automatically attempt a random available port and log the new URL.
- **Manual Kill**: `lsof -ti:18790 | xargs kill -9`

### 🔄 Redis Global Bus: Connection Timeout

If you see `A2A [BUS] Connection failed`:

- **Cause**: Redis server is either down or refusing connections on the standard port (6379).
- **Check**: `redis-cli ping` should return `PONG`.
- **Tuning**: Ensure `AETHER_REDIS_HOST` in `.env` matches your environment (Docker vs Local).

---

## 🔥 2. Firebase & Cloud Integration

### 🚫 Cloud Firestore API Disabled

**Error**: `Cloud Firestore API has not been used in project... or it is disabled.`

- **Quick Fix**:
  1. Visit the Google Cloud Console Link provided in the log.
  2. Click **Enable**.
  3. Wait 5 minutes for DNA (Domain Neural Activation) to propagate.

### 🔑 Authentication Failures

**Error**: `connect.challenge failed` / `AUTH_FAILED`

- **Frontend vs Backend**: The user identity is verified via Ed25519 signatures. Frontend keys are generated randomly on first run and rotated by max-age policy; ensure any registered public keys and gateway expectations in `core/infra/transport/gateway.py` are aligned.

---

## 🎤 3. Audio Pipeline Debugging

### 🙉 No Microphone Found

**Error**: `AudioDeviceNotFoundError`

- **Fix**: List available devices via `python scripts/debug/audio_list.py` (if available) or check system permissions.
- **Mac Users**: Ensure `Microphone` access is granted to the terminal/IDE running the engine.

### 🔊 Audio Stuttering (p99 Jitter)

- **Cause**: The Python GIL is being blocked by a synchronous tool call.
- **Prevention**: Use **Async Everything**. Ensure all tools in `core/tools/` use `async def` and non-blocking libraries (e.g., `httpx` instead of `requests`).

---

## 🧠 4. Neural Link (Cold Start)

### ⏳ Long Startup (40s - 60s)

If the engine takes >30s to report "online":

- **Cause**: The system is embedding 20+ ADK tools into the `LocalVectorStore` on the first run.
- **Optimization**: The `LocalVectorStore` caches results in `.aether_index.pkl`. Subsequent boots will be sub-5 seconds.

---

## 🚀 One-Click Reset

If the engine state becomes corrupted:

1. `killall python3`
2. `rm .aether_index.pkl` (Forces re-indexing)
3. `python main.py`
