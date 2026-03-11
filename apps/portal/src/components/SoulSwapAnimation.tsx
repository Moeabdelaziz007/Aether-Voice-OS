"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";

interface SoulSwapAnimationProps {
    isVisible: boolean;
    onComplete?: () => void;
}

/**
 * SoulSwapAnimation
 * A cinematic transition used when entering the Portal.
 * Uses a neural-flare effect to bridge the Landing and Portal states.
 */
export default function SoulSwapAnimation({ isVisible, onComplete }: SoulSwapAnimationProps) {
    return (
        <AnimatePresence onExitComplete={onComplete}>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-none"
                >
                    {/* Central Neural Flare */}
                    <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{
                            scale: [0, 1.2, 20],
                            opacity: [0, 1, 0],
                        }}
                        transition={{
                            duration: 1.2,
                            ease: "circIn",
                            times: [0, 0.4, 1]
                        }}
                        className="w-32 h-32 rounded-full bg-cyan-400 blur-3xl shadow-[0_0_100px_rgba(34,211,238,0.8)]"
                    />

                    {/* Full-screen flash */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: [0, 0.4, 0] }}
                        transition={{ duration: 1, delay: 0.3 }}
                        className="absolute inset-0 bg-white"
                    />

                    {/* Particle implosion hint */}
                    <div className="absolute inset-0 overflow-hidden">
                        {Array.from({ length: 20 }).map((_, i) => (
                            <motion.div
                                key={i}
                                initial={{
                                    x: (Math.random() - 0.5) * window.innerWidth * 2,
                                    y: (Math.random() - 0.5) * window.innerHeight * 2,
                                    scale: 2,
                                    opacity: 0
                                }}
                                animate={{
                                    x: 0,
                                    y: 0,
                                    scale: 0,
                                    opacity: [0, 1, 0]
                                }}
                                transition={{
                                    duration: 0.8,
                                    delay: Math.random() * 0.2,
                                    ease: "easeIn"
                                }}
                                className="absolute top-1/2 left-1/2 w-1 h-1 bg-cyan-200 rounded-full"
                            />
                        ))}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
