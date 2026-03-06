/**
 * Aether Voice OS — PCM Encoder AudioWorklet.
 *
 * Runs on the audio rendering thread (no main-thread blocking).
 * Converts Float32 mic samples to Int16 PCM and posts chunks
 * at a configurable capacity controlled by the main thread.
 *
 * Performance optimizations:
 *   - Pre-allocated ring buffer (no GC-triggering allocations)
 *   - Zero-copy transfer via Transferable ArrayBuffer
 *   - Configurable chunk presets for conversational vs bandwidth-saver modes
 */
class PCMEncoderProcessor extends AudioWorkletProcessor {
    static PRESET_CAPACITIES = {
        ultra_low_latency: 512,
        low_latency: 1024,
        balanced: 2048,
        bandwidth_saver: 4096,
    };

    constructor() {
        super();

        this._capacity = PCMEncoderProcessor.PRESET_CAPACITIES.low_latency;
        this._ring = new Float32Array(this._capacity);
        this._writePos = 0;

        this.port.onmessage = (event) => {
            const data = event.data;
            if (!data || data.type !== "configure") return;
            this._configureCapacity(data);
        };
    }

    _configureCapacity(data) {
        const presets = PCMEncoderProcessor.PRESET_CAPACITIES;
        const presetKey = typeof data.preset === "string" ? data.preset : "";
        const presetCapacity = presets[presetKey];

        const requestedCapacity = Number.isInteger(data.capacity)
            ? data.capacity
            : presetCapacity;

        const allowedCapacities = [512, 1024, 2048, 4096];
        if (!allowedCapacities.includes(requestedCapacity)) return;

        if (requestedCapacity === this._capacity) return;

        // Flush existing buffered samples before changing capacity to avoid data loss.
        if (this._writePos > 0) {
            this._flushPartial(this._writePos);
        }

        this._capacity = requestedCapacity;
        this._ring = new Float32Array(this._capacity);
        this._writePos = 0;

        this.port.postMessage({
            type: "configured",
            capacity: this._capacity,
            chunkMs: (this._capacity / 16000) * 1000,
        });
    }

    process(inputs) {
        const input = inputs[0];
        if (!input || !input[0]) return true;

        const channelData = input[0]; // mono channel
        const len = channelData.length;

        if (this._writePos + len <= this._capacity) {
            this._ring.set(channelData, this._writePos);
            this._writePos += len;
        } else {
            let srcPos = 0;
            while (srcPos < len) {
                const writable = this._capacity - this._writePos;
                const toCopy = Math.min(writable, len - srcPos);
                this._ring.set(channelData.subarray(srcPos, srcPos + toCopy), this._writePos);
                this._writePos += toCopy;
                srcPos += toCopy;

                if (this._writePos >= this._capacity) {
                    this._flush();
                }
            }
        }

        if (this._writePos >= this._capacity) {
            this._flush();
        }

        return true;
    }

    _flush() {
        this._flushPartial(this._capacity);
        this._writePos = 0;
    }

    _flushPartial(sampleCount) {
        if (sampleCount <= 0) return;

        let sumSq = 0;
        for (let i = 0; i < sampleCount; i++) {
            sumSq += this._ring[i] * this._ring[i];
        }
        const rms = Math.sqrt(sumSq / sampleCount);

        const pcm = new Int16Array(sampleCount);
        for (let i = 0; i < sampleCount; i++) {
            const s = Math.max(-1, Math.min(1, this._ring[i]));
            pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        this.port.postMessage(
            { pcm: pcm.buffer, rms, capacity: this._capacity },
            [pcm.buffer]
        );
    }
}

registerProcessor('pcm-encoder', PCMEncoderProcessor);
