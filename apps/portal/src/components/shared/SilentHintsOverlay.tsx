"use client";

/**
 * SilentHintsOverlay — Floating tool result cards.
 * Shows contextual hints from tool_result events that auto-dismiss.
 * Glassmorphism cards slide in from right, stack vertically.
 */

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

interface HintCard {
    id: string;
    toolName: string;
    summary: string;
    status: "success" | "error" | "running";
    timestamp: number;
}

const STATUS_STYLES = {
    success: {
        dot: "bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)]",
        border: "border-emerald-400/10",
        label: "text-emerald-400/60",
    },
    error: {
        dot: "bg-red-400 shadow-[0_0_8px_rgba(239,68,68,0.5)]",
        border: "border-red-400/10",
        label: "text-red-400/60",
    },
    running: {
        dot: "bg-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.5)] animate-pulse",
        border: "border-amber-400/10",
        label: "text-amber-400/60",
    },
};

const AUTO_DISMISS_MS = 8000;
const MAX_VISIBLE = 4;

export default function SilentHintsOverlay() {
    const silentHints = useAetherStore((s) => s.silentHints);
    const [cards, setCards] = useState<HintCard[]>([]);

    // Convert store hints to display cards
    useEffect(() => {
        if (silentHints.length === 0) return;
        const latest = silentHints[silentHints.length - 1];
        if (!latest) return;

        const newCard: HintCard = {
            id: `hint-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            toolName: latest.text || "System",
            summary: latest.explanation || "Action completed.",
            status: "success",
            timestamp: Date.now(),
        };

        setCards((prev) => [...prev.slice(-(MAX_VISIBLE - 1)), newCard]);
    }, [silentHints.length]); // eslint-disable-line react-hooks/exhaustive-deps

    // Auto-dismiss timer
    useEffect(() => {
        if (cards.length === 0) return;
        const timer = setInterval(() => {
            const now = Date.now();
            setCards((prev) => prev.filter((c) => now - c.timestamp < AUTO_DISMISS_MS));
        }, 1000);
        return () => clearInterval(timer);
    }, [cards.length]);

    const dismiss = useCallback((id: string) => {
        setCards((prev) => prev.filter((c) => c.id !== id));
    }, []);

    return (
        <div className="fixed top-4 right-4 z-40 flex flex-col gap-2 w-80 pointer-events-none">
            <AnimatePresence mode="popLayout">
                {cards.map((card) => {
                    const styles = STATUS_STYLES[card.status];
                    return (
                        <motion.div
                            key={card.id}
                            layout
                            initial={{ opacity: 0, x: 80, scale: 0.9 }}
                            animate={{ opacity: 1, x: 0, scale: 1 }}
                            exit={{ opacity: 0, x: 80, scale: 0.9 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className={`
                                pointer-events-auto
                                bg-[rgba(10,10,18,0.85)] backdrop-blur-2xl
                                border ${styles.border} rounded-2xl
                                p-4 cursor-pointer
                                hover:bg-[rgba(20,20,30,0.9)]
                                transition-colors duration-200
                                shadow-[0_8px_32px_rgba(0,0,0,0.4)]
                            `}
                            onClick={() => dismiss(card.id)}
                        >
                            {/* Header */}
                            <div className="flex items-center gap-2 mb-1.5">
                                <div className={`w-1.5 h-1.5 rounded-full ${styles.dot}`} />
                                <span className={`font-mono text-[10px] uppercase tracking-[0.12em] ${styles.label}`}>
                                    {card.toolName}
                                </span>
                                {/* Progress ring for auto-dismiss */}
                                <div className="ml-auto relative w-3 h-3">
                                    <svg className="w-3 h-3 -rotate-90" viewBox="0 0 12 12">
                                        <circle
                                            cx="6" cy="6" r="5"
                                            fill="none"
                                            stroke="rgba(255,255,255,0.06)"
                                            strokeWidth="1"
                                        />
                                        <motion.circle
                                            cx="6" cy="6" r="5"
                                            fill="none"
                                            stroke="rgba(255,255,255,0.2)"
                                            strokeWidth="1"
                                            strokeDasharray={2 * Math.PI * 5}
                                            initial={{ strokeDashoffset: 0 }}
                                            animate={{ strokeDashoffset: 2 * Math.PI * 5 }}
                                            transition={{ duration: AUTO_DISMISS_MS / 1000, ease: "linear" }}
                                        />
                                    </svg>
                                </div>
                            </div>

                            {/* Body */}
                            <p className="text-white/60 text-xs leading-relaxed line-clamp-2">
                                {card.summary}
                            </p>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}
