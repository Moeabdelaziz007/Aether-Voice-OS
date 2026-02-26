"use client";
/**
 * Aether Voice OS — Audio Pipeline Hook.
 *
 * Manages browser audio I/O:
 *   - Mic capture via getUserMedia + AudioWorklet
 *   - PCM encoding (Float32 → Int16 @ 16kHz)
 *   - AI audio playback via AudioContext
 *   - Real-time energy levels for visualization
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

    // Speaker level tracking
    const speakerAnalyserRef = useRef<AnalyserNode | null>(null);
    const speakerGainRef = useRef<GainNode | null>(null);

    const start = useCallback(async () => {
        if (state === "active") return;
        setState("starting");

        try {
            // Create AudioContext at 16kHz for mic capture
            const ctx = new AudioContext({ sampleRate: 16000 });
            audioCtxRef.current = ctx;

            // Resume if suspended (autoplay policy)
            if (ctx.state === "suspended") await ctx.resume();

            // Get microphone
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

            // Create analyser for mic level visualization
            const analyser = ctx.createAnalyser();
            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.5;
            analyserRef.current = analyser;

            // Create speaker output chain
            const speakerAnalyser = ctx.createAnalyser();
            speakerAnalyser.fftSize = 256;
            speakerAnalyser.smoothingTimeConstant = 0.5;
            speakerAnalyserRef.current = speakerAnalyser;

            const speakerGain = ctx.createGain();
            speakerGain.gain.value = 1.0;
            speakerGain.connect(speakerAnalyser);
            speakerAnalyser.connect(ctx.destination);
            speakerGainRef.current = speakerGain;

            // Connect mic to analyser
            const source = ctx.createMediaStreamSource(stream);
            source.connect(analyser);

            // Load AudioWorklet for PCM encoding
            await ctx.audioWorklet.addModule("/pcm-processor.js");
            const worklet = new AudioWorkletNode(ctx, "pcm-encoder");
            workletRef.current = worklet;

            // Wire mic → worklet
            source.connect(worklet);

            // Handle PCM chunks from worklet
            worklet.port.onmessage = (e: MessageEvent) => {
                const { pcm, rms } = e.data;
                setMicLevel(Math.min(1, rms * 5)); // Amplify for visibility
                if (onPCMChunk.current) {
                    onPCMChunk.current(pcm);
                }
            };

            // Start level monitoring animation loop
            const monitorLevels = () => {
                // Speaker level from analyser
                if (speakerAnalyserRef.current) {
                    const data = new Uint8Array(speakerAnalyserRef.current.frequencyBinCount);
                    speakerAnalyserRef.current.getByteFrequencyData(data);
                    const avg = data.reduce((a, b) => a + b, 0) / data.length;
                    setSpeakerLevel(Math.min(1, avg / 128));
                }
                rafRef.current = requestAnimationFrame(monitorLevels);
            };
            monitorLevels();

            setState("active");
        } catch (err) {
            console.error("Audio pipeline error:", err);
            setState("error");
        }
    }, [state]);

    const stop = useCallback(() => {
        // Stop mic
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;

        // Disconnect worklet
        workletRef.current?.disconnect();
        workletRef.current = null;

        // Close audio context
        audioCtxRef.current?.close();
        audioCtxRef.current = null;

        // Stop animation
        if (rafRef.current) cancelAnimationFrame(rafRef.current);

        setMicLevel(0);
        setSpeakerLevel(0);
        setState("idle");
    }, []);

    const playPCM = useCallback((pcmData: ArrayBuffer, sampleRate = 24000) => {
        const ctx = audioCtxRef.current;
        const gain = speakerGainRef.current;
        if (!ctx || !gain) return;

        // Create a new AudioContext for playback at correct sample rate if needed
        const pcm16 = new Int16Array(pcmData);
        const float32 = new Float32Array(pcm16.length);
        for (let i = 0; i < pcm16.length; i++) {
            float32[i] = pcm16[i] / 32768;
        }

        // Create buffer at Gemini's output sample rate
        const buffer = new AudioBuffer({
            length: float32.length,
            numberOfChannels: 1,
            sampleRate: sampleRate,
        });
        buffer.copyToChannel(float32, 0);

        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(gain);
        source.start();
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stop();
        };
    }, [stop]);

    return { state, micLevel, speakerLevel, start, stop, playPCM, onPCMChunk };
}
