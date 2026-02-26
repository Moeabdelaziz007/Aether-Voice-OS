/**
 * Aether Voice OS — PCM Encoder AudioWorklet.
 *
 * Runs on the audio rendering thread (no main-thread blocking).
 * Converts Float32 mic samples to Int16 PCM and posts chunks
 * every ~100ms (1600 samples @ 16kHz) to the main thread.
 *
 * Usage:
 *   audioContext.audioWorklet.addModule('/pcm-processor.js');
 *   const node = new AudioWorkletNode(ctx, 'pcm-encoder');
 *   node.port.onmessage = (e) => sendToGemini(e.data.pcm);
 */
class PCMEncoderProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this._buffer = new Float32Array(0);
        // 100ms of samples @ 16kHz = 1600 samples
        this._chunkSize = 1600;
    }

    process(inputs) {
        const input = inputs[0];
        if (!input || !input[0]) return true;

        const channelData = input[0]; // mono channel

        // Append to internal buffer
        const newBuffer = new Float32Array(this._buffer.length + channelData.length);
        newBuffer.set(this._buffer);
        newBuffer.set(channelData, this._buffer.length);
        this._buffer = newBuffer;

        // When we have enough samples, encode and send
        while (this._buffer.length >= this._chunkSize) {
            const chunk = this._buffer.slice(0, this._chunkSize);
            this._buffer = this._buffer.slice(this._chunkSize);

            // Float32 → Int16 PCM conversion
            const pcm = new Int16Array(chunk.length);
            for (let i = 0; i < chunk.length; i++) {
                const s = Math.max(-1, Math.min(1, chunk[i]));
                pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
            }

            // Calculate RMS energy for visualization
            let sumSq = 0;
            for (let i = 0; i < chunk.length; i++) {
                sumSq += chunk[i] * chunk[i];
            }
            const rms = Math.sqrt(sumSq / chunk.length);

            this.port.postMessage(
                { pcm: pcm.buffer, rms },
                [pcm.buffer] // Transfer ownership (zero-copy)
            );
        }

        return true; // Keep processor alive
    }
}

registerProcessor('pcm-encoder', PCMEncoderProcessor);
