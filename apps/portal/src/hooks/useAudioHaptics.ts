"use client";

import { useCallback, useRef } from "react";

/**
 * useAudioHaptics — The Neural Haptic Engine.
 * Synthesizes sci-fi UI sound effects using the Web Audio API.
 * Zero-latency, zero-dependency auditory feedback.
 */
export const useAudioHaptics = () => {
    const audioCtx = useRef<AudioContext | null>(null);

    const getCtx = () => {
        if (!audioCtx.current) {
            audioCtx.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        }
        return audioCtx.current;
    };

    const playTone = useCallback((
        freq: number,
        duration: number,
        type: OscillatorType = "sine",
        vol = 0.1,
        sweep = false
    ) => {
        try {
            const ctx = getCtx();
            if (ctx.state === "suspended") ctx.resume();

            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, ctx.currentTime);

            if (sweep) {
                osc.frequency.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
            }

            gain.gain.setValueAtTime(vol, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + duration);
        } catch (e) {
            console.warn("AudioHaptics: Failed to play tone", e);
        }
    }, []);

    const playClick = useCallback(() => playTone(800, 0.05, "sine", 0.05, true), [playTone]);
    const playHover = useCallback(() => playTone(400, 0.02, "sine", 0.02), [playTone]);
    const playSuccess = useCallback(() => {
        playTone(600, 0.1, "sine", 0.05);
        setTimeout(() => playTone(900, 0.15, "sine", 0.05), 50);
    }, [playTone]);

    const playError = useCallback(() => {
        playTone(150, 0.2, "sawtooth", 0.05);
        playTone(100, 0.2, "square", 0.03);
    }, [playTone]);

    const playPulse = useCallback(() => {
        playTone(200, 0.8, "sine", 0.03, true);
    }, [playTone]);

    const playBoot = useCallback(() => {
        const now = getCtx().currentTime;
        [440, 554.37, 659.25, 880].forEach((f, i) => {
            setTimeout(() => playTone(f, 0.5, "sine", 0.02), i * 100);
        });
    }, [playTone]);

    return { playClick, playHover, playSuccess, playError, playPulse, playBoot };
};
