"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useVisionPulse } from "@/hooks/useVisionPulse";

/**
 * VisionFeed — The "Aether Retina".
 * Displays a real-time PIP (Picture-in-Picture) of what Aether perceives.
 */
export const VisionFeed: React.FC = () => {
    const { latestFrame, isCapturing, frameCount, startCapture } = useVisionPulse();

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="fixed bottom-10 right-10 w-64 aspect-video z-50 pointer-events-auto group"
        >
            {/* Border Scaffolding */}
            <div className="absolute inset-0 border border-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.2)] bg-black/40 backdrop-blur-md overflow-hidden rounded-sm">

                {/* Visual Feed */}
                <AnimatePresence mode="wait">
                    {isCapturing && latestFrame ? (
                        <motion.div
                            key="feed"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="relative w-full h-full"
                        >
                            <img
                                src={`data:image/jpeg;base64,${latestFrame}`}
                                alt="Aether Vision"
                                className="w-full h-full object-cover opacity-80 grayscale-[0.3] sepia-[0.2] brightness-125"
                                style={{
                                    filter: "contrast(1.2) hue-rotate(-10deg) saturate(1.5)"
                                }}
                            />

                            {/* Scanning Overlay inside individual PIP */}
                            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                                <motion.div
                                    animate={{ top: ["0%", "100%"] }}
                                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                                    className="absolute left-0 right-0 h-[2px] bg-cyan-400/30 shadow-[0_0_10px_rgba(34,211,238,0.5)] z-10"
                                />
                                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_2px] opacity-30" />
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="offline"
                            className="w-full h-full flex flex-col items-center justify-center gap-3 bg-neutral-900/80"
                        >
                            <div className="w-8 h-8 border-2 border-dashed border-red-500/50 rounded-full animate-spin" />
                            <span className="text-[10px] font-mono text-red-500/70 tracking-tighter uppercase italic">
                                {isCapturing ? "AQUIRING DATA..." : "VISION OFFLINE"}
                            </span>
                            {!isCapturing && (
                                <button
                                    onClick={startCapture}
                                    className="px-3 py-1 border border-cyan-500/30 text-[9px] text-cyan-400 font-mono hover:bg-cyan-500/10 transition-colors uppercase tracking-widest"
                                >
                                    Enable Retina
                                </button>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Tactical Overlays */}
                <div className="absolute top-2 left-2 flex items-center gap-1.5 z-20">
                    <div className={`w-1.5 h-1.5 rounded-full ${isCapturing ? 'bg-red-500 animate-pulse' : 'bg-neutral-600'}`} />
                    <span className="text-[8px] font-mono text-white/50 tracking-widest uppercase">
                        {isCapturing ? `LIVE_FEED::FMR_${frameCount}` : "IDLE"}
                    </span>
                </div>

                <div className="absolute bottom-2 right-2 text-[8px] font-mono text-cyan-400/60 z-20">
                    RES: 960x540 | Q: 0.4
                </div>

                {/* Chromatic Aberration Edge (Subtle) */}
                <div className="absolute inset-0 pointer-events-none border border-white/5 opacity-20" />
            </div>

            {/* Corner Markers (Component Level) */}
            <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-cyan-400/50" />
            <div className="absolute -top-1 -right-1 w-2 h-2 border-t border-r border-cyan-400/50" />
            <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b border-l border-cyan-400/50" />
            <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-cyan-400/50" />
        </motion.div>
    );
};
