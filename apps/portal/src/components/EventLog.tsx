"use client";

import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface LogEntry {
    id: string;
    timestamp: string;
    type: "info" | "audio" | "system" | "error";
    message: string;
}

interface EventLogProps {
    entries: LogEntry[];
}

const typeColors: Record<LogEntry["type"], string> = {
    info: "text-neon-blue",
    audio: "text-neon-purple",
    system: "text-green-500",
    error: "text-red-500",
};

const typeBadge: Record<LogEntry["type"], string> = {
    info: "INFO",
    audio: "AUDIO",
    system: "SYS",
    error: "ERR",
};

export const EventLog: React.FC<EventLogProps> = ({ entries }) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [entries]);

    return (
        <div className="w-full carbon-panel rounded-xl border border-white/[0.06] overflow-hidden">
            <div className="px-4 py-2.5 border-b border-white/[0.06] flex justify-between items-center">
                <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">System Log</span>
                <span className="text-[10px] text-gray-600">{entries.length} events</span>
            </div>
            <div ref={scrollRef} className="max-h-36 overflow-y-auto p-3 space-y-1 scrollbar-thin">
                <AnimatePresence initial={false}>
                    {entries.map((entry) => (
                        <motion.div
                            key={entry.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="flex items-start gap-3 text-[11px] font-mono leading-relaxed"
                        >
                            <span className="text-gray-700 shrink-0 tabular-nums">{entry.timestamp}</span>
                            <span className={`shrink-0 font-bold ${typeColors[entry.type]}`}>
                                [{typeBadge[entry.type]}]
                            </span>
                            <span className="text-gray-400">{entry.message}</span>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};
