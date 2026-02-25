"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface LiveWaveLineProps {
    isListening: boolean;
    audioData?: number[]; // Array of values 0-1
}

export const LiveWaveLine: React.FC<LiveWaveLineProps> = ({ isListening, audioData = [] }) => {
    const [bars, setBars] = useState<number[]>(Array(40).fill(0.1));

    useEffect(() => {
        let animationFrame: number;
        let isActive = true;

        const animate = () => {
            if (!isActive) return;

            setBars((prevBars) => {
                return prevBars.map((_, i) => {
                    if (!isListening) {
                        // Idle state: smooth small sine wave
                        const time = Date.now() / 1000;
                        return 0.1 + Math.sin(time * 2 + i * 0.2) * 0.05;
                    }

                    // Active speaking state
                    if (audioData.length > 0) {
                        // Map actual audio data if provided
                        const value = audioData[i % audioData.length] || 0;
                        return 0.1 + value * 0.8; // scale to 0.1 - 0.9
                    } else {
                        // Simulated active speaking state if no data provided
                        const randomJitter = Math.random() * 0.4;
                        const centerPeak = 1 - Math.abs(i - 20) / 20; // 0 to 1 peak in center
                        return 0.1 + centerPeak * 0.6 + randomJitter;
                    }
                });
            });

            animationFrame = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            isActive = false;
            cancelAnimationFrame(animationFrame);
        };
    }, [isListening, audioData]);

    return (
        <div className="flex items-center justify-center gap-[3px] h-24 w-full px-4 overflow-hidden relative">
            {/* Glow effect back layer */}
            <div className="absolute inset-0 bg-blue-500/10 blur-3xl rounded-full" />

            {bars.map((height, i) => (
                <motion.div
                    key={i}
                    animate={{
                        height: `${Math.max(10, height * 100)}%`,
                        backgroundColor: isListening
                            ? i % 3 === 0
                                ? "#60A5FA" // blue-400
                                : i % 3 === 1
                                    ? "#A78BFA" // violet-400
                                    : "#F472B6" // pink-400
                            : "#4B5563", // gray-600
                    }}
                    transition={{
                        type: "spring",
                        damping: 15,
                        stiffness: 200,
                        mass: 0.5,
                    }}
                    className="w-1.5 rounded-full"
                    style={{
                        boxShadow: isListening ? "0 0 10px rgba(96, 165, 250, 0.5)" : "none",
                    }}
                />
            ))}
        </div>
    );
};
