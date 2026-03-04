"use client";
/**
 * AmbientTranscript — Floating Voice Captions.
 *
 * Replaces the traditional chat box with living, ambient text:
 *   - User words appear at the bottom, fade UP and away
 *   - AI words appear at the top, fade DOWN
 *   - Recent text is large + opaque, older text ghosts out
 *   - No scrollbar, no chatbox frame — pure floating typography
 */

import React, { useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

export default function AmbientTranscript() {
    const transcript = useAetherStore((s) => s.transcript);

    // Show only last 6 messages (3 user + 3 agent max)
    const recent = useMemo(
        () => transcript.slice(-6),
        [transcript]
    );

    const userMessages = recent.filter((m) => m.role === "user");
    const agentMessages = recent.filter((m) => m.role === "agent");

    return (
        <>
            {/* AI text: top area, fades down */}
            <div className="ambient-zone ambient-zone--top">
                <AnimatePresence mode="popLayout">
                    {agentMessages.slice(-3).map((msg, idx) => (
                        <motion.p
                            key={msg.id}
                            className="ambient-text ambient-text--agent"
                            initial={{ opacity: 0, y: -20, scale: 0.95 }}
                            animate={{
                                opacity: 1 - idx * 0.25,
                                y: 0,
                                scale: 1,
                            }}
                            exit={{ opacity: 0, y: 20, scale: 0.9 }}
                            transition={{
                                type: "spring",
                                stiffness: 200,
                                damping: 25,
                            }}
                        >
                            {msg.content}
                        </motion.p>
                    ))}
                </AnimatePresence>
            </div>

            {/* User text: bottom area, fades up */}
            <div className="ambient-zone ambient-zone--bottom">
                <AnimatePresence mode="popLayout">
                    {userMessages.slice(-2).map((msg, idx) => (
                        <motion.p
                            key={msg.id}
                            className="ambient-text ambient-text--user"
                            initial={{ opacity: 0, y: 20, scale: 0.95 }}
                            animate={{
                                opacity: 0.8 - idx * 0.3,
                                y: 0,
                                scale: 1,
                            }}
                            exit={{ opacity: 0, y: -20, scale: 0.9 }}
                            transition={{
                                type: "spring",
                                stiffness: 200,
                                damping: 25,
                            }}
                        >
                            {msg.content}
                        </motion.p>
                    ))}
                </AnimatePresence>
            </div>
        </>
    );
}
