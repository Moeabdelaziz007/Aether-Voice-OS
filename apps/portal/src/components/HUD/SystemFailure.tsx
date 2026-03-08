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

    const baseColor = isFailed ? "rgba(239, 68, 68, " // red-500
        : isApplied ? "rgba(16, 185, 129, " // emerald-500
            : "rgba(245, 158, 11, "; // amber-500

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-[100] flex flex-col items-center justify-center pointer-events-none overflow-hidden"
                style={{
                    backgroundColor: `${baseColor}0.15)`,
                    backdropFilter: "blur(6px)",
                }}
            >
                {/* SVG Filter Definition */}
                <svg className="absolute w-0 h-0 hidden">
                    <filter id={glitchId}>
                        <feTurbulence type="fractalNoise" baseFrequency="0.01 0.2" numOctaves="3" result="noise" seed="2" />
                        <feDisplacementMap in="SourceGraphic" in2="noise" scale={isFailed ? "15" : "5"} />
                    </filter>
                svg>

                {/* Glitch Overlay Noise */}
                <div
                    className="absolute inset-0 opacity-20 pointer-events-none mix-blend-overlay"
                    style={{ backgroundImage: "url('https://grainy-gradients.vercel.app/noise.svg')" }}
                />

                <motion.div
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ 
                        scale: 1, 
                        y: 0,
                        filter: isFailed ? [`url(#${glitchId})`, "none", `url(#${glitchId})`] : "none",
                        x: isFailed ? [0, -2, 2, -1, 0] : 0
                    }}
                    exit={{ scale: 0.9, y: 20, opacity: 0 }}
                    transition={{ 
                        type: "spring", 
                        stiffness: 300, 
                        damping: 20,
                        filter: { repeat: Infinity, duration: 0.2 },
                        x: { repeat: Infinity, duration: 0.1 }
                    }}
                    className="relative px-8 py-6 max-w-2xl w-full text-center border-y"
                    style={{
                        borderColor: `${baseColor}0.5)`,
                        backgroundColor: `${baseColor}0.05)`,
                        boxShadow: `0 0 60px ${baseColor}0.2), inset 0 0 30px ${baseColor}0.1)`,
                        backdropFilter: "blur(20px)"
                    }}
                >
                    {/* Top/Bottom Scan Lines */}
                    <motion.div
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ duration: 0.5 }}
                        className="absolute top-0 left-0 right-0 h-[2px]"
                        style={{ background: `linear-gradient(90deg, transparent, ${baseColor}1), transparent)` }}
                    />
                    <motion.div
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="absolute bottom-0 left-0 right-0 h-[2px]"
                        style={{ background: `linear-gradient(90deg, transparent, ${baseColor}1), transparent)` }}
                    />

                    {/* Header */}
                    <motion.h2
                        animate={isDiagnosing || isFailed ? { 
                            opacity: [1, 0.5, 1],
                            skewX: isFailed ? [-5, 5, -5] : 0
                        } : {}}
                        transition={{ duration: isDiagnosing ? 1.5 : 0.1, repeat: Infinity }}
                        className="text-3xl font-bold tracking-[0.3em] mb-4 italic"
                        style={{ color: `${baseColor}1)`, textShadow: `0 0 25px ${baseColor}0.6)` }}
                    >
                        {isFailed ? "⊘ CRITICAL STATE_FAULT"
                            : isApplied ? "✦ NEURAL_PATCH DEPLOYED"
                                : "⚡ ANALYZING_SYSTEM_SYNC"}
                    </motion.h2>

                    {/* Main Message */}
                    <p className="text-xl font-mono text-white/90 mb-6 tracking-widest drop-shadow-md uppercase">
                        {repairState.message || (isDiagnosing ? "TRANSMISSION GAP DETECTED. RETRYING..." : "")}
                    </p>

                    {/* Log details */}
                    {repairState.log && (
                        <div className="bg-black/70 p-4 rounded text-left font-mono text-xs max-h-40 overflow-y-auto mb-6 border-l-2 pointer-events-auto"
                            style={{ borderColor: `${baseColor}0.6)`, color: `${baseColor}0.9)` }}>
                            <div className="flex items-center gap-2 mb-2 opacity-50 uppercase tracking-tighter">
                                <span className="animate-pulse">_</span>
                                <span>diagnostics_stream_v2.log</span>
                            </div>
                            <div className="break-all whitespace-pre-wrap leading-relaxed opacity-80">{repairState.log}</div>
                        </div>
                    )}

                    {/* Actionable / Loading */}
                    <div className="flex justify-center mt-4 h-12 items-center">
                        {isDiagnosing && (
                            <div className="flex gap-3">
                                {[0, 1, 2, 3, 4].map((i) => (
                                    <motion.div
                                        key={i}
                                        animate={{ height: ["32px", "4px", "32px"], opacity: [1, 0.3, 1] }}
                                        transition={{ duration: 0.6, delay: i * 0.1, repeat: Infinity }}
                                        className="w-[3px]"
                                        style={{ backgroundColor: `${baseColor}0.9)` }}
                                    />
                                ))}
                            </div>
                        )}
                        {isFailed && (
                            <button
                                onClick={() => clearRepairState()}
                                className="px-8 py-3 border-2 font-mono text-xs uppercase tracking-[0.4em] hover:bg-white/5 transition-all pointer-events-auto active:scale-95"
                                style={{ borderColor: `${baseColor}0.4)`, color: `${baseColor}1)` }}
                            >
                                [ OVERRIDE_HANDSHAKE ]
                            </button>
                        )}
                    </div>

                    {/* Auto-dismiss progress */}
                    {isApplied && (
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 4, ease: "linear" }}
                            className="h-[2px] absolute bottom-0 left-0"
                            style={{ backgroundColor: `${baseColor}0.8)` }}
                        />
                    )}
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}

