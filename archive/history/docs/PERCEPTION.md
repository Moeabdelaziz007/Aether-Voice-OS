# 🦅 Perception: The Senses of AetherOS

## 1. Overview: The Thalamic Gate

AetherOS perception is divided into two distinct but interleaved modules: **Audio Intelligence (Senses)** and **Hybrid Memory (The Hippocampus)**. These layers work together to filter out system noise (Echo Guard) and provide instant contextual recall.

---

## 2. Audio Intelligence (Echo Guard)

> [!IMPORTANT]
> AetherOS uses a 5-Layer Echo Guard to prevent the system from "hearing itself." This is critical for Barge-in (interruption) to work reliably.

### The 5-Layer Protection

1. **RMS Energy Threshold**: A primitive gate that ignores sound below the ambient noise floor.
2. **Acoustic Identity Cache**: The system caches fingerprints (MFCC-like) of its own output and compares them against incoming mic audio using Cosine Similarity.
3. **Spectral Fingerprinting**: Frequency-domain analysis that distinguishes the system's "Voice" from the user's.
4. **Hysteresis & Reverb Lock**: A 150ms lockout timer that prevents room reflections/reverb from triggering the VAD after the system stops speaking.
5. **Dynamic Noise Floor Tracking**: Recalculates the "silence" threshold at 15Hz to account for fans, keyboards, or city noise.

---

## 3. Streaming Continuity (Adaptive Jitter Buffer)

To maintain a sub-200ms latency while preventing audio clicking/jitter, Aether implements a circular `AudioJitterBuffer`.

- **Nominal Depth**: The minimum number of packets required before playback begins (standard: 100ms).
- **Auto-Recovery**: If a network glitch causes an underflow, the buffer enters a "Re-buffering" state to restore continuity rather than playing choppy audio.
- **Fast Flush**: On Barge-in, the buffer is instantly cleared to ensure the next response starts from zero latency.

---

## 4. Hybrid Memory Architecture

Aether's memory mimics the human brain's split between short-term and long-term storage.

### A. Short-Term Memory (Redis/RAM)

- **Latency**: <1ms.
- **Content**: Active conversation turn, current task stack, and transient tool outputs.
- **Function**: Used for immediate pronoun resolution (e.g., "What did *it* say?") and rapid state tracking.

### B. Long-Term Memory (Vector Search)

- **Latency**: ~50ms - 200ms.
- **Store**: Vertex AI / Pinecone / Local Index.
- **Function**: Semantic search across previous sessions. Aether uses "Indexical Syncing" to find related code snippets or past architectural decisions.

---

## 5. Vision Sync

While primarily audio-focused, the `VisionProcessor` pulses every 10s to keep the "Visual Hippocampus" grounded in the user's current IDE state, allowing the Memory layer to link voice commands to specific lines of code.

---

## 6. Verification

Perception systems are validated via:

- **VAD Accuracy Benchmarks**: Testing trigger rates in noisy environments (SNR analysis).
- **Echo Suppression Stress Tests**: Playing loud white noise through speakers to verify 0% leakage.
- **Recall Rate Metrics**: Measuring "Top-K" accuracy for the Vector Memory search.
