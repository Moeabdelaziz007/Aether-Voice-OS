#!/bin/bash
# Aether-Voice-OS: Judge Demo — Fail-Safe Recovery Snippets
# ══════════════════════════════════════════════════════════
# Execute these if the live demo fails. (Target Recovery: <20s)

# CASE 1: Google GenAI WebSocket (SSL/Conn) Failure
# Symptom: Waveform is flat, console shows "WebSocket connection failed".
# Fix: Force restart the gateway session via Firebase Functions.
RECOVER_CONN() {
    echo "🚨 SSL/Conn Failure: Restarting Gateway..."
    firebase functions:shell --command="processIntents({input: 'system_restart'})"
}

# CASE 2: Vision Pulse (Backpressure) Dropping Frames
# Symptom: AI says "I can't see your screen".
# Fix: Flush the frame buffer and re-sync UI state.
RECOVER_VISION() {
    echo "👁️ Vision Sync Failure: Flushing Buffer..."
    # Local terminal trigger (if AetherGateway is running locally)
    curl -X POST http://localhost:8000/sync/flush
}

# CASE 3: Total Backend Crash (Emergency Cut)
# Fix: If the environment is unrecoverable, CUT TO PRE-RECORDED CLIP.
# Instruction: "Click the 'Neural Backup' button in the dashboard top bar."
# This triggers `apps/portal/src/components/MemoryCrystal.tsx` to play `vids/backup_grounding.mp4`.

# CASE 4: Firestore Permission Denied
# Fix: Re-auth the service account.
RECOVER_DB() {
    gcloud auth activate-service-account --key-file=.env.GCP_KEY
    firebase use gemigram-prod
}

# CASE 5: Smoke Test (Pre-flight check)
run_smoke() {
    ./scripts/smoke_gemini_live.sh
}
