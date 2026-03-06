"use client";

/**
 * Aether Voice OS — Emotional Atmosphere System.
 *
 * Creates an immersive, state-responsive visual environment that
 * responds to the user's emotional state detected through voice analysis.
 *
 * The entire UI atmosphere transforms based on:
 * - Valence: Negative (-1) to Positive (+1)
 * - Arousal: Calm (0) to Excited (1)
 * - Dominance: Submissive (0) to Dominant (1)
 *
 * This creates a "Living Voice Portal" where the interface
 * breathes and responds to the user's emotional presence.
 */

import { useMemo, useEffect, useRef } from "react";
import { motion, useAnimation } from "framer-motion";
import { useAetherStore, useTelemetrySelector } from "../store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTIONAL PRESETS
// ═══════════════════════════════════════════════════════════════════════════════

interface EmotionalPreset {
    primaryColor: string;
    secondaryColor: string;
    glowIntensity: number;
    particleSpeed: number;
    backgroundGradient: string;
    orbPulse: "smooth" | "irregular" | "fast" | "slow";
    ambientSound?: string;
}

const EMOTIONAL_PRESETS: Record<string, EmotionalPreset> = {
    // Positive emotions
    flow_state: {
        primaryColor: "#39ff14", // Neon green
        secondaryColor: "#00ff41",
        glowIntensity: 1.2,
        particleSpeed: 1.5,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(57, 255, 20, 0.1) 0%, transparent 70%)",
        orbPulse: "smooth",
    },
    excited: {
        primaryColor: "#00f3ff", // Cyan
        secondaryColor: "#bc13fe", // Purple
        glowIntensity: 1.8,
        particleSpeed: 2.0,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(0, 243, 255, 0.15) 0%, rgba(188, 19, 254, 0.05) 50%, transparent 70%)",
        orbPulse: "fast",
    },
    curious: {
        primaryColor: "#bc13fe", // Purple
        secondaryColor: "#00f3ff",
        glowIntensity: 1.0,
        particleSpeed: 1.2,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(188, 19, 254, 0.1) 0%, transparent 70%)",
        orbPulse: "smooth",
    },

    // Negative emotions
    frustrated: {
        primaryColor: "#f59e0b", // Amber
        secondaryColor: "#f43f5e", // Rose
        glowIntensity: 0.8,
        particleSpeed: 0.3, // Slower, more tense
        backgroundGradient: "radial-gradient(ellipse at center, rgba(245, 158, 11, 0.12) 0%, rgba(244, 63, 94, 0.08) 50%, transparent 70%)",
        orbPulse: "irregular",
    },
    stressed: {
        primaryColor: "#f43f5e", // Rose
        secondaryColor: "#f59e0b",
        glowIntensity: 0.6,
        particleSpeed: 0.2,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(244, 63, 94, 0.15) 0%, transparent 70%)",
        orbPulse: "irregular",
    },

    // Neutral emotions
    calm: {
        primaryColor: "#22c55e", // Green
        secondaryColor: "#10b981", // Emerald
        glowIntensity: 0.7,
        particleSpeed: 0.8,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(34, 197, 94, 0.08) 0%, transparent 70%)",
        orbPulse: "slow",
    },
    focused: {
        primaryColor: "#3b82f6", // Blue
        secondaryColor: "#00f3ff",
        glowIntensity: 1.0,
        particleSpeed: 1.0,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%)",
        orbPulse: "smooth",
    },
    neutral: {
        primaryColor: "#00f3ff", // Default cyan
        secondaryColor: "#39ff14",
        glowIntensity: 0.8,
        particleSpeed: 1.0,
        backgroundGradient: "radial-gradient(ellipse at center, rgba(0, 243, 255, 0.05) 0%, transparent 70%)",
        orbPulse: "smooth",
    },
};

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTION CLASSIFIER
// ═══════════════════════════════════════════════════════════════════════════════

function classifyEmotion(
    valence: number,
    arousal: number,
    frustration: number
): string {
    // High frustration overrides other emotions
    if (frustration > 0.7) return "stressed";
    if (frustration > 0.4) return "frustrated";

    // High arousal + positive valence = excited or flow
    if (arousal > 0.7 && valence > 0.3) return "excited";
    if (arousal > 0.5 && valence > 0.5) return "flow_state";

    // High arousal + negative valence = stressed
    if (arousal > 0.6 && valence < -0.2) return "stressed";

    // Low arousal + positive valence = calm
    if (arousal < 0.3 && valence > 0.2) return "calm";

    // Moderate arousal + neutral valence = focused
    if (arousal >= 0.3 && arousal <= 0.6 && Math.abs(valence) < 0.3) return "focused";

    // Positive valence = curious
    if (valence > 0.2 && arousal > 0.4) return "curious";

    return "neutral";
}

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTIONAL ATMOSPHERE COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

interface EmotionalAtmosphereProps {
    children?: React.ReactNode;
    showDebugOverlay?: boolean;
}

export function EmotionalAtmosphere({
    children,
    showDebugOverlay = false,
}: EmotionalAtmosphereProps) {
    const { valence, arousal, engagement, frustrationScore } = useTelemetrySelector();
    const engineState = useAetherStore((s) => s.engineState);
    const controls = useAnimation();

    // Classify current emotion
    const currentEmotion = useMemo(() => {
        return classifyEmotion(valence, arousal, frustrationScore);
    }, [valence, arousal, frustrationScore]);

    // Get preset for current emotion
    const preset = useMemo(() => {
        return EMOTIONAL_PRESETS[currentEmotion] || EMOTIONAL_PRESETS.neutral;
    }, [currentEmotion]);

    // Smooth transition between emotional states
    useEffect(() => {
        controls.start({
            background: preset.backgroundGradient,
            transition: { duration: 1.5, ease: "easeInOut" },
        });
    }, [preset, controls]);

    // Calculate dynamic values based on emotional intensity
    const emotionalIntensity = useMemo(() => {
        return Math.min(1, Math.abs(valence) * 0.5 + arousal * 0.5 + frustrationScore * 0.3);
    }, [valence, arousal, frustrationScore]);

    return (
        <div className="emotional-atmosphere">
            {/* Background Gradient Layer */}
            <motion.div
                className="fixed inset-0 pointer-events-none z-0"
                animate={controls}
                style={{
                    background: preset.backgroundGradient,
                }}
            />

            {/* Chromatic Edge Glow */}
            <EdgeGlow
                primaryColor={preset.primaryColor}
                intensity={preset.glowIntensity * emotionalIntensity}
            />

            {/* Floating Particles */}
            <EmotionalParticles
                color={preset.primaryColor}
                speed={preset.particleSpeed}
                intensity={emotionalIntensity}
            />

            {/* Pulsing Aura */}
            <EmotionalAura
                color={preset.primaryColor}
                secondaryColor={preset.secondaryColor}
                intensity={preset.glowIntensity}
                pulseType={preset.orbPulse}
            />

            {/* Debug Overlay */}
            {showDebugOverlay && (
                <div className="fixed bottom-4 left-4 z-50 bg-black/80 text-white text-xs font-mono p-3 rounded-lg border border-white/20">
                    <div className="mb-1 font-bold text-cyan-400">Emotional State</div>
                    <div>Emotion: <span className="text-green-400">{currentEmotion}</span></div>
                    <div>Valence: {valence.toFixed(2)}</div>
                    <div>Arousal: {arousal.toFixed(2)}</div>
                    <div>Frustration: {frustrationScore.toFixed(2)}</div>
                    <div>Intensity: {emotionalIntensity.toFixed(2)}</div>
                </div>
            )}

            {/* Main Content */}
            <div className="relative z-10">
                {children}
            </div>

            {/* CSS Animations */}
            <style jsx>{`
                .emotional-atmosphere {
                    position: relative;
                    min-height: 100vh;
                    overflow: hidden;
                }

                @keyframes pulse-smooth {
                    0%, 100% { opacity: 0.6; transform: scale(1); }
                    50% { opacity: 1; transform: scale(1.05); }
                }

                @keyframes pulse-fast {
                    0%, 100% { opacity: 0.8; transform: scale(1); }
                    50% { opacity: 1; transform: scale(1.1); }
                }

                @keyframes pulse-slow {
                    0%, 100% { opacity: 0.5; transform: scale(1); }
                    50% { opacity: 0.8; transform: scale(1.02); }
                }

                @keyframes pulse-irregular {
                    0% { opacity: 0.7; transform: scale(1); }
                    25% { opacity: 0.5; transform: scale(0.98); }
                    50% { opacity: 0.9; transform: scale(1.05); }
                    75% { opacity: 0.6; transform: scale(1.02); }
                    100% { opacity: 0.7; transform: scale(1); }
                }
            `}</style>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// EDGE GLOW COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

interface EdgeGlowProps {
    primaryColor: string;
    intensity: number;
}

function EdgeGlow({ primaryColor, intensity }: EdgeGlowProps) {
    return (
        <motion.div
            className="fixed inset-0 pointer-events-none z-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: intensity * 0.8 }}
            transition={{ duration: 1 }}
        >
            {/* Top edge */}
            <div
                className="absolute top-0 left-0 right-0 h-1"
                style={{
                    background: `linear-gradient(to bottom, ${primaryColor}, transparent)`,
                    boxShadow: `0 0 ${30 * intensity}px ${primaryColor}`,
                }}
            />

            {/* Bottom edge */}
            <div
                className="absolute bottom-0 left-0 right-0 h-1"
                style={{
                    background: `linear-gradient(to top, ${primaryColor}, transparent)`,
                    boxShadow: `0 0 ${30 * intensity}px ${primaryColor}`,
                }}
            />

            {/* Left edge */}
            <div
                className="absolute top-0 bottom-0 left-0 w-1"
                style={{
                    background: `linear-gradient(to right, ${primaryColor}, transparent)`,
                    boxShadow: `0 0 ${30 * intensity}px ${primaryColor}`,
                }}
            />

            {/* Right edge */}
            <div
                className="absolute top-0 bottom-0 right-0 w-1"
                style={{
                    background: `linear-gradient(to left, ${primaryColor}, transparent)`,
                    boxShadow: `0 0 ${30 * intensity}px ${primaryColor}`,
                }}
            />
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTIONAL PARTICLES COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

interface EmotionalParticlesProps {
    color: string;
    speed: number;
    intensity: number;
}

function EmotionalParticles({ color, speed, intensity }: EmotionalParticlesProps) {
    const particleCount = Math.floor(50 * intensity);

    return (
        <div className="fixed inset-0 pointer-events-none z-2 overflow-hidden">
            {Array.from({ length: particleCount }).map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 rounded-full"
                    style={{
                        backgroundColor: color,
                        boxShadow: `0 0 ${6 * intensity}px ${color}`,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                    }}
                    animate={{
                        y: [0, -100 * speed],
                        x: [0, (Math.random() - 0.5) * 50 * speed],
                        opacity: [0, 1, 0],
                        scale: [0.5, 1, 0.5],
                    }}
                    transition={{
                        duration: 3 / speed,
                        repeat: Infinity,
                        delay: Math.random() * 2,
                        ease: "easeOut",
                    }}
                />
            ))}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// EMOTIONAL AURA COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

interface EmotionalAuraProps {
    color: string;
    secondaryColor: string;
    intensity: number;
    pulseType: "smooth" | "irregular" | "fast" | "slow";
}

function EmotionalAura({ color, secondaryColor, intensity, pulseType }: EmotionalAuraProps) {
    const animationName = `pulse-${pulseType}`;

    return (
        <div className="fixed inset-0 pointer-events-none z-1 flex items-center justify-center">
            {/* Outer aura */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: "80vmin",
                    height: "80vmin",
                    background: `radial-gradient(circle, transparent 40%, ${color}15 60%, transparent 70%)`,
                    filter: `blur(${40 * intensity}px)`,
                }}
                animate={{
                    scale: [1, 1.1, 1],
                    opacity: [0.3, 0.5, 0.3],
                }}
                transition={{
                    duration: pulseType === "fast" ? 1.5 : pulseType === "slow" ? 4 : 2.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
            />

            {/* Inner aura */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: "40vmin",
                    height: "40vmin",
                    background: `radial-gradient(circle, ${color}10 0%, ${secondaryColor}05 50%, transparent 70%)`,
                    filter: `blur(${20 * intensity}px)`,
                }}
                animate={{
                    scale: [1, 1.05, 1],
                    opacity: [0.4, 0.6, 0.4],
                }}
                transition={{
                    duration: pulseType === "fast" ? 1 : pulseType === "slow" ? 3 : 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 0.5,
                }}
            />
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK: USE EMOTIONAL STATE
// ═══════════════════════════════════════════════════════════════════════════════

export function useEmotionalState() {
    const { valence, arousal, engagement, frustrationScore } = useTelemetrySelector();

    const emotion = useMemo(() => {
        return classifyEmotion(valence, arousal, frustrationScore);
    }, [valence, arousal, frustrationScore]);

    const preset = useMemo(() => {
        return EMOTIONAL_PRESETS[emotion] || EMOTIONAL_PRESETS.neutral;
    }, [emotion]);

    const intensity = useMemo(() => {
        return Math.min(1, Math.abs(valence) * 0.5 + arousal * 0.5 + frustrationScore * 0.3);
    }, [valence, arousal, frustrationScore]);

    return {
        emotion,
        preset,
        valence,
        arousal,
        engagement,
        frustrationScore,
        intensity,
        isPositive: valence > 0.2,
        isNegative: valence < -0.2,
        isHighEnergy: arousal > 0.6,
        isLowEnergy: arousal < 0.3,
    };
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export { EMOTIONAL_PRESETS, classifyEmotion };
