"use client";
/**
 * Aether Voice OS — Audio Pipeline Hook.
 *
 * Manages browser audio I/O:
 *   - Mic capture via getUserMedia + AudioWorklet (16kHz PCM)
 *   - Gapless streaming playback via scheduled AudioBufferSource nodes
 *   - Instant barge-in interruption (stop all queued audio)
 *   - Real-time mic and speaker energy levels for visualization
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type PipelineState = "idle" | "starting" | "active" | "error";

interface AudioPipelineReturn {
    state: PipelineState;
    micLevel: number;
    speakerLevel: number;
    start: () => Promise<void>;
    stop: () => void;
    playPCM: (pcmData: ArrayBuffer, sampleRate?: number) => void;
    stopPlayback: () => void;
    onPCMChunk: React.MutableRefObject<((pcm: ArrayBuffer) => void) | null>;
}

export function useAudioPipeline(): AudioPipelineReturn {
    const [state, setState] = useState<PipelineState>("idle");
    const [micLevel, setMicLevel] = useState(0);
    const [speakerLevel, setSpeakerLevel] = useState(0);

    const audioCtxRef = useRef<AudioContext | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const workletRef = useRef<AudioWorkletNode | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const rafRef = useRef<number>(0);
    const onPCMChunk = useRef<((pcm: ArrayBuffer) => void) | null>(null);

    // Speaker output chain
    const speakerAnalyserRef = useRef<AnalyserNode | null>(null);
    const speakerGainRef = useRef<GainNode | null>(null);

    // Gapless playback queue
    const nextPlayTimeRef = useRef(0);
    const activeSourcesRef = useRef<AudioBufferSourceNode[]>([]);
    const playbackCtxRef = useRef<AudioContext | null>(null);

    const start = useCallback(async () => {
        if (state === "active") return;
        setState("starting");

        try {
            // Mic capture context at 16kHz
            const ctx = new AudioContext({ sampleRate: 16000 });
            audioCtxRef.current = ctx;

            if (ctx.state === "suspended") await ctx.resume();

            // Separate context for playback at native rate (handles 24kHz internally)
            const playCtx = new AudioContext();
            playbackCtxRef.current = playCtx;
            if (playCtx.state === "suspended") await playCtx.resume();

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });
            streamRef.current = stream;

            // Mic analyser for energy visualization
            const analyser = ctx.createAnalyser();
            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.5;
            analyserRef.current = analyser;

            // Speaker output chain (on playback context)
            const speakerAnalyser = playCtx.createAnalyser();
            speakerAnalyser.fftSize = 256;
            speakerAnalyser.smoothingTimeConstant = 0.5;
            speakerAnalyserRef.current = speakerAnalyser;

            const speakerGain = playCtx.createGain();
            speakerGain.gain.value = 1.0;
            speakerGain.connect(speakerAnalyser);
            speakerAnalyser.connect(playCtx.destination);
            speakerGainRef.current = speakerGain;

            // Wire mic
            const source = ctx.createMediaStreamSource(stream);
            source.connect(analyser);

            // Load AudioWorklet for PCM encoding
            await ctx.audioWorklet.addModule("/pcm-processor.js");
            const worklet = new AudioWorkletNode(ctx, "pcm-encoder");
            workletRef.current = worklet;
            source.connect(worklet);

            // Handle PCM chunks from worklet
            worklet.port.onmessage = (e: MessageEvent) => {
                const { pcm, rms } = e.data;
                setMicLevel(Math.min(1, rms * 5)); // Amplify for visibility
                if (onPCMChunk.current) {
                    onPCMChunk.current(pcm);
                }
            };

            // Level monitoring animation loop
            const monitorLevels = () => {
                if (speakerAnalyserRef.current) {
                    const data = new Uint8Array(
                        speakerAnalyserRef.current.frequencyBinCount
                    );
                    speakerAnalyserRef.current.getByteFrequencyData(data);
                    const avg =
                        data.reduce((a, b) => a + b, 0) / data.length;
                    setSpeakerLevel(Math.min(1, avg / 128));
                }
                rafRef.current = requestAnimationFrame(monitorLevels);
            };
            monitorLevels();

            // Reset playback cursor
            nextPlayTimeRef.current = 0;
            setState("active");
        } catch (err) {
            console.error("Audio pipeline error:", err);
            setState("error");
        }
    }, [state]);

    const stop = useCallback(() => {
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;

        workletRef.current?.disconnect();
        workletRef.current = null;

        audioCtxRef.current?.close();
        audioCtxRef.current = null;

        playbackCtxRef.current?.close();
        playbackCtxRef.current = null;

        if (rafRef.current) cancelAnimationFrame(rafRef.current);

        // Clean up active sources
        activeSourcesRef.current.forEach((s) => {
            try { s.stop(); } catch { }
        });
        activeSourcesRef.current = [];
        nextPlayTimeRef.current = 0;

        setMicLevel(0);
        setSpeakerLevel(0);
        setState("idle");
    }, []);

    /**
     * Gapless PCM playback — schedules audio chunks sequentially
     * so there are zero gaps between chunks. This is critical for
     * natural-sounding voice output.
     */
    const playPCM = useCallback(
        (pcmData: ArrayBuffer, sampleRate = 24000) => {
            const ctx = playbackCtxRef.current;
            const gain = speakerGainRef.current;
            if (!ctx || !gain) return;

            // Decode Int16 → Float32
            const pcm16 = new Int16Array(pcmData);
            const float32 = new Float32Array(pcm16.length);
            for (let i = 0; i < pcm16.length; i++) {
                float32[i] = pcm16[i] / 32768;
            }

            // Create AudioBuffer at Gemini's output sample rate
            const buffer = new AudioBuffer({
                length: float32.length,
                numberOfChannels: 1,
                sampleRate: sampleRate,
            });
            buffer.copyToChannel(float32, 0);

            const source = ctx.createBufferSource();
            source.buffer = buffer;
            source.connect(gain);

            // Schedule gaplessly
            const now = ctx.currentTime;
            const startTime = Math.max(
                now,
                nextPlayTimeRef.current
            );
            source.start(startTime);

            // Update cursor for next chunk
            nextPlayTimeRef.current = startTime + buffer.duration;

            // Track for barge-in cleanup
            activeSourcesRef.current.push(source);
            source.onended = () => {
                const idx = activeSourcesRef.current.indexOf(source);
                if (idx !== -1) activeSourcesRef.current.splice(idx, 1);
            };
        },
        []
    );

    /**
     * Instant barge-in: stop all queued/playing audio immediately.
     * Prevents "zombie" audio from playing after user interrupts.
     */
    const stopPlayback = useCallback(() => {
        activeSourcesRef.current.forEach((source) => {
            try {
                source.onended = null;
                source.stop();
            } catch { }
        });
        activeSourcesRef.current = [];
        nextPlayTimeRef.current = 0;
        setSpeakerLevel(0);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stop();
        };
    }, [stop]);

    return {
        state,
        micLevel,
        speakerLevel,
        start,
        stop,
        playPCM,
        stopPlayback,
        onPCMChunk,
    };
}
