"use client";
/**
 * HUDCards — Ephemeral Telemetry Cards.
 *
 * Floating glassmorphism cards showing real-time system telemetry:
 *   - Real RTT latency (not hardcoded!)
 *   - Session timer
 *   - Connection mode
 *   - Voice engine state
 *
 * Cards auto-position in a curved arc below the orb.
 * Appear/disappear with smooth spring animations.
 */

import React, { useMemo, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

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

        return [
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
    }, [latencyMs, elapsed, connectionMode, engineState, status]);

    if (cards.length === 0) return null;

    return (
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
    );
}
