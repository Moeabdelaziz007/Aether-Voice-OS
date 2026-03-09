"use client";

import { useMemo } from "react";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * useAvatarVisemes — Neural Lip-Sync Logic
 * 
 * Maps realtime audio levels from Gemini and local microphone to a 
 * "mouthOpenness" scalar (0.0 - 1.0) for the 3D avatar.
 */
export function useAvatarVisemes() {
    const micLevel = useAetherStore((s) => s.micLevel);
    const speakerLevel = useAetherStore((s) => s.speakerLevel);
    const engineState = useAetherStore((s) => s.engineState);

    const mouthOpenness = useMemo(() => {
        // Priority: Speaker level when Aether is talking, Mic level when listening
        const rawLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

        // Non-linear mapping for more organic mouth movement
        // Basic clamping and sensitivity adjustment
        const sensitivity = 1.2;
        const base = Math.min(rawLevel * sensitivity, 1.0);

        // Apply a threshold to ignore background noise
        const threshold = 0.05;
        return base > threshold ? base : 0;
    }, [micLevel, speakerLevel, engineState]);

    return {
        mouthOpenness,
        engineState,
        isSpeaking: engineState === "SPEAKING",
        isListening: engineState === "LISTENING",
    };
}
