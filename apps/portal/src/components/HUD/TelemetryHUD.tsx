"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * TelemetryHUD — The Minimalist Cyberpunk RTT Tracker
 *
 * Displays a thin status bar at the bottom representing connection health.
 * On click, expands into a detailed visual overlay showing metrics.
 */
export default function TelemetryHUD() {
    const [expanded, setExpanded] = useState(false);

    // Subscribe to store metrics
    const latencyMs = useAetherStore(s => s.latencyMs || 0);
    const status = useAetherStore(s => s.status);
    const micLevel = useAetherStore(s => s.micLevel || 0);
    const speakerLevel = useAetherStore(s => s.speakerLevel || 0);

    // Color logic
    let statusColor = "bg-white/20"; // disconnected
    let textColor = "text-white/50";
    if (status === "connected") {
        if (latencyMs < 100) { statusColor = "bg-neon-cyan"; textColor = "text-neon-cyan"; }
        else if (latencyMs < 300) { statusColor = "bg-amber-400"; textColor = "text-amber-400"; }
        else { statusColor = "bg-red-500"; textColor = "text-red-500"; }
    } else if (status === "connecting" || status === "reconnecting") {
        statusColor = "bg-purple-500"; textColor = "text-purple-400";
    } else if (status === "error") {
        statusColor = "bg-red-600"; textColor = "text-red-500";
    }

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 flex flex-col items-center pointer-events-none">

            {/* Expanded Detailed Overlay */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="pointer-events-auto bg-black/80 backdrop-blur-md border border-white/10 rounded-t-xl p-4 mb-2 shadow-lg shadow-neon-cyan/10 w-80 font-mono text-[10px] uppercase tracking-wider"
                    >
                        <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
                            <span className="text-neon-cyan">Neural Uplink Stats</span>
                            <button onClick={() => setExpanded(false)} className="text-white/40 hover:text-white">✕</button>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-white/50">State</span>
                                <span className={textColor}>{status.toUpperCase()}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/50">Internal RTT</span>
                                <span className={textColor}>{latencyMs} ms</span>
                            </div>

                            {/* Visual Levels */}
                            <div className="pt-2">
                                <div className="flex justify-between mb-1">
                                    <span className="text-white/50">Input (Mic)</span>
                                    <span className="text-neon-pink">{(micLevel * 100).toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                                    <div className="bg-neon-pink h-full transition-all duration-75" style={{ width: `${Math.min(100, micLevel * 200)}%` }} />
                                </div>
                            </div>

                            <div>
                                <div className="flex justify-between mb-1">
                                    <span className="text-white/50">Output (Speaker)</span>
                                    <span className="text-neon-cyan">{(speakerLevel * 100).toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                                    <div className="bg-neon-cyan h-full transition-all duration-75" style={{ width: `${Math.min(100, speakerLevel * 200)}%` }} />
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Minimalist Bottom Bar */}
            <div
                onClick={() => setExpanded(!expanded)}
                className="pointer-events-auto cursor-pointer flex items-center justify-center w-full h-1 group hover:h-4 transition-all duration-200 bg-black/40"
            >
                {/* Latency Indicator Line */}
                <div className={`h-full transition-all duration-300 ${statusColor} shadow-[0_0_10px_rgba(255,255,255,0.2)]`} style={{ width: status === 'connected' ? '30%' : '100%' }} />

                {/* Hover text indicator */}
                <div className="absolute bottom-1 text-[9px] font-mono opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 px-2 rounded backdrop-blur">
                    <span className={textColor}>NET: {status === 'connected' ? `${latencyMs}ms` : status.toUpperCase()}</span>
                </div>
            </div>
        </div>
    );
}
