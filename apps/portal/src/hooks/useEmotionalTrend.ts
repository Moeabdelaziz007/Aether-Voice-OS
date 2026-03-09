/**
 * Aether Voice OS — Emotional Trend Hook.
 * 
 * Handles history, trend detection, and frustration scoring.
 */

import { useRef, useCallback } from "react";
import { EmotionalState, EmotionType } from "../utils/emotionUtils";

export interface EmotionalTrend {
    direction: "improving" | "declining" | "stable";
    intensity: number;
}

export function useEmotionalTrend() {
    const stateHistory = useRef<EmotionalState[]>([]);
    const lastEmotionType = useRef<EmotionType>("neutral");
    const flowStateStartTime = useRef<number | null>(null);
    const frustrationStartTime = useRef<number | null>(null);

    const addStateToHistory = useCallback((state: EmotionalState) => {
        stateHistory.current = [...stateHistory.current.slice(-99), state];
    }, []);

    const getEmotionalTrend = useCallback((windowMs: number = 30000): EmotionalTrend => {
        const now = Date.now();
        const recentStates = stateHistory.current.filter(
            (s) => now - s.timestamp < windowMs
        );

        if (recentStates.length < 2) {
            return { direction: "stable", intensity: 0 };
        }

        const firstHalf = recentStates.slice(0, Math.floor(recentStates.length / 2));
        const secondHalf = recentStates.slice(Math.floor(recentStates.length / 2));

        const avgFirst = firstHalf.reduce((sum, s) => sum + s.valence, 0) / firstHalf.length;
        const avgSecond = secondHalf.reduce((sum, s) => sum + s.valence, 0) / secondHalf.length;

        const direction = avgSecond > avgFirst + 0.1
            ? "improving"
            : avgSecond < avgFirst - 0.1
                ? "declining"
                : "stable";

        return {
            direction,
            intensity: Math.abs(avgSecond - avgFirst),
        };
    }, []);

    const getFrustrationScore = useCallback(() => {
        const recentStates = stateHistory.current.slice(-10);
        if (recentStates.length === 0) return 0;

        const weights = recentStates.map((_, i) => i + 1);
        const totalWeight = weights.reduce((a, b) => a + b, 0);

        const frustrationSum = recentStates.reduce((sum, state, i) => {
            const frustrationValue = state.type === "frustrated" || state.type === "stressed"
                ? 1 - state.valence
                : 0;
            return sum + frustrationValue * weights[i];
        }, 0);

        return frustrationSum / totalWeight;
    }, []);

    return {
        stateHistory,
        lastEmotionType,
        flowStateStartTime,
        frustrationStartTime,
        addStateToHistory,
        getEmotionalTrend,
        getFrustrationScore,
    };
}
