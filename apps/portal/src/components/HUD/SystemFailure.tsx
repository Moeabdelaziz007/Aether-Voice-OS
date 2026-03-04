"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * HUD: System Failure Overlay
 * Renders during autonomous healing events (`diagnosing` -> `applied` -> `failed`).
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

    if (!repairState || repairState.status === "idle") return null;

    // Determine colors and copy based on status
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
                className="absolute inset-0 z-[100] flex flex-col items-center justify-center pointer-events-none"
                style={{
                    backgroundColor: `${baseColor}0.15)`,
                    backdropFilter: "blur(4px)",
                }}
            >
                {/* Glitch Overlay Noise */}
                <div
                    className="absolute inset-0 opacity-20 pointer-events-none mix-blend-overlay"
                    style={{ backgroundImage: "url('https://grainy-gradients.vercel.app/noise.svg')" }}
                />

                <motion.div
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.9, y: 20, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    className="relative px-8 py-6 max-w-2xl w-full text-center border-y"
                    style={{
                        borderColor: `${baseColor}0.5)`,
                        backgroundColor: `${baseColor}0.1)`,
                        boxShadow: `0 0 40px ${baseColor}0.2), inset 0 0 20px ${baseColor}0.1)`,
                        backdropFilter: "blur(12px)"
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
                        animate={isDiagnosing || isFailed ? { opacity: [1, 0.5, 1] } : {}}
                        transition={{ duration: isDiagnosing ? 1.5 : 0.2, repeat: Infinity }}
                        className="text-3xl font-bold tracking-[0.2em] mb-4"
                        style={{ color: `${baseColor}1)`, textShadow: `0 0 20px ${baseColor}0.5)` }}
                    >
                        {isFailed ? "⊘ CRITICAL SYSTEM FAILURE"
                            : isApplied ? "✦ AUTONOMOUS REPAIR DEPLOYED"
                                : "⚡ ANALYZING CRITICAL FAULT"}
                    </motion.h2>

                    {/* Main Message */}
                    <p className="text-xl font-mono text-white/90 mb-6 tracking-wide drop-shadow-md">
                        {repairState.message || (isDiagnosing ? "Lost connection to neural bridge. Initiating diagnostics..." : "")}
                    </p>

                    {/* Log details */}
                    {repairState.log && (
                        <div className="bg-black/50 p-4 rounded text-left font-mono text-sm max-h-32 overflow-y-auto mb-6 border pointer-events-auto"
                            style={{ borderColor: `${baseColor}0.3)`, color: `${baseColor}0.8)` }}>
                            <div className="flex items-center gap-2 mb-2 opacity-70">
                                <span className="animate-pulse">_</span>
                                <span>diagnostics_log.txt</span>
                            </div>
                            <div className="break-all whitespace-pre-wrap">{repairState.log}</div>
                        </div>
                    )}

                    {/* Actionable or Loading Indicator */}
                    <div className="flex justify-center mt-4 h-12 items-center">
                        {isDiagnosing && (
                            <div className="flex gap-2">
                                {[0, 1, 2].map((i) => (
                                    <motion.div
                                        key={i}
                                        animate={{ height: ["24px", "8px", "24px"] }}
                                        transition={{ duration: 0.8, delay: i * 0.15, repeat: Infinity }}
                                        className="w-1"
                                        style={{ backgroundColor: `${baseColor}0.8)` }}
                                    />
                                ))}
                            </div>
                        )}
                        {isFailed && (
                            <button
                                onClick={() => clearRepairState()}
                                className="px-6 py-2 border font-mono text-sm uppercase tracking-widest hover:bg-white/10 transition-colors pointer-events-auto"
                                style={{ borderColor: `${baseColor}0.5)`, color: `${baseColor}1)` }}
                            >
                                Acknowledge & Override
                            </button>
                        )}
                    </div>
                    {/* Auto-dismiss progress bar */}
                    {isApplied && (
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 4, ease: "linear" }}
                            className="h-1 absolute bottom-0 left-0"
                            style={{ backgroundColor: `${baseColor}0.5)` }}
                        />
                    )}
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
