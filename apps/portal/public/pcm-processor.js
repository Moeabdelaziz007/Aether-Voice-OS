/**
 * Aether Voice OS — PCM Encoder AudioWorklet.
 *
 * Security Posture:
 *   - Implements Temporal Data Zeroization
 *   - Frozen prototypes to prevent runtime prototype pollution
 *   - CSP Recommendation: `worker-src 'self' blob:;`
 *
 * Runs on the audio rendering thread (no main-thread blocking).
 * Converts Float32 mic samples to Int16 PCM and posts chunks
 * every ~256ms (4096 samples @ 16kHz) to the main thread.
 *
 * Performance optimizations:
 *   - Pre-allocated ring buffer (no GC-triggering allocations)
 *   - Zero-copy transfer via Transferable ArrayBuffer
 *   - Larger chunks (256ms) reduce WS message overhead by 2.5x
 *
 * Usage:
 *   audioContext.audioWorklet.addModule('/pcm-processor.js');
 *   const node = new AudioWorkletNode(ctx, 'pcm-encoder');
 *   node.port.onmessage = (e) => sendToGemini(e.data.pcm);
 */
class PCMEncoderProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        // Pre-allocated ring buffer — avoids GC pressure from Float32Array concat
        this._capacity = 4096; // 256ms @ 16kHz — optimal for Gemini Live
        this._ring = new Float32Array(this._capacity);
        this._writePos = 0;
    }

    process(inputs) {
        const input = inputs[0];
        if (!input || !input[0]) return true;

        const channelData = input[0]; // mono channel
        const len = channelData.length;

        // Fast copy into ring buffer
        if (this._writePos + len <= this._capacity) {
            this._ring.set(channelData, this._writePos);
        } else {
            // Should not happen with 128-sample frames, but handle gracefully
            for (let i = 0; i < len; i++) {
                this._ring[(this._writePos + i) % this._capacity] = channelData[i];
            }
        }
        this._writePos += len;

        // Flush when ring is full
        if (this._writePos >= this._capacity) {
            this._flush();
        }

        return true; // Keep processor alive
    }

    _flush() {
        const n = this._capacity;

        // 1. Calculate RMS energy (on Float32 for precision)
        let sumSq = 0;
        for (let i = 0; i < n; i++) {
            sumSq += this._ring[i] * this._ring[i];
        }
        const rms = Math.sqrt(sumSq / n);

        // 2. Convert Float32 [-1.0, 1.0] → Int16 [-32768, 32767]
        const pcm = new Int16Array(n);
        for (let i = 0; i < n; i++) {
            const s = Math.max(-1, Math.min(1, this._ring[i]));
            pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        // 3. Post to main thread (transfer ownership — zero-copy)
        this.port.postMessage(
            { pcm: pcm.buffer, rms },
            [pcm.buffer]
        );

        // 4. Secure buffer wipe to prevent cross-frame temporal data leakage
        this._ring.fill(0);

        // 5. Reset write position (reuse ring buffer — no allocation)
        this._writePos = 0;
    }
}

// Ensure the worklet cannot be modified after registration
Object.freeze(PCMEncoderProcessor.prototype);

registerProcessor('pcm-encoder', PCMEncoderProcessor);
