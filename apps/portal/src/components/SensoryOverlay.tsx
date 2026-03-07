"use client";

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * SensoryOverlay — Global animation engine for AetherOS.
 * Renders high-fidelity effects like LaserScan, SoulSwap, and SparkFX.
 */
export const SensoryOverlay: React.FC = () => {
    const trigger = useAetherStore((s) => s.animationTrigger);

    return (
        <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
            <AnimatePresence>
                {/* 1. Laser Scan Effect (File Drop) */}
                {trigger === 'laser-scan' && (
                    <motion.div
                        key="laser-scan"
                        initial={{ top: '-10%' }}
                        animate={{ top: '110%' }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 1.5, ease: "easeInOut" }}
                        className="absolute left-0 right-0 h-[2px] bg-cyan-400 shadow-[0_0_25px_#22d3ee,0_0_50px_#22d3ee] z-10"
                    >
                        {/* Scan Flare */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent blur-md" />
                    </motion.div>
                )}

                {/* 2. Soul Swap Animation (Context Absorption) */}
                {trigger === 'soul-swap' && (
                    <motion.div
                        key="soul-swap"
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: [0, 1, 0], scale: [0.5, 1.5, 2] }}
                        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96"
                    >
                        {/* Particle Dissolve */}
                        <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/30 to-cyan-500/30 blur-3xl rounded-full animate-pulse" />
                        <motion.div
                            className="absolute inset-0 border-2 border-white/20 rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        />
                    </motion.div>
                )}

                {/* 3. High Voltage Spark (Skill Injection) */}
                {trigger === 'high-voltage' && (
                    <motion.div
                        key="high-voltage"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: [0, 1, 0, 1, 0] }}
                        className="absolute inset-0 bg-white/5 backdrop-invert-[0.1]"
                    >
                        {/* Crackle Lines */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                            {[1, 2, 3].map((i) => (
                                <motion.div
                                    key={i}
                                    className="absolute w-1 h-32 bg-cyan-300 blur-sm"
                                    animate={{
                                        rotate: [0, 45, -45, 90, 0],
                                        scaleY: [1, 1.5, 0.8, 1.2, 1],
                                        opacity: [1, 0.5, 1, 0.8, 1]
                                    }}
                                    transition={{ duration: 0.2, repeat: 10 }}
                                />
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* 4. Data Tether Stream (Semantic Linking) */}
                {trigger === 'tether-stream' && (
                    <div className="absolute inset-0">
                        {/* This would ideally use an SVG path connector between source and destination */}
                        {/* Animated overlay for now */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-cyan-500/5 backdrop-blur-[1px]"
                        />
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default SensoryOverlay;
