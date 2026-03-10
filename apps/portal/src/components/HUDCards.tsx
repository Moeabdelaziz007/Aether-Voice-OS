"use client";
/**
 * HUDCards — Ephemeral Telemetry + Silent Hint Cards.
 *
 * Floating glassmorphism cards showing:
 *   - Real RTT latency
 *   - Session timer
 *   - Connection mode & engine state
 *   - Vision Active indicator
 *   - Silent hints from Gemini tool calls (amber glow, 8s auto-dismiss)
 *
 * Cards auto-position in a curved arc below the orb.
 * Appear/disappear with smooth spring animations.
 */

import React, { useMemo, useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";
import { type SilentHint } from "@/store/types";

interface CardData {
    id: string;
    label: string;
    value: string;
    icon: string;
}

export default function HUDCards() {
    const latencyMs = useAetherStore((s) => s.latencyMs);
    const engineState = useAetherStore((s) => s.engineState);
    const connectionMode = useAetherStore((s) => s.connectionMode);
    const sessionStartTime = useAetherStore((s) => s.sessionStartTime);
    const status = useAetherStore((s) => s.status);
    const silentHints = useAetherStore((s) => s.silentHints);
    const visionActive = useAetherStore((s) => s.visionActive);
    const dismissHint = useAetherStore((s) => s.dismissHint);

    const [elapsed, setElapsed] = useState("00:00");

    // Session timer
    useEffect(() => {
        if (!sessionStartTime) {
            setElapsed("00:00");
            return;
        }

        const interval = setInterval(() => {
            const diff = Math.floor((Date.now() - sessionStartTime) / 1000);
            const m = String(Math.floor(diff / 60)).padStart(2, "0");
            const s = String(diff % 60).padStart(2, "0");
            setElapsed(`${m}:${s}`);
        }, 1000);

        return () => clearInterval(interval);
    }, [sessionStartTime]);

    const cards: CardData[] = useMemo(() => {
        if (status === "disconnected") return [];

        const c: CardData[] = [
            {
                id: "latency",
                label: "RTT",
                value: latencyMs > 0 ? `${latencyMs}ms` : "—",
                icon: "⚡",
            },
            {
                id: "session",
                label: "Session",
                value: elapsed,
                icon: "⏱",
            },
            {
                id: "mode",
                label: "Mode",
                value: connectionMode === "gemini" ? "Gemini Live" : "Gateway",
                icon: "🔗",
            },
            {
                id: "state",
                label: "Engine",
                value: engineState.charAt(0) + engineState.slice(1).toLowerCase(),
                icon: "🧠",
            },
        ];

        if (visionActive) {
            c.push({
                id: "vision",
                label: "Vision",
                value: "Active",
                icon: "👁",
            });
        }

        return c;
    }, [latencyMs, elapsed, connectionMode, engineState, status, visionActive]);

    // Auto-dismiss silent hints after 8 seconds
    useEffect(() => {
        if (silentHints.length === 0) return;

        const timers = silentHints.map((hint) => {
            const age = Date.now() - hint.timestamp;
            const remaining = Math.max(8000 - age, 0);
            return setTimeout(() => dismissHint(hint.id), remaining);
        });

        return () => timers.forEach(clearTimeout);
    }, [silentHints, dismissHint]);

    if (cards.length === 0 && silentHints.length === 0) return null;

    return (
        <>
            {/* Silent Hints — above HUD cards */}
            <AnimatePresence>
                {silentHints.map((hint) => (
                    <motion.div
                        key={hint.id}
                        className={`silent-hint silent-hint--${hint.priority || "info"} silent-hint--${hint.type}`}
                        initial={{ opacity: 0, y: 30, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    >
                        <span className="silent-hint__icon">
                            {hint.type === "code" ? "💡" : hint.priority === "warning" ? "⚠️" : "💬"}
                        </span>
                        <div className="silent-hint__body">
                            <span className="silent-hint__text">{hint.text}</span>
                            {hint.code && (
                                <pre className="silent-hint__code">{hint.code}</pre>
                            )}
                            {hint.explanation && (
                                <span className="silent-hint__explanation">{hint.explanation}</span>
                            )}
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>

            {/* Regular HUD Cards */}
            <div className="hud-cards">
                {cards.map((card, index) => (
                    <motion.div
                        key={card.id}
                        className="hud-card"
                        initial={{ opacity: 0, y: 20, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 25,
                            delay: index * 0.08,
                        }}
                    >
                        <span className="hud-card__icon">{card.icon}</span>
                        <div className="hud-card__content">
                            <span className="hud-card__label">{card.label}</span>
                            <span className="hud-card__value">{card.value}</span>
                        </div>
                    </motion.div>
                ))}
            </div>
        </>
    );
}
