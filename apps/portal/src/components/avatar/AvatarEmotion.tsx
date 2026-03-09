"use client";

import React from "react";

interface AvatarEmotionProps {
    engineState: string;
    color: string;
    intensity?: number;
}

/**
 * AvatarEmotion — Radial Dynamic Backdrop
 * 
 * Provides the "Quantum Aura" and pulsing backdrops that respond 
 * to Aether's emotional state.
 */
export function AvatarEmotion({
    engineState,
    color,
    intensity = 1
}: AvatarEmotionProps) {
    const isIdle = engineState === "IDLE";

    return (
        <>
            {/* Carbon fiber texture overlay */}
            <div
                className="absolute inset-0 opacity-10 pointer-events-none"
                style={{
                    backgroundImage: `
            linear-gradient(45deg, transparent 48%, #1a1a1a 49%, #1a1a1a 51%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, #1a1a1a 49%, #1a1a1a 51%, transparent 52%)
          `,
                    backgroundSize: "6px 6px",
                }}
            />

            {/* Dynamic Emotional Glow */}
            <div
                className="absolute inset-0 pointer-events-none"
                style={{
                    background: `radial-gradient(circle at center, ${color}20 0%, transparent 60%)`,
                    filter: `blur(${30 * intensity}px)`,
                    transition: "background 0.5s ease-in-out",
                }}
            />

            {/* State Pulse Indicator (Bottom Right) */}
            {!isIdle && (
                <div
                    className="absolute bottom-4 right-4 rounded-full"
                    style={{
                        width: 12,
                        height: 12,
                        backgroundColor: color,
                        boxShadow: `0 0 15px ${color}, 0 0 30px ${color}60`,
                        animation: "pulse 2.5s ease-in-out infinite",
                    }}
                />
            )}

            <style jsx>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; filter: brightness(1); }
          50% { transform: scale(1.35); opacity: 0.7; filter: brightness(1.5); }
        }
      `}</style>
        </>
    );
}
