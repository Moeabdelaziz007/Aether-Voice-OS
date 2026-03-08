"use client";

import React, { useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * HUD: System Failure Overlay
 * Renders during autonomous healing events (`diagnosing` -> `applied` -> `failed`).
 * Enhanced with SVG Glitch Filters (V2.3)
 */
export default function SystemFailure() {
    const repairState = useAetherStore((s) => s.repairState);
    const clearRepairState = useAetherStore((s) => s.clearRepairState);

    // Auto-dismiss after 4 seconds if applied successfully
    useEffect(() => {
        if (repairState?.status === "applied") {
            const timer = setTimeout(() => {
                clearRepairState();
            }, 4000);
            return () => clearTimeout(timer);
        }
    }, [repairState?.status, clearRepairState]);

    const glitchId = useMemo(() => `glitch-filter-${Math.random().toString(36).substr(2, 9)}`, []);

    if (!repairState || repairState.status === "idle") return null;

    const isDiagnosing = repairState.status === "diagnosing";
    const isFailed = repairState.status === "failed";
    const isApplied = repairState.status === "applied";

    const baseColor = isFailed ? "rgba(255, 0, 60, " // Radically neon red
        : isApplied ? "rgba(0, 255, 170, " // Cyber emerald
            : "rgba(255, 170, 0, "; // Neon amber

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-[100] flex flex-col items-center justify-center pointer-events-none overflow-hidden system-failure-overlay"
                style={{
                    backgroundColor: `${baseColor}0.12)`,
                }}
            >
                {/* SVG Filter Definition */}
                <svg className="absolute w-0 h-0 hidden">
                    <filter id={glitchId}>
                        <feTurbulence type="fractalNoise" baseFrequency="0.05 0.5" numOctaves="3" result="noise" seed="5" />
                        <feDisplacementMap in="SourceGraphic" in2="noise" scale={isFailed ? "25" : "8"} />
                    </filter>
                </svg>

                {/* Glitch Overlay Noise (Animated) */}
                <motion.div
                    animate={{
                        opacity: [0.1, 0.2, 0.15, 0.25, 0.1],
                        x: [0, -10, 10, -5, 0],
                    }}
                    transition={{ repeat: Infinity, duration: 0.1 }}
                    className="absolute inset-0 pointer-events-none mix-blend-overlay"
                    style={{
                        backgroundImage: "url('https://grainy-gradients.vercel.app/noise.svg')",
                        backgroundSize: "200px 200px"
                    }}
                />

                <motion.div
                    initial={{ scale: 0.85, opacity: 0 }}
                    animate={{
                        scale: 1,
                        opacity: 1,
                        filter: isFailed ? [`url(#${glitchId})`, "none", `url(#${glitchId})`] : "none",
                        x: isFailed ? [0, -4, 4, -2, 0] : 0,
                        skewY: isFailed ? [0, -1, 1, 0] : 0
                    }}
                    exit={{ scale: 1.1, opacity: 0, filter: "blur(20px)" }}
                    transition={{
                        type: "spring",
                        stiffness: 400,
                        damping: 15,
                        filter: { repeat: Infinity, duration: 0.15 },
                        x: { repeat: Infinity, duration: 0.08 },
                        skewY: { repeat: Infinity, duration: 0.12 }
                    }}
                    className="relative px-12 py-10 max-w-2xl w-full text-center border-y-2"
                    style={{
                        borderColor: `${baseColor}0.6)`,
                        backgroundColor: "rgba(10, 10, 10, 0.85)",
                        boxShadow: `0 0 100px ${baseColor}0.25), inset 0 0 50px ${baseColor}0.15)`,
                        borderImage: `linear-gradient(90deg, transparent, ${baseColor}0.8), transparent) 1`
                    }}
                >
                    {/* Chromatic Aberration RGB Layers (Simulated for text) */}
                    {isFailed && (
                        <>
                            <motion.div
                                className="absolute inset-0 flex items-center justify-center opacity-40 mix-blend-screen pointer-events-none"
                                animate={{ x: [-2, 2, -1], y: [1, -1, 0] }}
                                transition={{ repeat: Infinity, duration: 0.1 }}
                                style={{ color: "#0FF" }} // Cyan
                            >
                                <div className="text-3xl font-bold tracking-[0.3em] mb-4 italic opacity-0">⊘ CRITICAL STATE_FAULT</div>
                            </motion.div>
                            <motion.div
                                className="absolute inset-0 flex items-center justify-center opacity-40 mix-blend-screen pointer-events-none"
                                animate={{ x: [2, -2, 1], y: [-1, 1, 0] }}
                                transition={{ repeat: Infinity, duration: 0.12 }}
                                style={{ color: "#F0F" }} // Magenta
                            >
                                <div className="text-3xl font-bold tracking-[0.3em] mb-4 italic opacity-0">⊘ CRITICAL STATE_FAULT</div>
                            </motion.div>
                        </>
                    )}

                    {/* Top/Bottom Scan Lines (High Intensity) */}
                    <div className="absolute top-0 left-0 right-0 h-[3px] bg-white opacity-20 blur-sm animate-pulse" />
                    <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-white opacity-20 blur-sm animate-pulse" />

                    {/* Header */}
                    <motion.h2
                        animate={isDiagnosing || isFailed ? {
                            opacity: [1, 0.3, 1, 0.8, 1],
                            scale: [1, 1.02, 0.98, 1]
                        } : {}}
                        transition={{ duration: 0.12, repeat: Infinity }}
                        className="text-4xl font-extrabold tracking-[0.4em] mb-6 italic z-10 relative uppercase"
                        style={{
                            color: `${baseColor}1)`,
                            textShadow: `0 0 30px ${baseColor}0.8), 0 0 60px ${baseColor}0.4)`
                        }}
                    >
                        {isFailed ? "⊘ CRITICAL STATE_FAULT"
                            : isApplied ? "✦ NEURAL_PATCH DEPLOYED"
                                : "⚡ ANALYZING_SYSTEM_SYNC"}
                    </motion.h2>

                    {/* Main Message */}
                    <p className="text-xl font-mono text-white/90 mb-8 tracking-[0.2em] drop-shadow-lg uppercase leading-relaxed">
                        {repairState.message || (isDiagnosing ? "TRANSMISSION GAP DETECTED. RETRYING..." : "")}
                    </p>

                    {/* Log details (Industrial terminal style) */}
                    {repairState.log && (
                        <div className="bg-black/90 p-6 rounded-sm text-left font-mono text-xs max-h-48 overflow-y-auto mb-8 border border-white/10 pointer-events-auto shadow-2xl system-failure-log">
                            <div className="flex items-center justify-between mb-3 opacity-60 uppercase tracking-widest text-[10px]">
                                <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full animate-pulse system-failure-indicator" />
                                    <span>diagnostics_v4.0.96.log</span>
                                </div>
                                <span>{new Date().toLocaleTimeString()}</span>
                            </div>
                            <div className="break-all whitespace-pre-wrap leading-loose opacity-90 font-medium selection:bg-white/20">
                                {`[SYSTEM_KERN]: ${repairState.log}`}
                            </div>
                        </div>
                    )}

                    {/* Actionable / Loading */}
                    <div className="flex justify-center mt-6 h-14 items-center gap-8">
                        {isDiagnosing && (
                            <div className="flex gap-4">
                                {[0, 1, 2, 3, 4, 5, 6].map((i) => (
                                    <motion.div
                                        key={i}
                                        animate={{ height: ["48px", "8px", "48px"], opacity: [1, 0.2, 1] }}
                                        transition={{ duration: 0.4, delay: i * 0.05, repeat: Infinity }}
                                        className="w-[4px]"
                                        style={{ backgroundColor: `${baseColor}1)`, boxShadow: `0 0 10px ${baseColor}0.5)` }}
                                    />
                                ))}
                            </div>
                        )}
                        {isFailed && (
                            <button
                                onClick={() => clearRepairState()}
                                className="px-12 py-4 border-2 font-black text-sm uppercase tracking-[0.5em] backdrop-blur-md transition-all pointer-events-auto active:scale-90 hover:tracking-[0.6em] system-failure-override"
                            >
                                [ FORCE_OVERRIDE ]
                            </button>
                        )}
                    </div>

                    {/* Auto-dismiss progress */}
                    {isApplied && (
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 4, ease: "linear" }}
                            className="h-[4px] absolute bottom-0 left-0"
                            style={{
                                background: `linear-gradient(90deg, transparent, ${baseColor}1))`,
                                boxShadow: `0 0 20px ${baseColor}0.8)`
                            }}
                        />
                    )}
                </motion.div>

                <style jsx>{`
                    .system-failure-overlay {
                        backdrop-filter: blur(12px) saturate(1.5);
                    }
                    .system-failure-log {
                        border-left: 4px solid ${baseColor}0.8);
                        color: ${baseColor}1);
                    }
                    .system-failure-indicator {
                        background-color: ${baseColor}1);
                    }
                    .system-failure-override {
                        border-color: ${baseColor}0.5);
                        color: ${baseColor}1);
                        text-shadow: 0 0 10px ${baseColor}0.5);
                    }
                `}</style>
            </motion.div>
        </AnimatePresence>

    );
}

