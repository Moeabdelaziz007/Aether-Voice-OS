"use client";

/**
 * EdgeGlow — Advanced Neural Chromatic Border
 * 
 * Multi-layered glowing edge effect that responds to system state.
 * Creates an immersive feeling of energy flowing around the screen.
 * 
 * Features:
 * - State-responsive glow intensity
 * - Animated gradient flow
 * - Corner accent highlights
 * - Pulse effects during voice activity
 */

import { useMemo } from "react";
import { motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

export default function EdgeGlow() {
    const engineState = useAetherStore((s) => s.engineState);
    const speakerLevel = useAetherStore((s) => s.speakerLevel);
    const micLevel = useAetherStore((s) => s.micLevel);

    // State-based configuration
    const config = useMemo(() => {
        switch (engineState) {
            case "SPEAKING":
                return { 
                    opacity: 0.8 + speakerLevel * 0.2, 
                    intensity: 1.5,
                    pulseSpeed: 1.5,
                    color: "39, 255, 20" // Neon green
                };
            case "LISTENING":
                return { 
                    opacity: 0.5 + micLevel * 0.3, 
                    intensity: 1.0,
                    pulseSpeed: 2.0,
                    color: "57, 255, 20" // Bright green
                };
            case "THINKING":
                return { 
                    opacity: 0.6, 
                    intensity: 1.2,
                    pulseSpeed: 0.8,
                    color: "255, 215, 0" // Gold
                };
            case "INTERRUPTING":
                return { 
                    opacity: 0.9, 
                    intensity: 2.0,
                    pulseSpeed: 3.0,
                    color: "255, 23, 68" // Crimson
                };
            default:
                return { 
                    opacity: 0.15, 
                    intensity: 0.5,
                    pulseSpeed: 0,
                    color: "26, 92, 26" // Dim green
                };
        }
    }, [engineState, speakerLevel, micLevel]);

    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

    return (
        <>
            {/* Main Edge Glow */}
            <motion.div 
                className="fixed inset-0 pointer-events-none z-50"
                animate={{ opacity: config.opacity }}
                transition={{ duration: 0.3 }}
                style={{
                    boxShadow: `
                        inset 0 0 ${80 * config.intensity}px rgba(${config.color}, 0.15),
                        inset 0 0 ${40 * config.intensity}px rgba(${config.color}, 0.1),
                        inset 0 0 ${20 * config.intensity}px rgba(${config.color}, 0.05)
                    `,
                }}
            />

            {/* Animated Edge Border */}
            <div 
                className="fixed inset-0 pointer-events-none z-50"
                style={{ 
                    opacity: config.opacity * 0.8,
                    border: `1px solid rgba(${config.color}, 0.2)`,
                    borderRadius: '0px',
                }}
            />

            {/* Top Edge Glow Line */}
            <motion.div
                className="fixed top-0 left-0 right-0 h-[2px] pointer-events-none z-50"
                style={{
                    background: `linear-gradient(90deg, 
                        transparent 0%, 
                        rgba(${config.color}, ${0.6 * config.intensity}) 20%, 
                        rgba(${config.color}, ${0.9 * config.intensity}) 50%, 
                        rgba(${config.color}, ${0.6 * config.intensity}) 80%, 
                        transparent 100%
                    )`,
                    boxShadow: `
                        0 0 ${20 * config.intensity}px rgba(${config.color}, 0.5),
                        0 0 ${40 * config.intensity}px rgba(${config.color}, 0.3)
                    `,
                }}
                animate={{
                    scaleX: [1, 1.02 + audioLevel * 0.03, 1],
                }}
                transition={{
                    duration: config.pulseSpeed || 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
            />

            {/* Bottom Edge Glow Line */}
            <motion.div
                className="fixed bottom-0 left-0 right-0 h-[2px] pointer-events-none z-50"
                style={{
                    background: `linear-gradient(90deg, 
                        transparent 0%, 
                        rgba(${config.color}, ${0.5 * config.intensity}) 20%, 
                        rgba(${config.color}, ${0.8 * config.intensity}) 50%, 
                        rgba(${config.color}, ${0.5 * config.intensity}) 80%, 
                        transparent 100%
                    )`,
                    boxShadow: `
                        0 0 ${15 * config.intensity}px rgba(${config.color}, 0.4),
                        0 0 ${30 * config.intensity}px rgba(${config.color}, 0.2)
                    `,
                }}
                animate={{
                    scaleX: [1, 1.02 + audioLevel * 0.03, 1],
                }}
                transition={{
                    duration: config.pulseSpeed || 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 0.5,
                }}
            />

            {/* Left Edge Glow Line */}
            <motion.div
                className="fixed top-0 bottom-0 left-0 w-[2px] pointer-events-none z-50"
                style={{
                    background: `linear-gradient(180deg, 
                        transparent 0%, 
                        rgba(${config.color}, ${0.4 * config.intensity}) 20%, 
                        rgba(${config.color}, ${0.7 * config.intensity}) 50%, 
                        rgba(${config.color}, ${0.4 * config.intensity}) 80%, 
                        transparent 100%
                    )`,
                    boxShadow: `
                        0 0 ${12 * config.intensity}px rgba(${config.color}, 0.3),
                        0 0 ${25 * config.intensity}px rgba(${config.color}, 0.15)
                    `,
                }}
            />

            {/* Right Edge Glow Line */}
            <motion.div
                className="fixed top-0 bottom-0 right-0 w-[2px] pointer-events-none z-50"
                style={{
                    background: `linear-gradient(180deg, 
                        transparent 0%, 
                        rgba(${config.color}, ${0.4 * config.intensity}) 20%, 
                        rgba(${config.color}, ${0.7 * config.intensity}) 50%, 
                        rgba(${config.color}, ${0.4 * config.intensity}) 80%, 
                        transparent 100%
                    )`,
                    boxShadow: `
                        0 0 ${12 * config.intensity}px rgba(${config.color}, 0.3),
                        0 0 ${25 * config.intensity}px rgba(${config.color}, 0.15)
                    `,
                }}
            />

            {/* Corner Accents */}
            {["top-0 left-0", "top-0 right-0", "bottom-0 left-0", "bottom-0 right-0"].map((position, i) => (
                <motion.div
                    key={i}
                    className={`fixed ${position} w-16 h-16 pointer-events-none z-50`}
                    style={{
                        background: `radial-gradient(circle at ${
                            position.includes("left") ? "0% " : "100% "
                        }${position.includes("top") ? "0%" : "100%"}, 
                            rgba(${config.color}, ${0.3 * config.intensity}) 0%, 
                            transparent 70%
                        )`,
                    }}
                    animate={{
                        opacity: [0.5, 1, 0.5],
                        scale: [1, 1.1 + audioLevel * 0.1, 1],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: i * 0.3,
                    }}
                />
            ))}

            {/* Scan Line Effect (when active) */}
            {(engineState === "SPEAKING" || engineState === "THINKING") && (
                <motion.div
                    className="fixed left-0 right-0 h-[1px] pointer-events-none z-50"
                    style={{
                        background: `linear-gradient(90deg, 
                            transparent 0%, 
                            rgba(${config.color}, 0.5) 50%, 
                            transparent 100%
                        )`,
                        boxShadow: `0 0 10px rgba(${config.color}, 0.4)`,
                    }}
                    animate={{
                        top: ["0%", "100%", "0%"],
                    }}
                    transition={{
                        duration: 8,
                        repeat: Infinity,
                        ease: "linear",
                    }}
                />
            )}
        </>
    );
}
