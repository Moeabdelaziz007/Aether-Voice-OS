"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTelemetry } from "@/hooks/useTelemetry";

/**
 * TelemetryFeed — The Industrial Matrix Stream.
 * 
 * Displays a scrolling list of system operations in a monospace font.
 * Logs fade as they get older/higher in the list.
 */
export default function TelemetryFeed() {
    const { logs } = useTelemetry();

    return (
        <div className="telemetry-feed fixed left-6 top-24 w-64 h-auto max-h-[40vh] pointer-events-none z-20 flex flex-col-reverse gap-1 overflow-hidden">
            <AnimatePresence initial={false}>
                {logs.map((log, index) => (
                    <motion.div
                        key={log.id}
                        initial={{ opacity: 0, x: -20, filter: "blur(4px)" }}
                        animate={{
                            opacity: Math.max(0.1, 1 - index * 0.15),
                            x: 0,
                            filter: "blur(0px)"
                        }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                        className="flex items-start gap-2 py-0.5"
                    >
                        <span className="font-mono text-[10px] text-white/20 select-none pt-0.5">
                            [{log.timestamp}]
                        </span>
                        <div className="flex flex-col">
                            {log.source && (
                                <span className="font-mono text-[9px] uppercase tracking-wider text-neon-cyan/40 leading-none mb-0.5">
                                    {log.source}
                                </span>
                            )}
                            <span className={`font-mono text-[11px] leading-tight ${log.type === "error" ? "text-red-400" :
                                    log.type === "success" ? "text-green-400" :
                                        log.type === "action" ? "text-amber-400" :
                                            "text-white/60"
                                }`}>
                                {log.message}
                            </span>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>

            {/* Visual scanline/gradient to fade out top logs */}
            <div className="absolute inset-0 bg-gradient-to-t from-transparent via-transparent to-void z-10 pointer-events-none h-full" />
        </div>
    );
}
