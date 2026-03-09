/**
 * Aether Voice OS — Emotional Analysis Utilities.
 * 
 * Pure mathematical functions for analyzing paralinguistic features.
 */

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
    zcr: number;
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

const SPEECH_RATE_FAST = 7;

export function analyzeValence(features: EmotionalFeatures): number {
    const pitchExpressiveness = Math.min(1, features.pitchVariance / 50);
    const brightness = Math.min(1, features.spectralCentroid / 4000);
    const energyLevel = Math.min(1, features.energy * 2);

    let valence = 0;
    valence += pitchExpressiveness * 0.4;
    valence += brightness * 0.3;
    valence += energyLevel * 0.3;

    return Math.max(-1, Math.min(1, valence * 2 - 0.5));
}

export function analyzeArousal(features: EmotionalFeatures): number {
    const rateArousal = Math.min(1, features.speechRate / SPEECH_RATE_FAST);
    const energyArousal = Math.min(1, features.energy * 3);
    const pitchArousal = Math.min(1, features.pitch / 300);

    let arousal = 0;
    arousal += rateArousal * 0.4;
    arousal += energyArousal * 0.4;
    arousal += pitchArousal * 0.2;

    return Math.max(0, Math.min(1, arousal));
}

export function analyzeDominance(features: EmotionalFeatures): number {
    const controlFactor = 1 - Math.min(1, features.pitchVariance / 80);
    const steadiness = 1 - Math.min(1, features.energyVariance);

    let dominance = 0;
    dominance += controlFactor * 0.5;
    dominance += steadiness * 0.5;

    return Math.max(0, Math.min(1, dominance));
}

export function classifyEmotionFromState(
    valence: number,
    arousal: number,
    dominance: number
): EmotionType {
    if (arousal > 0.7 && valence < -0.2) return dominance > 0.5 ? "stressed" : "frustrated";
    if (arousal > 0.6 && valence > 0.2) return dominance > 0.6 ? "flow_state" : "excited";
    if (arousal > 0.3 && arousal <= 0.6 && valence > 0) return valence > 0.3 ? "curious" : "focused";
    if (arousal <= 0.3 && valence > 0) return "calm";
    if (arousal <= 0.4 && valence < -0.2) return "frustrated";
    return "neutral";
}
