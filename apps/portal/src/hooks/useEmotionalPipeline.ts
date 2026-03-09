"use client";

/**
 * Aether Voice OS — Emotional Pipeline Hook.
 *
 * Bridges the audio processing pipeline with emotional state management.
 * Provides real-time emotional analysis from audio features and
 * integrates with the visual atmosphere system.
 */

import { useCallback, useState } from "react";
import { useAetherStore } from "../store/useAetherStore";
import {
    EmotionType,
    EmotionalFeatures,
    EmotionalState,
    EmotionalEvent,
    analyzeValence,
    analyzeArousal,
    analyzeDominance,
    classifyEmotionFromState,
} from "../utils/emotionUtils";
import { useEmotionalTrend } from "./useEmotionalTrend";

interface UseEmotionalPipelineOptions {
    smoothingFactor?: number; // 0 to 1, higher = smoother
    onEmotionalEvent?: (event: EmotionalEvent) => void;
}

export function useEmotionalPipeline(options: UseEmotionalPipelineOptions = {}) {
    const {
        smoothingFactor = 0.85,
        onEmotionalEvent,
    } = options;

    const store = useAetherStore();
    const trend = useEmotionalTrend();

    // Smoothed emotional state
    const [smoothedState, setSmoothedState] = useState<EmotionalState>({
        type: "neutral",
        valence: 0,
        arousal: 0,
        dominance: 0.5,
        confidence: 0,
        timestamp: Date.now(),
    });

    // Update store telemetry from emotional analysis
    const updateStoreTelemetry = useCallback(
        (state: EmotionalState, features: EmotionalFeatures) => {
            store.setTelemetry(
                {
                    frustration: state.type === "frustrated" || state.type === "stressed"
                        ? 1 - state.valence
                        : 0,
                    valence: state.valence,
                    arousal: state.arousal,
                    engagement: state.arousal * (state.valence > 0 ? 1 : 0.5),
                    pitch: features.pitch,
                    rate: features.speechRate,
                    spectralCentroid: features.spectralCentroid,
                },
                0 // Latency will be set by gateway
            );
        },
        [store]
    );

    // Detect emotional events (transitions)
    const detectEmotionalEvent = useCallback(
        (newState: EmotionalState) => {
            const prevType = trend.lastEmotionType.current;
            const now = Date.now();

            // Frustration logic
            if ((newState.type === "frustrated" || newState.type === "stressed") &&
                prevType !== "frustrated" && prevType !== "stressed") {
                trend.frustrationStartTime.current = now;
                onEmotionalEvent?.({
                    type: "frustration_spike",
                    emotion: newState.type,
                    intensity: 1 - newState.valence,
                    timestamp: now,
                });
            } else if (trend.frustrationStartTime.current && (now - trend.frustrationStartTime.current > 10000) &&
                (newState.type === "frustrated" || newState.type === "stressed")) {
                onEmotionalEvent?.({
                    type: "stress_detected",
                    emotion: newState.type,
                    intensity: 1 - newState.valence,
                    timestamp: now,
                });
                trend.frustrationStartTime.current = null;
            }

            // Flow logic
            if (newState.type === "flow_state" && prevType !== "flow_state") {
                trend.flowStateStartTime.current = now;
                onEmotionalEvent?.({ type: "flow_enter", emotion: "flow_state", intensity: newState.arousal, timestamp: now });
            } else if (newState.type !== "flow_state" && prevType === "flow_state") {
                const flowDuration = trend.flowStateStartTime.current ? now - trend.flowStateStartTime.current : 0;
                onEmotionalEvent?.({ type: "flow_exit", emotion: prevType, intensity: flowDuration / 1000, timestamp: now });
                trend.flowStateStartTime.current = null;
            }

            // Excitement
            if (newState.type === "excited" && newState.arousal > 0.8 && prevType !== "excited") {
                onEmotionalEvent?.({ type: "excitement_peak", emotion: "excited", intensity: newState.arousal, timestamp: now });
            }

            if (newState.type !== "frustrated" && newState.type !== "stressed") {
                trend.frustrationStartTime.current = null;
            }

            trend.lastEmotionType.current = newState.type;
        },
        [onEmotionalEvent, trend]
    );

    // Process audio features into emotional state
    const processEmotionalFeatures = useCallback(
        (features: EmotionalFeatures) => {
            const rawValence = analyzeValence(features);
            const rawArousal = analyzeArousal(features);
            const rawDominance = analyzeDominance(features);

            const smoothedValence =
                smoothedState.valence * smoothingFactor + rawValence * (1 - smoothingFactor);
            const smoothedArousal =
                smoothedState.arousal * smoothingFactor + rawArousal * (1 - smoothingFactor);
            const smoothedDominance =
                smoothedState.dominance * smoothingFactor + rawDominance * (1 - smoothingFactor);

            const emotionType = classifyEmotionFromState(
                smoothedValence,
                smoothedArousal,
                smoothedDominance
            );

            const newState: EmotionalState = {
                type: emotionType,
                valence: smoothedValence,
                arousal: smoothedArousal,
                dominance: smoothedDominance,
                confidence: Math.min(1, features.energy * 5),
                timestamp: Date.now(),
            };

            setSmoothedState(newState);
            trend.addStateToHistory(newState);
            updateStoreTelemetry(newState, features);
            detectEmotionalEvent(newState);

            return newState;
        },
        [smoothedState, smoothingFactor, updateStoreTelemetry, detectEmotionalEvent, trend]
    );

    return {
        emotionalState: smoothedState,
        processEmotionalFeatures,
        getEmotionalTrend: trend.getEmotionalTrend,
        getFrustrationScore: trend.getFrustrationScore,
        isFrustrated: smoothedState.type === "frustrated" || smoothedState.type === "stressed",
        isFlowState: smoothedState.type === "flow_state",
        isHighEnergy: smoothedState.arousal > 0.6,
        isPositive: smoothedState.valence > 0.2,
        stateHistory: trend.stateHistory.current,
    };
}

export { extractEmotionalFeaturesFromPCM } from "../utils/audioUtils"; // Assuming we move extraction too
