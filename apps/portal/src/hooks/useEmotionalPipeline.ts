"use client";

/**
 * Aether Voice OS — Emotional Pipeline Hook.
 *
 * Bridges the audio processing pipeline with emotional state management.
 * Provides real-time emotional analysis from audio features and
 * integrates with the visual atmosphere system.
 *
 * Features:
 * - Real-time emotion detection from audio features
 * - Smoothed emotional state transitions
 * - Frustration spike detection
 * - Flow state detection
 * - Proactive intervention triggers
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useAetherStore } from "../store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type EmotionType =
    | "neutral"
    | "calm"
    | "focused"
    | "curious"
    | "flow_state"
    | "excited"
    | "frustrated"
    | "stressed";

export interface EmotionalFeatures {
    pitch: number;
    pitchVariance: number;
    speechRate: number;
    energy: number;
    energyVariance: number;
    spectralCentroid: number;
    zcr: number; // Zero-crossing rate
}

export interface EmotionalState {
    type: EmotionType;
    valence: number; // -1 to 1
    arousal: number; // 0 to 1
    dominance: number; // 0 to 1
    confidence: number;
    timestamp: number;
}

export interface EmotionalEvent {
    type: "frustration_spike" | "flow_enter" | "flow_exit" | "stress_detected" | "excitement_peak";
    emotion: EmotionType;
    intensity: number;
    timestamp: number;
}

interface UseEmotionalPipelineOptions {
    smoothingFactor?: number; // 0 to 1, higher = smoother
    frustrationThreshold?: number;
    flowThreshold?: number;
    onEmotionalEvent?: (event: EmotionalEvent) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTION ANALYSIS
// ═══════════════════════════════════════════════════════════════════════════════

// Pitch ranges for male/female typical speech (Hz)
const PITCH_MALE_MIN = 85;
const PITCH_MALE_MAX = 180;
const PITCH_FEMALE_MIN = 165;
const PITCH_FEMALE_MAX = 255;

// Typical speech rate (syllables per second)
const SPEECH_RATE_SLOW = 3;
const SPEECH_RATE_NORMAL = 5;
const SPEECH_RATE_FAST = 7;

function analyzeValence(features: EmotionalFeatures): number {
    // Positive valence indicators:
    // - Higher pitch variance (more expressive)
    // - Moderate to high energy
    // - Higher spectral centroid (brighter voice)

    const pitchExpressiveness = Math.min(1, features.pitchVariance / 50);
    const brightness = Math.min(1, features.spectralCentroid / 4000);
    const energyLevel = Math.min(1, features.energy * 2);

    // Combine factors
    let valence = 0;
    valence += pitchExpressiveness * 0.4;
    valence += brightness * 0.3;
    valence += energyLevel * 0.3;

    // Clamp to -1 to 1 range
    return Math.max(-1, Math.min(1, valence * 2 - 0.5));
}

function analyzeArousal(features: EmotionalFeatures): number {
    // Arousal indicators:
    // - Higher speech rate
    // - Higher energy
    // - Higher pitch

    const rateArousal = Math.min(1, features.speechRate / SPEECH_RATE_FAST);
    const energyArousal = Math.min(1, features.energy * 3);
    const pitchArousal = Math.min(1, features.pitch / 300);

    // Combine factors
    let arousal = 0;
    arousal += rateArousal * 0.4;
    arousal += energyArousal * 0.4;
    arousal += pitchArousal * 0.2;

    return Math.max(0, Math.min(1, arousal));
}

function analyzeDominance(features: EmotionalFeatures): number {
    // Dominance indicators:
    // - Lower pitch variance (more controlled)
    // - Steady energy (confident)
    // - Lower speech rate variation

    const controlFactor = 1 - Math.min(1, features.pitchVariance / 80);
    const steadiness = 1 - Math.min(1, features.energyVariance);

    let dominance = 0;
    dominance += controlFactor * 0.5;
    dominance += steadiness * 0.5;

    return Math.max(0, Math.min(1, dominance));
}

function classifyEmotionFromState(
    valence: number,
    arousal: number,
    dominance: number
): EmotionType {
    const rules: Array<{
        condition: () => boolean;
        emotion: EmotionType | ((dom: number) => EmotionType);
    }> = [
            {
                condition: () => arousal > 0.7 && valence < -0.2,
                emotion: (dom: number) => (dom > 0.5 ? "stressed" : "frustrated"),
            },
            {
                condition: () => arousal > 0.6 && valence > 0.2,
                emotion: (dom: number) => (dom > 0.6 ? "flow_state" : "excited"),
            },
            {
                condition: () => arousal > 0.3 && arousal <= 0.6 && valence > 0,
                emotion: valence > 0.3 ? "curious" : "focused",
            },
            {
                condition: () => arousal <= 0.3 && valence > 0,
                emotion: "calm",
            },
            {
                condition: () => arousal <= 0.4 && valence < -0.2,
                emotion: "frustrated",
            },
        ];

    for (const rule of rules) {
        if (rule.condition()) {
            return typeof rule.emotion === "function"
                ? rule.emotion(dominance)
                : rule.emotion;
        }
    }

    return "neutral";
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export function useEmotionalPipeline(options: UseEmotionalPipelineOptions = {}) {
    const {
        smoothingFactor = 0.85,
        frustrationThreshold = 0.6,
        flowThreshold = 0.7,
        onEmotionalEvent,
    } = options;

    const store = useAetherStore();

    // Smoothed emotional state
    const [smoothedState, setSmoothedState] = useState<EmotionalState>({
        type: "neutral",
        valence: 0,
        arousal: 0,
        dominance: 0.5,
        confidence: 0,
        timestamp: Date.now(),
    });

    // History for trend detection
    const stateHistory = useRef<EmotionalState[]>([]);
    const lastEmotionType = useRef<EmotionType>("neutral");
    const flowStateStartTime = useRef<number | null>(null);
    const frustrationStartTime = useRef<number | null>(null);

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
            const prevType = lastEmotionType.current;
            const now = Date.now();

            const eventDetectors = [
                {
                    // Frustration spike
                    condition: () => (newState.type === "frustrated" || newState.type === "stressed") &&
                        prevType !== "frustrated" && prevType !== "stressed",
                    action: () => {
                        frustrationStartTime.current = now;
                        onEmotionalEvent?.({
                            type: "frustration_spike",
                            emotion: newState.type,
                            intensity: 1 - newState.valence,
                            timestamp: now,
                        });
                    }
                },
                {
                    // Stress (prolonged frustration)
                    condition: () => frustrationStartTime.current && (now - frustrationStartTime.current > 10000) &&
                        (newState.type === "frustrated" || newState.type === "stressed"),
                    action: () => {
                        onEmotionalEvent?.({
                            type: "stress_detected",
                            emotion: newState.type,
                            intensity: 1 - newState.valence,
                            timestamp: now,
                        });
                        frustrationStartTime.current = null;
                    }
                },
                {
                    // Flow Enter
                    condition: () => newState.type === "flow_state" && prevType !== "flow_state",
                    action: () => {
                        flowStateStartTime.current = now;
                        onEmotionalEvent?.({
                            type: "flow_enter",
                            emotion: "flow_state",
                            intensity: newState.arousal,
                            timestamp: now,
                        });
                    }
                },
                {
                    // Flow Exit
                    condition: () => newState.type !== "flow_state" && prevType === "flow_state",
                    action: () => {
                        const flowDuration = flowStateStartTime.current ? now - flowStateStartTime.current : 0;
                        onEmotionalEvent?.({
                            type: "flow_exit",
                            emotion: prevType,
                            intensity: flowDuration / 1000,
                            timestamp: now,
                        });
                        flowStateStartTime.current = null;
                    }
                },
                {
                    // Excitement peak
                    condition: () => newState.type === "excited" && newState.arousal > 0.8 && prevType !== "excited",
                    action: () => {
                        onEmotionalEvent?.({
                            type: "excitement_peak",
                            emotion: "excited",
                            intensity: newState.arousal,
                            timestamp: now,
                        });
                    }
                }
            ];

            // Execute matching detectors
            eventDetectors.forEach(detector => {
                if (detector.condition()) detector.action();
            });

            // Cleanup frustration timer if emotion improves
            if (newState.type !== "frustrated" && newState.type !== "stressed") {
                frustrationStartTime.current = null;
            }

            lastEmotionType.current = newState.type;
        },
        [onEmotionalEvent]
    );

    // Process audio features into emotional state
    const processEmotionalFeatures = useCallback(
        (features: EmotionalFeatures) => {
            const rawValence = analyzeValence(features);
            const rawArousal = analyzeArousal(features);
            const rawDominance = analyzeDominance(features);

            // Apply exponential smoothing
            const smoothedValence =
                smoothedState.valence * smoothingFactor + rawValence * (1 - smoothingFactor);
            const smoothedArousal =
                smoothedState.arousal * smoothingFactor + rawArousal * (1 - smoothingFactor);
            const smoothedDominance =
                smoothedState.dominance * smoothingFactor + rawDominance * (1 - smoothingFactor);

            // Classify emotion
            const emotionType = classifyEmotionFromState(
                smoothedValence,
                smoothedArousal,
                smoothedDominance
            );

            // Calculate confidence based on signal quality
            const confidence = Math.min(1, features.energy * 5);

            const newState: EmotionalState = {
                type: emotionType,
                valence: smoothedValence,
                arousal: smoothedArousal,
                dominance: smoothedDominance,
                confidence,
                timestamp: Date.now(),
            };

            // Update state
            setSmoothedState(newState);

            // Update history (keep last 100 states)
            stateHistory.current = [...stateHistory.current.slice(-99), newState];

            // Update store
            updateStoreTelemetry(newState, features);

            // Detect events
            detectEmotionalEvent(newState);

            return newState;
        },
        [
            smoothedState,
            smoothingFactor,
            updateStoreTelemetry,
            detectEmotionalEvent,
        ]
    );

    // Get emotional trend over time
    const getEmotionalTrend = useCallback(
        (windowMs: number = 30000) => {
            const now = Date.now();
            const recentStates = stateHistory.current.filter(
                (s) => now - s.timestamp < windowMs
            );

            if (recentStates.length < 2) {
                return { direction: "stable", intensity: 0 };
            }

            // Calculate linear regression on valence
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
        },
        []
    );

    // Get frustration score (used for proactive interventions)
    const getFrustrationScore = useCallback(() => {
        const recentStates = stateHistory.current.slice(-10);
        if (recentStates.length === 0) return 0;

        // Weighted average with recency bias
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
        // Current state
        emotionalState: smoothedState,

        // Processing functions
        processEmotionalFeatures,

        // Analysis functions
        getEmotionalTrend,
        getFrustrationScore,

        // State checks
        isFrustrated: smoothedState.type === "frustrated" || smoothedState.type === "stressed",
        isFlowState: smoothedState.type === "flow_state",
        isHighEnergy: smoothedState.arousal > 0.6,
        isPositive: smoothedState.valence > 0.2,

        // History
        stateHistory: stateHistory.current,
    };
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY: Extract features from audio
// ═══════════════════════════════════════════════════════════════════════════════

export function extractEmotionalFeaturesFromPCM(
    pcmData: Int16Array,
    sampleRate: number = 16000
): EmotionalFeatures {
    const samples = pcmData.length;
    const duration = samples / sampleRate;

    // Energy (RMS)
    let sumSquares = 0;
    for (let i = 0; i < samples; i++) {
        const normalized = pcmData[i] / 32768;
        sumSquares += normalized * normalized;
    }
    const energy = Math.sqrt(sumSquares / samples);

    // Zero-crossing rate
    let crossings = 0;
    for (let i = 1; i < samples; i++) {
        if ((pcmData[i] >= 0) !== (pcmData[i - 1] >= 0)) {
            crossings++;
        }
    }
    const zcr = crossings / samples;

    // Approximate pitch from ZCR (simplified)
    // ZCR ≈ 2 * frequency / sample_rate
    const pitch = (zcr * sampleRate) / 2;

    // Spectral centroid approximation using energy distribution
    // This is a simplified version - full implementation would use FFT
    const spectralCentroid = 2000 + (zcr - 0.1) * 10000;

    // Speech rate estimation (syllables per second)
    // Simplified: based on energy variations
    const speechRate = 4 + energy * 3;

    // Variance estimations (would need history for accurate values)
    const pitchVariance = pitch * 0.15;
    const energyVariance = energy * 0.2;

    return {
        pitch,
        pitchVariance,
        speechRate,
        energy,
        energyVariance,
        spectralCentroid,
        zcr,
    };
}
